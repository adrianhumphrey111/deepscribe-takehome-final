from abc import ABC, abstractmethod
from typing import Dict, Optional
import json
import time
import logging
from models.patient_data import PatientData, ExtractionResult, ConfidenceScores
from config import Config

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: Config):
        self.config = config
    
    @abstractmethod
    async def extract_patient_data(self, transcript: str) -> ExtractionResult:
        """Extract patient data from transcript"""
        pass
    
    @abstractmethod
    async def generate_qa_response(self, question: str, context: str) -> str:
        """Generate Q&A response"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        import openai
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    async def extract_patient_data(self, transcript: str) -> ExtractionResult:
        """Extract patient data using OpenAI GPT-4"""
        start_time = time.time()
        
        try:
            extraction_prompt = self._build_extraction_prompt(transcript)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant that extracts structured patient data from clinical transcripts. Always return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            
            # Parse the JSON response
            try:
                extracted_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from OpenAI response")
            
            # Convert to our models
            patient_data = self._convert_to_patient_data(extracted_data)
            confidence_scores = self._calculate_confidence_scores(extracted_data)
            
            extraction_time = int((time.time() - start_time) * 1000)
            
            return ExtractionResult(
                patient_data=patient_data,
                confidence_scores=confidence_scores,
                provider_used=self.provider_name,
                extraction_time_ms=extraction_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            extraction_time = int((time.time() - start_time) * 1000)
            
            return ExtractionResult(
                patient_data=PatientData(),
                confidence_scores=ConfidenceScores(),
                provider_used=self.provider_name,
                extraction_time_ms=extraction_time,
                success=False,
                error_message=str(e)
            )
    
    async def generate_qa_response(self, question: str, context: str) -> str:
        """Generate Q&A response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a medical AI assistant helping doctors understand clinical trials. Provide accurate, helpful responses based on the trial information provided."},
                    {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI Q&A failed: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _build_extraction_prompt(self, transcript: str) -> str:
        """Build extraction prompt for OpenAI"""
        return f"""
        You are extracting patient information for CLINICAL TRIAL MATCHING. Focus on the primary condition the patient wants to find clinical trials for.
        
        Extract the following information from this medical transcript and return it as JSON:
        - age (integer)
        - gender ("MALE", "FEMALE", or "ALL")
        - conditions (array of strings - secondary conditions only if relevant for trials)
        - primary_diagnosis (string - THE MAIN CONDITION for which they need clinical trials, or null if unclear)
        - comorbidities (array of strings - only significant comorbidities that would affect trial eligibility)
        - medications (array of strings - normalize drug names, e.g., "baby aspirin" → "aspirin")
        - allergies (array of strings)
        - location (object with city, state, zip_code - normalize state abbreviations, e.g., "CO" → "Colorado")
        - cancer_stage (string, e.g., "Stage IIA", "Stage IIIB")
        - tumor_markers (object with markers like {{"ER": "positive", "PR": "negative", "HER2": "positive"}})
        - tumor_size (string, e.g., "2.5 cm")
        - overall_confidence (single number 0-1 representing how confident you are in the overall extraction quality)
        
        CRITICAL RULES for primary_diagnosis:
        1. CONFIRMED DIAGNOSIS ONLY: Only use if explicitly stated or clearly documented (e.g., "diagnosed with", "confirmed", established treatment)
        2. SUSPICIOUS/PENDING: If "suspicious", "rule out", "scheduled for biopsy", "pending results" → set to null
        3. SYMPTOMS ONLY: If only symptoms without diagnosis (fatigue, pain) → set to null
        4. BE CONSERVATIVE: When in doubt, use null rather than guessing
        
        NORMALIZATION EXAMPLES:
        - "T1DM" or "T1D" → "Type 1 diabetes mellitus"
        - "NSCLC" → "non-small cell lung cancer"
        - "CO", "Colo" → "Colorado"
        - "MA", "Mass" → "Massachusetts"
        - Drug dosing (remove): "Metoprolol XL 50mg BID" → "Metoprolol"
        
        CONFIDENCE CALIBRATION (be more conservative):
        - 0.9-1.0: Complete, explicit information with confirmed diagnosis
        - 0.7-0.8: Good extraction with some abbreviations/inferences, clear diagnosis
        - 0.5-0.6: Moderate quality, some missing data or abbreviations
        - 0.3-0.4: Minimal information, mostly symptoms, no clear diagnosis
        - 0.1-0.2: Very little reliable information, highly ambiguous
        
        EXAMPLES:
        - "58-year-old with invasive ductal carcinoma" → primary_diagnosis: "breast cancer", confidence: 0.9
        - "T1DM patient on insulin" → primary_diagnosis: "Type 1 diabetes mellitus", confidence: 0.8
        - "suspicious breast lump, biopsy pending" → primary_diagnosis: null, confidence: 0.4
        - "fatigue, memory issues" → primary_diagnosis: null, confidence: 0.2
        
        Transcript:
        {transcript}
        
        Return only valid JSON:
        """
    
    def _convert_to_patient_data(self, extracted_data: Dict) -> PatientData:
        """Convert extracted data to PatientData model"""
        patient_data = PatientData(
            age=extracted_data.get('age'),
            gender=extracted_data.get('gender'),
            conditions=extracted_data.get('conditions', []),
            primary_diagnosis=extracted_data.get('primary_diagnosis'),
            comorbidities=extracted_data.get('comorbidities', []),
            medications=extracted_data.get('medications', []),
            allergies=extracted_data.get('allergies', []),
            location=extracted_data.get('location'),
            cancer_stage=extracted_data.get('cancer_stage'),
            tumor_markers={k: v for k, v in (extracted_data.get('tumor_markers') or {}).items() if v is not None},
            tumor_size=extracted_data.get('tumor_size')
        )
        
        return patient_data
    
    def _calculate_confidence_scores(self, extracted_data: Dict) -> ConfidenceScores:
        """Calculate confidence scores from extracted data"""
        # Use the LLM-provided overall confidence for all fields
        overall_confidence = extracted_data.get('overall_confidence', 0.5)
        
        return ConfidenceScores(
            age=overall_confidence,
            gender=overall_confidence,
            primary_diagnosis=overall_confidence,
            conditions=overall_confidence,
            medications=overall_confidence,
            location=overall_confidence,
            overall=overall_confidence
        )

class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, config: Config):
        super().__init__(config)
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key is required")
        
        import anthropic
        self.client = anthropic.Client(api_key=config.ANTHROPIC_API_KEY)
    
    @property
    def provider_name(self) -> str:
        return "claude"
    
    async def extract_patient_data(self, transcript: str) -> ExtractionResult:
        """Extract patient data using Claude"""
        start_time = time.time()
        
        try:
            extraction_prompt = self._build_extraction_prompt(transcript)
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": extraction_prompt}
                ]
            )
            
            result_text = response.content[0].text
            
            # Parse the JSON response
            try:
                extracted_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from Claude response")
            
            # Convert to our models
            patient_data = self._convert_to_patient_data(extracted_data)
            confidence_scores = self._calculate_confidence_scores(extracted_data)
            
            extraction_time = int((time.time() - start_time) * 1000)
            
            return ExtractionResult(
                patient_data=patient_data,
                confidence_scores=confidence_scores,
                provider_used=self.provider_name,
                extraction_time_ms=extraction_time,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Claude extraction failed: {str(e)}")
            extraction_time = int((time.time() - start_time) * 1000)
            
            return ExtractionResult(
                patient_data=PatientData(),
                confidence_scores=ConfidenceScores(),
                provider_used=self.provider_name,
                extraction_time_ms=extraction_time,
                success=False,
                error_message=str(e)
            )
    
    async def generate_qa_response(self, question: str, context: str) -> str:
        """Generate Q&A response using Claude"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": f"You are a medical AI assistant helping doctors understand clinical trials. Provide accurate, helpful responses based on the trial information provided.\n\nContext: {context}\n\nQuestion: {question}"}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude Q&A failed: {str(e)}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _build_extraction_prompt(self, transcript: str) -> str:
        """Build extraction prompt for Claude"""
        return f"""
        You are extracting patient information for CLINICAL TRIAL MATCHING. Focus on the primary condition the patient wants to find clinical trials for.
        
        Extract the following information from this medical transcript and return it as JSON:
        - age (integer)
        - gender ("MALE", "FEMALE", or "ALL")
        - conditions (array of strings - secondary conditions only if relevant for trials)
        - primary_diagnosis (string - THE MAIN CONDITION for which they need clinical trials, or null if unclear)
        - comorbidities (array of strings - only significant comorbidities that would affect trial eligibility)
        - medications (array of strings - normalize drug names, e.g., "baby aspirin" → "aspirin")
        - allergies (array of strings)
        - location (object with city, state, zip_code - normalize state abbreviations, e.g., "CO" → "Colorado")
        - cancer_stage (string, e.g., "Stage IIA", "Stage IIIB")
        - tumor_markers (object with markers like {{"ER": "positive", "PR": "negative", "HER2": "positive"}})
        - tumor_size (string, e.g., "2.5 cm")
        - overall_confidence (single number 0-1 representing how confident you are in the overall extraction quality)
        
        CRITICAL RULES for primary_diagnosis:
        1. CONFIRMED DIAGNOSIS ONLY: Only use if explicitly stated or clearly documented (e.g., "diagnosed with", "confirmed", established treatment)
        2. SUSPICIOUS/PENDING: If "suspicious", "rule out", "scheduled for biopsy", "pending results" → set to null
        3. SYMPTOMS ONLY: If only symptoms without diagnosis (fatigue, pain) → set to null
        4. BE CONSERVATIVE: When in doubt, use null rather than guessing
        
        NORMALIZATION EXAMPLES:
        - "T1DM" or "T1D" → "Type 1 diabetes mellitus"
        - "NSCLC" → "non-small cell lung cancer"
        - "CO", "Colo" → "Colorado"
        - "MA", "Mass" → "Massachusetts"
        - Drug dosing (remove): "Metoprolol XL 50mg BID" → "Metoprolol"
        
        CONFIDENCE CALIBRATION (be more conservative):
        - 0.9-1.0: Complete, explicit information with confirmed diagnosis
        - 0.7-0.8: Good extraction with some abbreviations/inferences, clear diagnosis
        - 0.5-0.6: Moderate quality, some missing data or abbreviations
        - 0.3-0.4: Minimal information, mostly symptoms, no clear diagnosis
        - 0.1-0.2: Very little reliable information, highly ambiguous
        
        EXAMPLES:
        - "58-year-old with invasive ductal carcinoma" → primary_diagnosis: "breast cancer", confidence: 0.9
        - "T1DM patient on insulin" → primary_diagnosis: "Type 1 diabetes mellitus", confidence: 0.8
        - "suspicious breast lump, biopsy pending" → primary_diagnosis: null, confidence: 0.4
        - "fatigue, memory issues" → primary_diagnosis: null, confidence: 0.2
        
        Transcript:
        {transcript}
        
        Return only valid JSON without any additional text:
        """
    
    def _convert_to_patient_data(self, extracted_data: Dict) -> PatientData:
        """Convert extracted data to PatientData model"""
        patient_data = PatientData(
            age=extracted_data.get('age'),
            gender=extracted_data.get('gender'),
            conditions=extracted_data.get('conditions', []),
            primary_diagnosis=extracted_data.get('primary_diagnosis'),
            comorbidities=extracted_data.get('comorbidities', []),
            medications=extracted_data.get('medications', []),
            allergies=extracted_data.get('allergies', []),
            location=extracted_data.get('location'),
            cancer_stage=extracted_data.get('cancer_stage'),
            tumor_markers={k: v for k, v in (extracted_data.get('tumor_markers') or {}).items() if v is not None},
            tumor_size=extracted_data.get('tumor_size')
        )
        
        return patient_data
    
    def _calculate_confidence_scores(self, extracted_data: Dict) -> ConfidenceScores:
        """Calculate confidence scores from extracted data"""
        # Use the LLM-provided overall confidence for all fields
        overall_confidence = extracted_data.get('overall_confidence', 0.5)
        
        return ConfidenceScores(
            age=overall_confidence,
            gender=overall_confidence,
            primary_diagnosis=overall_confidence,
            conditions=overall_confidence,
            medications=overall_confidence,
            location=overall_confidence,
            overall=overall_confidence
        )