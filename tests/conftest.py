import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from api.index import app
from api.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    config = Mock(spec=Config)
    config.OPENAI_API_KEY = "test_openai_key"
    config.ANTHROPIC_API_KEY = "test_anthropic_key"
    config.FLASK_ENV = "testing"
    config.DEBUG = False
    config.CLINICAL_TRIALS_API_URL = "https://test-clinicaltrials.gov/api/v2"
    config.ENABLE_CLAUDE_PROVIDER = True
    config.ENABLE_OPENAI_PROVIDER = True
    config.ENABLE_QA_SYSTEM = True
    config.MAX_EXTRACTION_RETRIES = 3
    config.REQUEST_TIMEOUT_MS = 30000
    config.has_required_keys = True
    return config


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client"""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client"""
    with patch('anthropic.Anthropic') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield {'get': mock_get, 'post': mock_post}


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing"""
    return {
        "basic_info": {
            "age": 45,
            "gender": "female",
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "country": "US"
            }
        },
        "medical_history": {
            "diagnoses": ["Type 2 Diabetes", "Hypertension"],
            "medications": ["Metformin", "Lisinopril"],
            "allergies": ["Penicillin"]
        },
        "current_condition": {
            "primary_diagnosis": "Type 2 Diabetes",
            "symptoms": ["Excessive thirst", "Frequent urination"],
            "severity": "moderate"
        }
    }


@pytest.fixture
def sample_trial_data():
    """Sample trial data for testing"""
    return {
        "NCTId": "NCT12345678",
        "BriefTitle": "Study of New Diabetes Treatment",
        "OverallStatus": "Recruiting",
        "Phase": "Phase 2",
        "StudyType": "Interventional",
        "Condition": ["Type 2 Diabetes"],
        "InterventionName": ["Experimental Drug A"],
        "EligibilityCriteria": {
            "MinimumAge": "18 Years",
            "MaximumAge": "75 Years",
            "Gender": "All",
            "Criteria": "Inclusion: Type 2 diabetes diagnosis, HbA1c > 7%"
        },
        "LocationFacility": [{
            "LocationFacilityName": "Research Hospital",
            "LocationFacilityCity": "San Francisco",
            "LocationFacilityState": "CA",
            "LocationFacilityCountry": "US"
        }]
    }


@pytest.fixture
def sample_transcript():
    """Sample medical transcript for testing"""
    return """
    Patient is a 45-year-old female presenting with complaints of excessive thirst and frequent urination. 
    She has a history of Type 2 diabetes and hypertension. Current medications include Metformin and Lisinopril. 
    She reports an allergy to Penicillin. She lives in San Francisco, CA. 
    Her current blood sugar levels are elevated and she appears to have moderate symptoms.
    """


@pytest.fixture
def sample_openai_response():
    """Sample OpenAI API response"""
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message = Mock()
    response.choices[0].message.content = '{"age": 45, "gender": "female", "diagnosis": "Type 2 Diabetes"}'
    response.usage = Mock()
    response.usage.total_tokens = 150
    return response


@pytest.fixture
def sample_anthropic_response():
    """Sample Anthropic API response"""
    response = Mock()
    response.content = [Mock()]
    response.content[0].text = '{"age": 45, "gender": "female", "diagnosis": "Type 2 Diabetes"}'
    response.usage = Mock()
    response.usage.input_tokens = 100
    response.usage.output_tokens = 50
    return response


@pytest.fixture
def sample_trials_api_response():
    """Sample ClinicalTrials.gov API response"""
    return {
        "studies": [
            {
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT12345678",
                        "briefTitle": "Study of New Diabetes Treatment"
                    },
                    "statusModule": {
                        "overallStatus": "RECRUITING"
                    },
                    "designModule": {
                        "phases": ["PHASE2"],
                        "studyType": "INTERVENTIONAL"
                    },
                    "conditionsModule": {
                        "conditions": ["Type 2 Diabetes"]
                    },
                    "armsInterventionsModule": {
                        "interventions": [{
                            "name": "Experimental Drug A",
                            "type": "DRUG"
                        }]
                    },
                    "eligibilityModule": {
                        "minimumAge": "18 Years",
                        "maximumAge": "75 Years",
                        "sex": "ALL",
                        "eligibilityCriteria": "Inclusion: Type 2 diabetes diagnosis, HbA1c > 7%"
                    },
                    "contactsLocationsModule": {
                        "locations": [{
                            "facility": "Research Hospital",
                            "city": "San Francisco",
                            "state": "CA",
                            "country": "United States"
                        }]
                    }
                }
            }
        ]
    }