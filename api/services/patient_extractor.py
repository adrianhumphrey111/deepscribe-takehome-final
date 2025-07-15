import asyncio
import logging
from typing import Optional
from config import Config
from models.patient_data import ExtractionResult, PatientData, ConfidenceScores
from services.llm_router import SmartLLMRouter
from services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class PatientDataExtractor:
    """Service for extracting patient data from medical transcripts"""
    
    def __init__(self, config: Config):
        self.config = config
        self.router = SmartLLMRouter(config)
    
    async def extract_patient_data(self, transcript: str) -> ExtractionResult:
        """Extract patient data with automatic fallback"""
        
        # Input validation
        if not transcript or not transcript.strip():
            return ExtractionResult(
                patient_data=PatientData(),
                confidence_scores=ConfidenceScores(),
                provider_used="none",
                extraction_time_ms=0,
                success=False,
                error_message="Empty transcript provided"
            )
        
        # Sanitize transcript (remove potential PHI)
        sanitized_transcript = self._sanitize_transcript(transcript)
        
        # Select primary provider
        primary_provider = self.router.select_provider(sanitized_transcript)
        
        # Attempt extraction with primary provider
        result = await self._extract_with_fallback(sanitized_transcript, primary_provider)
        
        # Post-process the result
        if result.success:
            result = self._post_process_extraction(result, transcript)
        
        return result
    
    async def _extract_with_fallback(self, transcript: str, primary_provider: LLMProvider) -> ExtractionResult:
        """Extract data with automatic fallback to alternate provider"""
        
        # Try primary provider
        try:
            logger.info(f"Attempting extraction with {primary_provider.provider_name}")
            result = await primary_provider.extract_patient_data(transcript)
            
            if result.success and self._is_valid_extraction(result):
                logger.info(f"Successful extraction with {primary_provider.provider_name}")
                return result
            else:
                logger.warning(f"Primary provider {primary_provider.provider_name} returned invalid result")
                
        except Exception as e:
            logger.error(f"Primary provider {primary_provider.provider_name} failed: {str(e)}")
        
        # Try alternate provider
        try:
            alternate_provider = self.router.get_alternate_provider(primary_provider)
            if alternate_provider.provider_name != primary_provider.provider_name:
                logger.info(f"Attempting extraction with alternate provider {alternate_provider.provider_name}")
                result = await alternate_provider.extract_patient_data(transcript)
                
                if result.success and self._is_valid_extraction(result):
                    logger.info(f"Successful extraction with alternate provider {alternate_provider.provider_name}")
                    return result
                else:
                    logger.warning(f"Alternate provider {alternate_provider.provider_name} returned invalid result")
                    
        except Exception as e:
            logger.error(f"Alternate provider failed: {str(e)}")
        
        # Both providers failed - return manual entry template
        return self._create_manual_entry_template(transcript)
    
    def _sanitize_transcript(self, transcript: str) -> str:
        """Remove potential PHI from transcript"""
        import re
        
        # PHI patterns to remove/mask
        phi_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone numbers
            r'\b\d{5}(?:-\d{4})?\b',  # ZIP codes (basic pattern)
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email addresses
        ]
        
        sanitized = transcript
        for pattern in phi_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized
    
    def _is_valid_extraction(self, result: ExtractionResult) -> bool:
        """Validate extraction result quality"""
        if not result.success:
            return False
        
        data = result.patient_data
        scores = result.confidence_scores
        
        # Check if we have at least some meaningful data
        has_basic_info = (
            data.age is not None or 
            data.gender is not None or 
            data.primary_diagnosis is not None or
            len(data.conditions) > 0
        )
        
        # Check confidence scores are reasonable
        has_reasonable_confidence = scores.overall >= 0.3
        
        return has_basic_info and has_reasonable_confidence
    
    def _post_process_extraction(self, result: ExtractionResult, original_transcript: str) -> ExtractionResult:
        """Post-process extraction result for quality improvements"""
        
        # Enhance location data if missing
        if result.patient_data.location is None:
            enhanced_location = self._enhance_location_data(original_transcript)
            if enhanced_location:
                result.patient_data.location = enhanced_location
        
        # Deduplicate conditions and medications
        result.patient_data.conditions = list(set(result.patient_data.conditions))
        result.patient_data.medications = list(set(result.patient_data.medications))
        result.patient_data.comorbidities = list(set(result.patient_data.comorbidities))
        
        # Infer missing age if possible
        if result.patient_data.age is None:
            inferred_age = self._infer_age_from_context(original_transcript, result.patient_data)
            if inferred_age:
                result.patient_data.age = inferred_age
                result.confidence_scores.age = 0.6  # Lower confidence for inferred data
        
        return result
    
    def _enhance_location_data(self, transcript: str) -> Optional[dict]:
        """Extract location information from transcript"""
        import re
        
        # Common location patterns
        location_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, State
            r'\b([A-Z][a-z]+)\s+([A-Z]{2})\b',  # City State
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+area\b',  # Area references
        ]
        
        # Common cities for context
        major_cities = [
            'San Francisco', 'Los Angeles', 'New York', 'Chicago', 'Houston',
            'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas',
            'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus',
            'Charlotte', 'Seattle', 'Denver', 'Boston', 'Detroit'
        ]
        
        text = transcript
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if len(match) == 2:  # City, State format
                        city, state = match
                        if city in major_cities or len(city) > 3:
                            return {
                                'city': city,
                                'state': state
                            }
        
        return None
    
    def _infer_age_from_context(self, transcript: str, patient_data: PatientData) -> Optional[int]:
        """Infer age from medical context"""
        
        # Age inference rules based on common medical conditions
        age_indicators = {
            'pediatric': (5, 17),
            'adolescent': (13, 19),
            'young adult': (20, 35),
            'middle-aged': (40, 65),
            'elderly': (65, 85),
            'geriatric': (70, 90)
        }
        
        # Condition-based age inference
        condition_age_hints = {
            'type 1 diabetes': (15, 30),
            'type 2 diabetes': (40, 70),
            'hypertension': (35, 75),
            'arthritis': (50, 80),
            'alzheimer': (65, 85),
            'prostate': (50, 80),
            'menopause': (45, 60),
            'osteoporosis': (50, 80),
            'breast cancer': (35, 75),
            'colon cancer': (45, 75)
        }
        
        text_lower = transcript.lower()
        
        # Check for explicit age indicators
        for indicator, (min_age, max_age) in age_indicators.items():
            if indicator in text_lower:
                return (min_age + max_age) // 2
        
        # Check for condition-based age hints
        if patient_data.primary_diagnosis:
            diagnosis_lower = patient_data.primary_diagnosis.lower()
            for condition, (min_age, max_age) in condition_age_hints.items():
                if condition in diagnosis_lower:
                    return (min_age + max_age) // 2
        
        # Check conditions list
        for condition in patient_data.conditions:
            condition_lower = condition.lower()
            for hint_condition, (min_age, max_age) in condition_age_hints.items():
                if hint_condition in condition_lower:
                    return (min_age + max_age) // 2
        
        return None
    
    def _create_manual_entry_template(self, transcript: str) -> ExtractionResult:
        """Create a manual entry template when automatic extraction fails"""
        
        # Try to extract some basic information for pre-filling
        basic_info = self._extract_basic_info(transcript)
        
        return ExtractionResult(
            patient_data=PatientData(
                age=basic_info.get('age'),
                gender=basic_info.get('gender'),
                conditions=basic_info.get('conditions', []),
                primary_diagnosis=basic_info.get('primary_diagnosis'),
                medications=basic_info.get('medications', []),
                location=basic_info.get('location')
            ),
            confidence_scores=ConfidenceScores(
                age=0.3 if basic_info.get('age') else 0.0,
                gender=0.3 if basic_info.get('gender') else 0.0,
                primary_diagnosis=0.3 if basic_info.get('primary_diagnosis') else 0.0,
                conditions=0.3 if basic_info.get('conditions') else 0.0,
                medications=0.3 if basic_info.get('medications') else 0.0,
                location=0.3 if basic_info.get('location') else 0.0,
                overall=0.2
            ),
            provider_used="manual_fallback",
            extraction_time_ms=0,
            success=False,
            error_message="Automatic extraction failed. Please review and complete the information below."
        )
    
    def _extract_basic_info(self, transcript: str) -> dict:
        """Extract basic information using simple patterns as fallback"""
        import re
        
        info = {}
        text_lower = transcript.lower()
        
        # Simple age extraction
        age_patterns = [
            r'\b(\d{1,2})\s*(?:year|yr)s?\s*old\b',
            r'\bage\s*(?:is\s*)?(\d{1,2})\b',
            r'\b(\d{1,2})\s*(?:year|yr)s?\s*of\s*age\b'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                age = int(match.group(1))
                if 0 < age < 120:
                    info['age'] = age
                    break
        
        # Simple gender extraction
        if 'he ' in text_lower or 'his ' in text_lower or 'mr.' in text_lower:
            info['gender'] = 'MALE'
        elif 'she ' in text_lower or 'her ' in text_lower or 'mrs.' in text_lower or 'ms.' in text_lower:
            info['gender'] = 'FEMALE'
        
        # Simple location extraction
        location = self._enhance_location_data(transcript)
        if location:
            info['location'] = location
        
        return info