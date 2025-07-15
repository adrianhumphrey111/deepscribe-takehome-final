from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from
from config import Config
from services.patient_extractor import PatientDataExtractor
from services.trials_client import ClinicalTrialsClient
from services.ranking_engine import TrialRankingEngine
from services.trial_qa_service import TrialQAService
from models.patient_data import PatientData
import time
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://clinical-trials-matcher.vercel.app"])

# Initialize Swagger
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
        "title": "Clinical Trials Matcher API",
        "description": "AI-powered clinical trial matching system for healthcare providers",
        "version": "1.0.0",
        "contact": {
            "name": "DeepScribe",
            "url": "https://deepscribe.ai"
        }
    },
    "host": "localhost:5328",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {
            "name": "Health",
            "description": "System health and status endpoints"
        },
        {
            "name": "Patient Data",
            "description": "Patient data extraction from medical transcripts"
        },
        {
            "name": "Clinical Trials",
            "description": "Clinical trial search and matching"
        },
        {
            "name": "Q&A",
            "description": "Trial-specific question answering"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Load configuration
config = Config()

# Initialize services
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

try:
    qa_service = TrialQAService(config)
    logger.info("Q&A service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Q&A service: {e}")
    qa_service = None

@app.route("/api/health", methods=["GET"])
@swag_from('docs/swagger/health.yml')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "config": {
            "has_openai_key": bool(config.OPENAI_API_KEY),
            "has_anthropic_key": bool(config.ANTHROPIC_API_KEY),
            "claude_enabled": config.ENABLE_CLAUDE_PROVIDER,
            "openai_enabled": config.ENABLE_OPENAI_PROVIDER,
            "qa_enabled": config.ENABLE_QA_SYSTEM
        }
    })

@app.route("/api/extract", methods=["POST"])
@swag_from('docs/swagger/extract.yml')
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
        
        # Check if patient extractor is available
        if not patient_extractor:
            return jsonify({
                "success": False,
                "error_message": "Patient extraction service is not available. Please check your API keys."
            }), 503
        
        # Run async extraction in sync context
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
        
        # Convert result to JSON response
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
@swag_from('docs/swagger/search_trials.yml')
def search_trials():
    """Search for clinical trials"""
    # Add headers to keep connection alive during long processing
    response_headers = {
        'Connection': 'keep-alive',
        'Keep-Alive': 'timeout=600, max=1000',  # 10 minute keep-alive
        'Cache-Control': 'no-cache',
        'X-Content-Type-Options': 'nosniff'
    }
    try:
        data = request.get_json()
        
        if not data or 'patient_data' not in data:
            return jsonify({
                "success": False,
                "error_message": "Patient data is required"
            }), 400
        
        patient_data_dict = data['patient_data']
        max_results = data.get('max_results', 25)
        
        # Check if required services are available
        if not trials_client or not ranking_engine:
            return jsonify({
                "success": False,
                "error_message": "Trial search services are not available"
            }), 503
        
        # Convert dict to PatientData object
        try:
            patient_data = PatientData(**patient_data_dict)
        except Exception as e:
            return jsonify({
                "success": False,
                "error_message": f"Invalid patient data: {str(e)}"
            }), 400
        
        # Search for trials with extended timeout and progress logging
        start_time = time.time()
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            logger.info(f"Starting trial search for {max_results} trials...")
            
            # Extended timeout for comprehensive LLM analysis
            trials = loop.run_until_complete(
                asyncio.wait_for(
                    trials_client.search_trials(patient_data, max_results),
                    timeout=300.0  # 5 minute timeout for thorough analysis
                )
            )
            loop.close()
            
            search_duration = int((time.time() - start_time) * 1000)
            logger.info(f"Trial search completed successfully in {search_duration}ms, found {len(trials)} trials")
            
        except asyncio.TimeoutError:
            logger.error("Trial search timed out after 5 minutes")
            return jsonify({
                "success": False,
                "error_message": "The comprehensive trial analysis is taking longer than expected. This usually happens with complex medical profiles. Please try again."
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
        
        response = jsonify({
            "success": True,
            "trials": trials_data,
            "total_found": len(trials_data),
            "search_metadata": {
                "query_used": patient_data.primary_diagnosis or "general",
                "search_time_ms": search_time,
                "patient_location": patient_data.location.dict() if patient_data.location else None
            }
        })
        
        # Add keep-alive headers
        for header, value in response_headers.items():
            response.headers[header] = value
            
        return response
        
    except Exception as e:
        logger.error(f"Error in search_trials: {str(e)}")
        return jsonify({
            "success": False,
            "error_message": str(e)
        }), 500

@app.route("/api/trials/<trial_id>", methods=["GET"])
@swag_from('docs/swagger/trial_details.yml')
def get_trial_details(trial_id):
    """Get detailed information about a specific trial"""
    try:
        # TODO: Implement trial details logic
        # For now, return a placeholder response
        return jsonify({
            "success": True,
            "trial": {
                "nct_id": trial_id,
                "title": "Phase III Trial of New Breast Cancer Treatment",
                "detailed_description": "This is a randomized, double-blind, placebo-controlled trial...",
                "status": "RECRUITING",
                "phase": "PHASE_3",
                "primary_outcome": "Overall survival at 5 years",
                "secondary_outcomes": ["Progression-free survival", "Quality of life scores"],
                "enrollment_target": 500,
                "estimated_completion": "2025-12-31",
                "sponsor": "Research University"
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_trial_details: {str(e)}")
        return jsonify({
            "success": False,
            "error_message": str(e)
        }), 500

@app.route("/api/trials/qa", methods=["POST"])
@swag_from('docs/swagger/trial_qa.yml')
def trial_qa():
    """Answer questions about clinical trials"""
    try:
        data = request.get_json()
        
        if not data or 'trial_id' not in data or 'question' not in data:
            return jsonify({
                "success": False,
                "error_message": "Trial ID and question are required"
            }), 400
        
        trial_id = data['trial_id']
        question = data['question']
        patient_context = data.get('patient_context')
        
        # Check if Q&A service is available
        if not qa_service:
            return jsonify({
                "success": False,
                "error_message": "Q&A service is not available. Please check your API keys."
            }), 503
        
        # Run async Q&A in sync context
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                qa_service.answer_question(trial_id, question, patient_context)
            )
            loop.close()
        except Exception as e:
            logger.error(f"Error during Q&A processing: {str(e)}")
            return jsonify({
                "success": False,
                "error_message": f"Q&A processing failed: {str(e)}"
            }), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in trial_qa: {str(e)}")
        return jsonify({
            "success": False,
            "error_message": str(e)
        }), 500

# Keep the original endpoint for backward compatibility
@app.route("/api/python")
def hello_world():
    return {"message": "Hello from Python!"}