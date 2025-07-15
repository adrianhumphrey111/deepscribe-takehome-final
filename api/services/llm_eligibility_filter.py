import logging
from typing import List, Dict, Any, Optional
from models.patient_data import PatientData
from models.trial_data import Trial
from services.llm_router import SmartLLMRouter
from config import Config

logger = logging.getLogger(__name__)

class LLMEligibilityFilter:
    """Use LLM to analyze eligibility criteria and rank trials"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_router = SmartLLMRouter(config)
    
    async def rank_and_filter_trials(self, trials: List[Trial], patient: PatientData, batch_size: int = 8) -> List[Dict[str, Any]]:
        """Use LLM to analyze eligibility and rank trials with batching"""
        if not trials:
            return []
        
        ranked_trials = []
        
        # Process trials in batches to reduce LLM calls
        for i in range(0, len(trials), batch_size):
            batch = trials[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(trials) + batch_size - 1)//batch_size} ({len(batch)} trials)")
            try:
                batch_analyses = await self._analyze_trials_batch(batch, patient)
                
                for j, trial in enumerate(batch):
                    if j < len(batch_analyses):
                        analysis = batch_analyses[j]
                        # Calculate location score if patient coordinates available
                        location_score = self._calculate_location_score(trial, getattr(self, 'patient_coords', None))
                        
                        trial_data = {
                            "trial": trial,
                            "eligibility_score": analysis.get("eligibility_score", 0.5),
                            "location_score": location_score,
                            "combined_score": (analysis.get("eligibility_score", 0.5) * 0.7) + (location_score * 0.3),
                            "is_eligible": analysis.get("is_eligible", True),
                            "reasoning": analysis.get("reasoning", ""),
                            "key_issues": analysis.get("key_issues", [])
                        }
                        
                        # Only include trials that are likely eligible
                        if analysis.get("is_eligible", True):
                            ranked_trials.append(trial_data)
                        else:
                            logger.info(f"LLM filtered out trial {trial.nct_id}: {analysis.get('reasoning', 'Not eligible')}")
                    else:
                        # Fallback if batch analysis didn't return enough results
                        location_score = self._calculate_location_score(trial, getattr(self, 'patient_coords', None))
                        ranked_trials.append({
                            "trial": trial,
                            "eligibility_score": 0.5,
                            "location_score": location_score,
                            "combined_score": (0.5 * 0.7) + (location_score * 0.3),
                            "is_eligible": True,
                            "reasoning": "Batch analysis incomplete",
                            "key_issues": []
                        })
                        
            except Exception as e:
                logger.error(f"Error analyzing batch of trials: {e}")
                # Include all trials in batch with neutral scores if batch analysis fails
                for trial in batch:
                    location_score = self._calculate_location_score(trial, getattr(self, 'patient_coords', None))
                    ranked_trials.append({
                        "trial": trial,
                        "eligibility_score": 0.5,
                        "location_score": location_score,
                        "combined_score": (0.5 * 0.7) + (location_score * 0.3),
                        "is_eligible": True,
                        "reasoning": "Could not analyze eligibility criteria",
                        "key_issues": []
                    })
        
        # Sort by combined score (highest first) - eligibility 70%, location 30%
        ranked_trials.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return ranked_trials
    
    def _calculate_location_score(self, trial: Trial, patient_coords: tuple) -> float:
        """Calculate location-based score (0-1) based on distance to patient"""
        if not patient_coords or not trial.locations:
            return 0.5  # Neutral score if no location data
        
        patient_lat, patient_lon = patient_coords
        min_distance = float('inf')
        
        # Find closest trial location
        for location in trial.locations:
            if location.city and location.state:
                try:
                    # Use simple geocoding for trial locations
                    trial_coords = self._get_trial_location_coordinates(location.city, location.state)
                    if trial_coords:
                        trial_lat, trial_lon = trial_coords
                        # Calculate distance using haversine formula
                        distance = self._calculate_distance(patient_lat, patient_lon, trial_lat, trial_lon)
                        min_distance = min(min_distance, distance)
                except Exception:
                    continue
        
        if min_distance == float('inf'):
            return 0.5  # Neutral score if no valid locations
        
        # Convert distance to score (closer = higher score)
        # Max useful distance: 500 miles, closer locations get exponentially higher scores
        if min_distance <= 50:
            return 1.0
        elif min_distance <= 100:
            return 0.8
        elif min_distance <= 200:
            return 0.6
        elif min_distance <= 500:
            return 0.4
        else:
            return 0.2
    
    def _get_trial_location_coordinates(self, city: str, state: str) -> Optional[tuple]:
        """Get coordinates for trial location (simplified version)"""
        # This could be cached or use the same geocoding service as trials_client
        # For now, return None to avoid making additional API calls
        # In production, this should use a cached geocoding service
        return None
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using haversine formula (in miles)"""
        import math
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in miles
        r = 3956
        
        return c * r
    
    async def _analyze_trials_batch(self, trials: List[Trial], patient: PatientData) -> List[Dict[str, Any]]:
        """Analyze multiple trials in a single LLM call for efficiency"""
        
        # Build patient summary
        patient_summary = self._build_patient_summary(patient)
        
        # Create batch analysis prompt
        prompt = self._build_batch_eligibility_prompt(patient_summary, trials)
        
        # Get LLM analysis
        provider = self.llm_router.select_provider(prompt)
        response = await provider.generate_qa_response(prompt, "")
        
        # Parse batch response
        return self._parse_batch_eligibility_response(response, len(trials))
    
    async def _analyze_trial_eligibility(self, trial: Trial, patient: PatientData) -> Dict[str, Any]:
        """Analyze a single trial's eligibility for the patient"""
        
        # Build patient summary
        patient_summary = self._build_patient_summary(patient)
        
        # Extract eligibility criteria
        eligibility_text = self._extract_eligibility_text(trial)
        
        # Create analysis prompt
        prompt = self._build_eligibility_prompt(patient_summary, eligibility_text, trial)
        
        # Get LLM analysis
        provider = self.llm_router.select_provider(prompt)
        response = await provider.generate_qa_response(prompt, "")
        
        # Parse response
        return self._parse_eligibility_response(response)
    
    def _build_patient_summary(self, patient: PatientData) -> str:
        """Build a concise patient summary for LLM analysis"""
        summary_parts = []
        
        if patient.age:
            summary_parts.append(f"Age: {patient.age} years old")
        
        if patient.gender:
            summary_parts.append(f"Gender: {patient.gender.value}")
        
        if patient.primary_diagnosis:
            summary_parts.append(f"Primary Diagnosis: {patient.primary_diagnosis}")
        
        if patient.cancer_stage:
            summary_parts.append(f"Cancer Stage: {patient.cancer_stage}")
        
        if patient.tumor_markers:
            markers = ", ".join([f"{k}: {v}" for k, v in patient.tumor_markers.items()])
            summary_parts.append(f"Tumor Markers: {markers}")
        
        if patient.tumor_size:
            summary_parts.append(f"Tumor Size: {patient.tumor_size}")
        
        if patient.comorbidities:
            summary_parts.append(f"Comorbidities: {', '.join(patient.comorbidities)}")
        
        if patient.medications:
            summary_parts.append(f"Current Medications: {', '.join(patient.medications)}")
        
        # Infer menopausal status for females
        if patient.gender and patient.gender.value == "FEMALE" and patient.age:
            menopausal_status = patient.infer_menopausal_status()
            summary_parts.append(f"Menopausal Status: {menopausal_status.value}")
        
        return "; ".join(summary_parts)
    
    def _extract_eligibility_text(self, trial: Trial) -> str:
        """Extract eligibility criteria text from trial"""
        eligibility_parts = []
        
        if trial.eligibility_criteria:
            criteria = trial.eligibility_criteria
            
            # Basic criteria
            if criteria.age_min or criteria.age_max:
                age_range = f"Age: {criteria.age_min or 'No minimum'} to {criteria.age_max or 'No maximum'}"
                eligibility_parts.append(age_range)
            
            if criteria.gender:
                eligibility_parts.append(f"Gender: {criteria.gender}")
            
            if criteria.healthy_volunteers is not None:
                hv_status = "Yes" if criteria.healthy_volunteers else "No"
                eligibility_parts.append(f"Healthy Volunteers: {hv_status}")
            
            # Inclusion criteria
            if criteria.inclusion_criteria:
                inclusion_text = "\n".join(criteria.inclusion_criteria)
                eligibility_parts.append(f"Inclusion Criteria:\n{inclusion_text}")
            
            # Exclusion criteria
            if criteria.exclusion_criteria:
                exclusion_text = "\n".join(criteria.exclusion_criteria)
                eligibility_parts.append(f"Exclusion Criteria:\n{exclusion_text}")
        
        return "\n\n".join(eligibility_parts) if eligibility_parts else "No detailed eligibility criteria available"
    
    def _build_eligibility_prompt(self, patient_summary: str, eligibility_text: str, trial: Trial) -> str:
        """Build prompt for LLM eligibility analysis"""
        return f"""
You are a clinical trial eligibility expert. Analyze whether this patient is eligible for the given clinical trial.

PATIENT PROFILE:
{patient_summary}

TRIAL INFORMATION:
Study: {trial.title}
NCT ID: {trial.nct_id}

ELIGIBILITY CRITERIA:
{eligibility_text}

Please provide your analysis in the following JSON format:
{{
    "is_eligible": true/false,
    "eligibility_score": 0.0-1.0,
    "reasoning": "Brief explanation of eligibility decision",
    "key_issues": ["list", "of", "specific", "eligibility", "concerns", "if", "any"]
}}

ANALYSIS GUIDELINES:
1. is_eligible: false only if there are clear, definitive exclusions (age out of range, wrong gender, contraindicated medications, etc.)
2. eligibility_score: 
   - 1.0 = Perfect match, clearly eligible
   - 0.8-0.9 = Very good match, likely eligible
   - 0.6-0.7 = Reasonable match, possibly eligible
   - 0.4-0.5 = Poor match, questionable eligibility
   - 0.0-0.3 = Very poor match, likely not eligible
3. Focus on definitive exclusions rather than minor concerns
4. AGE EXAMPLES: If minimum age is 16 and patient is 29, they ARE eligible. If maximum age is 65 and patient is 70, they are NOT eligible.
4. Pay special attention to:
   - Age requirements (patient must be >= minimum age AND <= maximum age if specified)
   - Gender requirements
   - Disease stage/severity requirements
   - Menopausal status requirements (especially for breast cancer trials)
   - Prior treatment requirements
   - Contraindicated medications/conditions

Return ONLY the JSON response:
"""
    
    def _build_batch_eligibility_prompt(self, patient_summary: str, trials: List[Trial]) -> str:
        """Build prompt for batch LLM eligibility analysis"""
        trials_info = []
        
        for i, trial in enumerate(trials):
            eligibility_text = self._extract_eligibility_text(trial)
            trial_info = f"""
TRIAL {i+1}:
NCT ID: {trial.nct_id}
Title: {trial.title}
Eligibility Criteria:
{eligibility_text}
"""
            trials_info.append(trial_info)
        
        trials_text = "\n".join(trials_info)
        
        return f"""
You are a clinical trial eligibility expert. Analyze whether this patient is eligible for each of the following clinical trials.

PATIENT PROFILE:
{patient_summary}

{trials_text}

Please provide your analysis as a JSON array with one object per trial (in the same order as presented):

[
  {{
    "trial_number": 1,
    "nct_id": "NCT...",
    "is_eligible": true/false,
    "eligibility_score": 0.0-1.0,
    "reasoning": "Brief explanation of eligibility decision",
    "key_issues": ["list", "of", "specific", "eligibility", "concerns", "if", "any"]
  }},
  ...
]

ANALYSIS GUIDELINES:
1. is_eligible: false only if there are clear, definitive exclusions (age out of range, wrong gender, contraindicated medications, etc.)
2. eligibility_score: 
   - 1.0 = Perfect match, clearly eligible
   - 0.8-0.9 = Very good match, likely eligible
   - 0.6-0.7 = Reasonable match, possibly eligible
   - 0.4-0.5 = Poor match, questionable eligibility
   - 0.0-0.3 = Very poor match, likely not eligible
3. Focus on definitive exclusions rather than minor concerns
4. AGE EXAMPLES: If minimum age is 16 and patient is 29, they ARE eligible. If maximum age is 65 and patient is 70, they are NOT eligible.
4. Pay special attention to:
   - Age requirements (patient must be >= minimum age AND <= maximum age if specified)
   - Gender requirements
   - Disease stage/severity requirements
   - Menopausal status requirements (especially for breast cancer trials)
   - Prior treatment requirements
   - Contraindicated medications/conditions

Return ONLY the JSON array:
"""
    
    def _parse_batch_eligibility_response(self, response: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse batch LLM response into list of analysis results"""
        try:
            import json
            import re
            
            # Try to extract JSON array from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                results = json.loads(json_str)
                
                # Validate and clean results
                cleaned_results = []
                for result in results:
                    if isinstance(result, dict):
                        cleaned_results.append({
                            "is_eligible": result.get("is_eligible", True),
                            "eligibility_score": float(result.get("eligibility_score", 0.5)),
                            "reasoning": result.get("reasoning", "No reasoning provided"),
                            "key_issues": result.get("key_issues", [])
                        })
                
                # Pad with fallback results if we didn't get enough
                while len(cleaned_results) < expected_count:
                    cleaned_results.append({
                        "is_eligible": True,
                        "eligibility_score": 0.5,
                        "reasoning": "Incomplete batch analysis",
                        "key_issues": []
                    })
                
                return cleaned_results[:expected_count]  # Trim to expected count
            
        except Exception as e:
            logger.error(f"Error parsing batch LLM eligibility response: {e}")
        
        # Fallback if parsing fails
        return [{
            "is_eligible": True,
            "eligibility_score": 0.5,
            "reasoning": "Could not parse batch eligibility analysis",
            "key_issues": []
        }] * expected_count
    
    def _parse_eligibility_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'\\{.*\\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Validate required fields
                return {
                    "is_eligible": result.get("is_eligible", True),
                    "eligibility_score": float(result.get("eligibility_score", 0.5)),
                    "reasoning": result.get("reasoning", "No reasoning provided"),
                    "key_issues": result.get("key_issues", [])
                }
            
        except Exception as e:
            logger.error(f"Error parsing LLM eligibility response: {e}")
        
        # Fallback if parsing fails
        return {
            "is_eligible": True,
            "eligibility_score": 0.5,
            "reasoning": "Could not parse eligibility analysis",
            "key_issues": []
        }