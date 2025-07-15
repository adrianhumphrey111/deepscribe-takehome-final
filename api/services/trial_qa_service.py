"""
AI-powered Q&A service for clinical trials
Provides conversational interface for trial-related questions
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from services.llm_provider import LLMProvider
from services.llm_router import SmartLLMRouter
from services.trials_client import ClinicalTrialsClient
from models.patient_data import PatientData

logger = logging.getLogger(__name__)

class TrialQAService:
    """Service for answering questions about clinical trials using AI"""
    
    def __init__(self, config):
        self.config = config
        self.llm_router = SmartLLMRouter(config)
        self.trials_client = ClinicalTrialsClient(config)
        
    async def answer_question(
        self, 
        trial_id: str, 
        question: str, 
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question about a specific clinical trial
        
        Args:
            trial_id: NCT ID of the trial
            question: User's question about the trial
            patient_context: Optional patient information for personalized answers
            
        Returns:
            Dictionary containing answer, confidence, and sources
        """
        try:
            # Get detailed trial information
            trial_details = await self._get_trial_details(trial_id)
            
            if not trial_details:
                return {
                    "success": False,
                    "error_message": f"Could not find trial details for {trial_id}"
                }
            
            # Select appropriate LLM provider
            llm_provider = self.llm_router.select_provider(question)
            
            # Generate context-aware answer
            answer_data = await self._generate_answer(
                llm_provider, 
                trial_details, 
                question, 
                patient_context
            )
            
            return {
                "success": True,
                "answer": answer_data["answer"],
                "confidence": answer_data["confidence"],
                "sources": answer_data["sources"],
                "provider_used": answer_data["provider_used"],
                "response_time_ms": answer_data["response_time_ms"]
            }
            
        except Exception as e:
            logger.error(f"Error in answer_question: {str(e)}")
            return {
                "success": False,
                "error_message": str(e)
            }
    
    async def _get_trial_details(self, trial_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed trial information from ClinicalTrials.gov"""
        try:
            # Use the trials client to get detailed information
            trial_details = await self.trials_client.get_trial_dict(trial_id)
            return trial_details
        except Exception as e:
            logger.error(f"Error fetching trial details for {trial_id}: {str(e)}")
            return None
    
    async def _generate_answer(
        self, 
        llm_provider: LLMProvider, 
        trial_details: Dict[str, Any], 
        question: str, 
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI-powered answer using trial context"""
        import time
        start_time = time.time()
        
        # Build comprehensive context
        context = self._build_trial_context(trial_details, patient_context)
        
        # Create specialized Q&A prompt
        prompt = self._create_qa_prompt(context, question, patient_context)
        
        try:
            # Generate response using selected LLM
            response = await llm_provider.generate_qa_response(question, context)
            
            # Parse structured response
            answer_data = self._parse_qa_response(response)
            
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                "answer": answer_data["answer"],
                "confidence": answer_data.get("confidence", 0.8),
                "sources": answer_data.get("sources", []),
                "provider_used": llm_provider.__class__.__name__,
                "response_time_ms": response_time
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def _build_trial_context(
        self, 
        trial_details: Dict[str, Any], 
        patient_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build comprehensive context about the trial"""
        context_parts = []
        
        # Basic trial information
        context_parts.append(f"TRIAL: {trial_details.get('title', 'Unknown')}")
        context_parts.append(f"NCT ID: {trial_details.get('nct_id', 'Unknown')}")
        context_parts.append(f"Status: {trial_details.get('status', 'Unknown')}")
        context_parts.append(f"Phase: {trial_details.get('phase', 'Unknown')}")
        
        # Study details
        if trial_details.get('brief_summary'):
            context_parts.append(f"Summary: {trial_details['brief_summary']}")
        
        if trial_details.get('detailed_description'):
            context_parts.append(f"Detailed Description: {trial_details['detailed_description']}")
        
        # Eligibility criteria
        if trial_details.get('eligibility_criteria'):
            eligibility = trial_details['eligibility_criteria']
            context_parts.append("ELIGIBILITY CRITERIA:")
            
            if eligibility.get('inclusion_criteria'):
                context_parts.append(f"Inclusion: {'; '.join(eligibility['inclusion_criteria'])}")
            
            if eligibility.get('exclusion_criteria'):
                context_parts.append(f"Exclusion: {'; '.join(eligibility['exclusion_criteria'])}")
            
            context_parts.append(f"Age Range: {eligibility.get('age_min', 'Any')} to {eligibility.get('age_max', 'Any')}")
            context_parts.append(f"Gender: {eligibility.get('gender', 'All')}")
        
        # Outcomes
        if trial_details.get('primary_outcome'):
            context_parts.append(f"Primary Outcome: {trial_details['primary_outcome']}")
        
        if trial_details.get('secondary_outcomes'):
            context_parts.append(f"Secondary Outcomes: {'; '.join(trial_details['secondary_outcomes'])}")
        
        # Locations
        if trial_details.get('locations'):
            locations = [f"{loc.get('city', '')}, {loc.get('state', '')}" 
                        for loc in trial_details['locations'][:5]]
            context_parts.append(f"Locations: {'; '.join(locations)}")
        
        # Patient context if provided
        if patient_context:
            context_parts.append("PATIENT CONTEXT:")
            context_parts.append(f"Age: {patient_context.get('age', 'Unknown')}")
            context_parts.append(f"Gender: {patient_context.get('gender', 'Unknown')}")
            context_parts.append(f"Primary Diagnosis: {patient_context.get('primary_diagnosis', 'Unknown')}")
            
            if patient_context.get('conditions'):
                context_parts.append(f"Conditions: {'; '.join(patient_context['conditions'])}")
            
            if patient_context.get('medications'):
                context_parts.append(f"Medications: {'; '.join(patient_context['medications'])}")
        
        return "\n".join(context_parts)
    
    def _create_qa_prompt(
        self, 
        context: str, 
        question: str, 
        patient_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create specialized prompt for Q&A"""
        prompt = f"""You are a clinical trial expert assistant helping healthcare providers understand trial details.

TRIAL INFORMATION:
{context}

QUESTION: {question}

Instructions:
1. Provide a clear, accurate answer based on the trial information provided
2. If the question relates to patient eligibility, consider the patient context provided
3. Be specific about what information comes from the trial protocol
4. If information is not available in the trial details, clearly state this
5. For medical questions, remind users to consult healthcare providers
6. Use professional medical terminology but keep explanations accessible

{"Consider the patient's specific medical profile when answering." if patient_context else ""}

Respond with a helpful, accurate answer that addresses the question directly."""
        
        return prompt
    
    def _parse_qa_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        # For now, treat the entire response as the answer
        # In a more sophisticated implementation, you could parse
        # structured responses that include confidence scores and sources
        
        # Try to extract confidence and sources if they're in the response
        confidence = 0.8  # Default confidence
        sources = []
        
        # Look for confidence indicators in the response
        if "very confident" in response.lower() or "certain" in response.lower():
            confidence = 0.9
        elif "somewhat confident" in response.lower() or "likely" in response.lower():
            confidence = 0.7
        elif "uncertain" in response.lower() or "not sure" in response.lower():
            confidence = 0.5
        
        # Extract sources if mentioned
        if "protocol" in response.lower():
            sources.append("Trial Protocol")
        if "eligibility" in response.lower():
            sources.append("Eligibility Criteria")
        if "investigator" in response.lower():
            sources.append("Investigator Information")
        
        return {
            "answer": response.strip(),
            "confidence": confidence,
            "sources": sources
        }