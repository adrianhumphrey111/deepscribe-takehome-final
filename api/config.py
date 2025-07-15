import os
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv('.env.local')

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Environment
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # External APIs
    CLINICAL_TRIALS_API_URL = os.getenv('CLINICAL_TRIALS_API_URL', 'https://clinicaltrials.gov/api/v2')
    
    # Feature Flags
    ENABLE_CLAUDE_PROVIDER = os.getenv('ENABLE_CLAUDE_PROVIDER', 'true').lower() == 'true'
    ENABLE_OPENAI_PROVIDER = os.getenv('ENABLE_OPENAI_PROVIDER', 'true').lower() == 'true'
    ENABLE_QA_SYSTEM = os.getenv('ENABLE_QA_SYSTEM', 'true').lower() == 'true'
    
    # Performance
    MAX_EXTRACTION_RETRIES = int(os.getenv('MAX_EXTRACTION_RETRIES', '3'))
    REQUEST_TIMEOUT_MS = int(os.getenv('REQUEST_TIMEOUT_MS', '30000'))
    
    @property
    def has_required_keys(self):
        return self.OPENAI_API_KEY and self.ANTHROPIC_API_KEY