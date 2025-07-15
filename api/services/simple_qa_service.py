"""
Simple Q&A service without LangChain dependencies
Direct calls to OpenAI/Anthropic APIs
"""
import asyncio
import logging
from typing import Optional, Dict, Any
import json
from .llm_provider import LLMProvider

logger = logging.getLogger(__name__)

class SimpleQAService:
    """Lightweight Q&A service using direct LLM API calls"""
    
    def __init__(self, config):
        self.config = config
        self.llm_provider = LLMProvider(config)
        
    async def answer_question(self, trial_id: str, question: str, patient_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Answer a question about a clinical trial using direct LLM calls
        """
        try:
            # Get trial data (simplified - in real implementation, fetch from database/API)
            trial_data = await self._get_trial_data(trial_id)
            
            # Build context prompt
            context_prompt = self._build_qa_prompt(trial_data, question, patient_context)
            
            # Call LLM directly
            start_time = asyncio.get_event_loop().time()
            
            if self.config.ENABLE_CLAUDE_PROVIDER:
                response = await self._call_claude(context_prompt)
                provider_used = "claude"
            elif self.config.ENABLE_OPENAI_PROVIDER:
                response = await self._call_openai(context_prompt)
                provider_used = "openai"
            else:
                raise Exception("No LLM providers enabled")
            
            processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            return {
                "success": True,
                "answer": response,
                "trial_id": trial_id,
                "question": question,
                "provider_used": provider_used,
                "processing_time_ms": processing_time,
                "confidence": "high"  # Could add confidence scoring later
            }
            
        except Exception as e:
            logger.error(f"Error in Q&A service: {str(e)}")
            return {
                "success": False,
                "error_message": str(e),
                "trial_id": trial_id,
                "question": question
            }
    
    async def _get_trial_data(self, trial_id: str) -> Dict:
        """Get trial data - simplified for demo"""
        # In real implementation, this would fetch from clinicaltrials.gov API
        # For now, return mock data
        return {
            "nct_id": trial_id,
            "title": "Phase III Trial of New Cancer Treatment",
            "description": "A randomized, double-blind, placebo-controlled trial evaluating a new treatment approach",
            "eligibility_criteria": {
                "inclusion": [
                    "Age 18-75 years",
                    "Confirmed diagnosis of target condition",
                    "ECOG performance status 0-2"
                ],
                "exclusion": [
                    "Previous treatment with study drug",
                    "Severe cardiac disease",
                    "Pregnancy or nursing"
                ]
            },
            "primary_outcome": "Overall survival at 24 months",
            "study_phase": "Phase 3",
            "enrollment_target": 500,
            "locations": ["Multiple sites in US and Canada"]
        }
    
    def _build_qa_prompt(self, trial_data: Dict, question: str, patient_context: Optional[Dict] = None) -> str:
        """Build prompt for Q&A without LangChain templates"""
        
        patient_info = ""
        if patient_context:
            patient_info = f"""
Patient Context:
- Age: {patient_context.get('age', 'Not specified')}
- Diagnosis: {patient_context.get('primary_diagnosis', 'Not specified')}
- Medical History: {patient_context.get('medical_history', 'Not specified')}
"""
        
        prompt = f"""You are a clinical trial expert assistant. Answer the following question about this clinical trial accurately and concisely.

Clinical Trial Information:
- Trial ID: {trial_data.get('nct_id', 'Unknown')}
- Title: {trial_data.get('title', 'Unknown')}
- Description: {trial_data.get('description', 'Unknown')}
- Phase: {trial_data.get('study_phase', 'Unknown')}
- Primary Outcome: {trial_data.get('primary_outcome', 'Unknown')}
- Target Enrollment: {trial_data.get('enrollment_target', 'Unknown')}

Eligibility Criteria:
Inclusion: {', '.join(trial_data.get('eligibility_criteria', {}).get('inclusion', []))}
Exclusion: {', '.join(trial_data.get('eligibility_criteria', {}).get('exclusion', []))}

{patient_info}

Question: {question}

Please provide a clear, accurate answer based on the trial information above. If the information needed to answer the question is not available in the trial data, please state that clearly.

Answer:"""
        
        return prompt
    
    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI directly without LangChain"""
        import openai
        
        client = openai.AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful clinical trial expert assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    async def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude directly without LangChain"""
        import anthropic
        
        client = anthropic.AsyncAnthropic(api_key=self.config.ANTHROPIC_API_KEY)
        
        response = await client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text.strip()