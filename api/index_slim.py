import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
from config import Config
from services.patient_extractor import PatientDataExtractor
from services.trials_client import ClinicalTrialsClient
from services.ranking_engine import TrialRankingEngine
# Skip QA service - it uses heavy LangChain dependencies
from models.patient_data import PatientData
import time
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Allow CORS for development and production
allowed_origins = [
    "http://localhost:3000",
    "https://clinical-trials-matcher.vercel.app"
]

# Add production URLs if available
if os.getenv('RENDER_EXTERNAL_URL'):
    allowed_origins.append(os.getenv('RENDER_EXTERNAL_URL'))

# For App Runner deployment, allow all origins in production
if os.getenv('FLASK_ENV') == 'production':
    CORS(app, origins="*")
else:
    CORS(app, origins=allowed_origins)

# Initialize Swagger (simplified)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Clinical Trials Matcher API (Slim)",
        "description": "Lightweight AI-powered clinical trial matching system",
        "version": "1.0.0-slim",
    },
    "host": "localhost:5328",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Load configuration
config = Config()

# Initialize services (skip heavy LangChain ones)
try:
    patient_extractor = PatientDataExtractor(config)
    logger.info("Patient extractor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize patient extractor: {e}")
    patient_extractor = None

try:
    trials_client = ClinicalTrialsClient(config)
    logger.info("Trials client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize trials client: {e}")
    trials_client = None

try:
    ranking_engine = TrialRankingEngine()
    logger.info("Ranking engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ranking engine: {e}")
    ranking_engine = None

# Skip QA service initialization - too heavy
qa_service = None
logger.info("QA service disabled in slim build")

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0-slim",
        "config": {
            "has_openai_key": bool(config.OPENAI_API_KEY),
            "has_anthropic_key": bool(config.ANTHROPIC_API_KEY),
            "claude_enabled": config.ENABLE_CLAUDE_PROVIDER,
            "openai_enabled": config.ENABLE_OPENAI_PROVIDER,
            "qa_enabled": False  # Disabled in slim build
        }
    })

@app.route("/api/extract", methods=["POST"])
def extract_patient_data():
    """Extract patient data from transcript"""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({
                "success": False,
                "error_message": "Transcript is required"
            }), 400
        
        transcript = data['transcript']
        
        if not patient_extractor:
            return jsonify({
                "success": False,
                "error_message": "Patient extraction service is not available. Please check your API keys."
            }), 503
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(patient_extractor.extract_patient_data(transcript))
            loop.close()
        except Exception as e:
            logger.error(f"Error during async extraction: {str(e)}")
            return jsonify({
                "success": False,
                "error_message": f"Extraction failed: {str(e)}"
            }), 500
        
        return jsonify({
            "success": result.success,
            "patient_data": result.patient_data.dict() if result.patient_data else {},
            "confidence_scores": result.confidence_scores.dict() if result.confidence_scores else {},
            "provider_used": result.provider_used,
            "extraction_time_ms": result.extraction_time_ms,
            "error_message": result.error_message
        })
        
    except Exception as e:
        logger.error(f"Error in extract_patient_data: {str(e)}")
        return jsonify({
            "success": False,
            "error_message": str(e)
        }), 500

@app.route("/api/trials/search", methods=["POST"])
def search_trials():
    """Search for clinical trials (simplified without heavy RAG)"""
    try:
        data = request.get_json()
        
        if not data or 'patient_data' not in data:
            return jsonify({
                "success": False,
                "error_message": "Patient data is required"
            }), 400
        
        patient_data_dict = data['patient_data']
        max_results = data.get('max_results', 25)
        
        if not trials_client or not ranking_engine:
            return jsonify({
                "success": False,
                "error_message": "Trial search services are not available"
            }), 503
        
        try:
            patient_data = PatientData(**patient_data_dict)
        except Exception as e:
            return jsonify({
                "success": False,
                "error_message": f"Invalid patient data: {str(e)}"
            }), 400
        
        start_time = time.time()
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            logger.info(f"Starting simplified trial search for {max_results} trials...")
            
            trials = loop.run_until_complete(
                asyncio.wait_for(
                    trials_client.search_trials(patient_data, max_results),
                    timeout=120.0  # Reduced timeout for slim build
                )
            )
            loop.close()
            
            search_duration = int((time.time() - start_time) * 1000)
            logger.info(f"Trial search completed in {search_duration}ms, found {len(trials)} trials")
            
        except asyncio.TimeoutError:
            logger.error("Trial search timed out")
            return jsonify({
                "success": False,
                "error_message": "Trial search timed out. Please try with fewer results or a simpler query."
            }), 504
        except Exception as e:
            logger.error(f"Error during trial search: {str(e)}")
            return jsonify({
                "success": False,
                "error_message": f"Trial search failed: {str(e)}"
            }), 500
        
        # Rank trials
        ranked_trials = ranking_engine.rank_trials(trials, patient_data)
        
        search_time = int((time.time() - start_time) * 1000)
        
        # Convert to JSON response
        trials_data = []
        for ranked_trial in ranked_trials:
            trial_dict = ranked_trial.trial.dict()
            trials_data.append({
                "trial": trial_dict,
                "match_score": ranked_trial.match_score,
                "match_factors": ranked_trial.match_factors,
                "reasoning": ranked_trial.reasoning
            })
        
        return jsonify({
            "success": True,
            "trials": trials_data,
            "total_found": len(trials_data),
            "search_metadata": {
                "query_used": patient_data.primary_diagnosis or "general",
                "search_time_ms": search_time,
                "patient_location": patient_data.location.dict() if patient_data.location else None,
                "build_type": "slim"
            }
        })
        
    except Exception as e:
        logger.error(f"Error in search_trials: {str(e)}")
        return jsonify({
            "success": False,
            "error_message": str(e)
        }), 500

@app.route("/api/trials/qa", methods=["POST"])
def trial_qa():
    """QA endpoint - disabled in slim build"""
    return jsonify({
        "success": False,
        "error_message": "Q&A service is disabled in slim build to reduce dependencies. Please use the full build for Q&A features."
    }), 503

@app.route("/api/python")
def hello_world():
    return {"message": "Hello from Python! (Slim Build)"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)