import re
import logging
from typing import Dict, List
from config import Config
from services.llm_provider import LLMProvider, OpenAIProvider, ClaudeProvider

logger = logging.getLogger(__name__)

class SmartLLMRouter:
    """Intelligent LLM provider selection based on transcript characteristics"""
    
    def __init__(self, config: Config):
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        
        # Initialize available providers
        if config.ENABLE_OPENAI_PROVIDER and config.OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAIProvider(config)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")
        
        if config.ENABLE_CLAUDE_PROVIDER and config.ANTHROPIC_API_KEY:
            try:
                self.providers["claude"] = ClaudeProvider(config)
            except Exception as e:
                logger.warning(f"Failed to initialize Claude provider: {e}")
        
        if not self.providers:
            raise ValueError("No LLM providers available. Please check your API keys and configuration.")
    
    def select_provider(self, transcript: str) -> LLMProvider:
        """Select the best LLM provider based on transcript characteristics"""
        
        # If only one provider is available, use it
        if len(self.providers) == 1:
            return list(self.providers.values())[0]
        
        # Calculate transcript characteristics
        word_count = len(transcript.split())
        token_estimate = word_count * 1.3  # Rough token estimation
        complexity_score = self._calculate_medical_complexity(transcript)
        
        logger.info(f"Transcript analysis: {word_count} words, {token_estimate:.0f} tokens, complexity: {complexity_score:.2f}")
        
        # Decision logic for provider selection
        
        # Route to Claude for long transcripts (better context handling)
        if word_count > 2000 or token_estimate > 8000:
            if "claude" in self.providers:
                logger.info("Selected Claude for long transcript")
                return self.providers["claude"]
        
        # Route to Claude for high medical complexity
        if complexity_score > 0.7:
            if "claude" in self.providers:
                logger.info("Selected Claude for high medical complexity")
                return self.providers["claude"]
        
        # Default to OpenAI for efficiency and cost
        if "openai" in self.providers:
            logger.info("Selected OpenAI for standard processing")
            return self.providers["openai"]
        
        # Fallback to any available provider
        provider_name = list(self.providers.keys())[0]
        logger.info(f"Fallback to {provider_name}")
        return self.providers[provider_name]
    
    def get_alternate_provider(self, current_provider: LLMProvider) -> LLMProvider:
        """Get an alternate provider for fallback scenarios"""
        current_name = current_provider.provider_name
        
        # Return the other available provider
        for name, provider in self.providers.items():
            if name != current_name:
                return provider
        
        # If no alternate provider, return the same one
        return current_provider
    
    def _calculate_medical_complexity(self, transcript: str) -> float:
        """Calculate medical complexity score based on transcript content"""
        
        complexity_indicators = {
            # Rare conditions and complex diagnoses
            'rare_conditions': [
                'adenocarcinoma', 'lymphoma', 'sarcoma', 'metastatic', 'malignant',
                'syndrome', 'dystrophy', 'neurological', 'autoimmune', 'congenital'
            ],
            
            # Complex medical terminology
            'complex_terms': [
                'pathophysiology', 'pharmacokinetics', 'immunotherapy', 'chemotherapy',
                'radiation', 'biomarker', 'genetic', 'mutation', 'prognosis'
            ],
            
            # Multiple systems involvement
            'multi_system': [
                'cardiovascular', 'pulmonary', 'hepatic', 'renal', 'neurological',
                'gastrointestinal', 'endocrine', 'hematologic', 'dermatologic'
            ],
            
            # Complex procedures
            'procedures': [
                'surgical', 'resection', 'biopsy', 'catheterization', 'transplant',
                'dialysis', 'endoscopy', 'angiography', 'laparoscopy'
            ]
        }
        
        text_lower = transcript.lower()
        total_score = 0.0
        total_weight = 0.0
        
        for category, terms in complexity_indicators.items():
            category_score = 0.0
            for term in terms:
                if term in text_lower:
                    category_score += 1.0
            
            # Normalize by category size and apply weights
            category_weight = {
                'rare_conditions': 0.3,
                'complex_terms': 0.3,
                'multi_system': 0.2,
                'procedures': 0.2
            }.get(category, 0.25)
            
            normalized_score = min(category_score / len(terms), 1.0)
            total_score += normalized_score * category_weight
            total_weight += category_weight
        
        # Additional complexity factors
        
        # Multiple medications (indicates complex case)
        medications = self._count_medications(transcript)
        medication_complexity = min(medications / 5.0, 1.0) * 0.1
        
        # Specialist involvement (indicates complexity)
        specialist_count = self._count_specialists(transcript)
        specialist_complexity = min(specialist_count / 3.0, 1.0) * 0.1
        
        # Combine all factors
        final_score = total_score + medication_complexity + specialist_complexity
        
        return min(final_score, 1.0)
    
    def _count_medications(self, transcript: str) -> int:
        """Count number of medications mentioned"""
        # Common medication patterns
        medication_patterns = [
            r'\b\w+cin\b',  # -cin endings (antibiotics)
            r'\b\w+pril\b',  # -pril endings (ACE inhibitors)
            r'\b\w+statin\b',  # -statin endings (cholesterol)
            r'\b\w+zole\b',  # -zole endings (proton pump inhibitors)
            r'\b\w+lol\b',  # -lol endings (beta blockers)
            r'\b\w+pine\b',  # -pine endings (calcium channel blockers)
        ]
        
        # Known medication names
        known_meds = [
            'aspirin', 'tylenol', 'ibuprofen', 'acetaminophen', 'prednisone',
            'metformin', 'insulin', 'lisinopril', 'amlodipine', 'atorvastatin',
            'omeprazole', 'levothyroxine', 'warfarin', 'hydrochlorothiazide'
        ]
        
        text_lower = transcript.lower()
        medication_count = 0
        
        # Count pattern matches
        for pattern in medication_patterns:
            matches = re.findall(pattern, text_lower)
            medication_count += len(matches)
        
        # Count known medications
        for med in known_meds:
            if med in text_lower:
                medication_count += 1
        
        return medication_count
    
    def _count_specialists(self, transcript: str) -> int:
        """Count number of medical specialists mentioned"""
        specialists = [
            'cardiologist', 'oncologist', 'neurologist', 'pulmonologist',
            'gastroenterologist', 'endocrinologist', 'rheumatologist',
            'hematologist', 'urologist', 'ophthalmologist', 'dermatologist',
            'psychiatrist', 'surgeon', 'radiologist', 'pathologist'
        ]
        
        text_lower = transcript.lower()
        specialist_count = 0
        
        for specialist in specialists:
            if specialist in text_lower:
                specialist_count += 1
        
        return specialist_count
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())
    
    def get_provider_by_name(self, name: str) -> LLMProvider:
        """Get provider by name"""
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not available. Available providers: {self.get_available_providers()}")
        return self.providers[name]