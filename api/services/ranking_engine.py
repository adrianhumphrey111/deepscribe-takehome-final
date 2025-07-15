import logging
from typing import Dict, List, Tuple
from models.patient_data import PatientData
from models.trial_data import Trial, RankedTrial, TrialStatus
from services.eligibility_filter import EligibilityFilter
import math
import re

logger = logging.getLogger(__name__)

class TrialRankingEngine:
    """Engine for ranking clinical trials based on patient fit"""
    
    def __init__(self):
        self.ranking_weights = {
            'condition_match': 0.30,
            'eligibility_fit': 0.25,
            'geographic_proximity': 0.20,
            'phase_appropriateness': 0.15,
            'enrollment_status': 0.10
        }
        self.eligibility_filter = EligibilityFilter()
    
    def rank_trials(self, trials: List[Trial], patient_data: PatientData) -> List[RankedTrial]:
        """Rank trials based on patient fit"""
        
        if not trials:
            return []
        
        ranked_trials = []
        
        for trial in trials:
            # Calculate individual scores
            match_factors = self._calculate_match_factors(trial, patient_data)
            
            # Calculate overall score
            overall_score = sum(
                match_factors[factor] * weight 
                for factor, weight in self.ranking_weights.items()
            )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(match_factors, trial, patient_data)
            
            ranked_trial = RankedTrial(
                trial=trial,
                match_score=overall_score,
                match_factors=match_factors,
                reasoning=reasoning
            )
            
            ranked_trials.append(ranked_trial)
        
        # Sort by score (descending)
        ranked_trials.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info(f"Ranked {len(ranked_trials)} trials for patient")
        return ranked_trials
    
    def _calculate_match_factors(self, trial: Trial, patient_data: PatientData) -> Dict[str, float]:
        """Calculate individual matching factors"""
        
        factors = {
            'condition_match': self._calculate_condition_match(trial, patient_data),
            'eligibility_fit': self._calculate_eligibility_fit(trial, patient_data),
            'geographic_proximity': self._calculate_geographic_proximity(trial, patient_data),
            'phase_appropriateness': self._calculate_phase_appropriateness(trial, patient_data),
            'enrollment_status': self._calculate_enrollment_status(trial)
        }
        
        return factors
    
    def _calculate_condition_match(self, trial: Trial, patient_data: PatientData) -> float:
        """Calculate how well the trial matches the patient's condition"""
        
        if not patient_data.primary_diagnosis and not patient_data.conditions:
            return 0.0
        
        # Get trial conditions from title, summary, and other fields
        trial_text = ' '.join(filter(None, [
            trial.title,
            trial.brief_summary,
            trial.detailed_description
        ])).lower()
        
        # Primary diagnosis match
        primary_score = 0.0
        if patient_data.primary_diagnosis:
            primary_condition = patient_data.primary_diagnosis.lower()
            if primary_condition in trial_text:
                primary_score = 1.0
            else:
                # Check for related terms
                primary_score = self._calculate_semantic_similarity(primary_condition, trial_text)
        
        # Secondary conditions match
        secondary_score = 0.0
        if patient_data.conditions:
            matches = 0
            for condition in patient_data.conditions:
                condition_lower = condition.lower()
                if condition_lower in trial_text:
                    matches += 1
                else:
                    matches += self._calculate_semantic_similarity(condition_lower, trial_text)
            
            secondary_score = matches / len(patient_data.conditions)
        
        # Combined score (prioritize primary diagnosis)
        if patient_data.primary_diagnosis:
            return 0.7 * primary_score + 0.3 * secondary_score
        else:
            return secondary_score
    
    def _calculate_eligibility_fit(self, trial: Trial, patient_data: PatientData) -> float:
        """Calculate how well the patient fits the trial eligibility criteria"""
        
        if not trial.eligibility_criteria:
            return 0.5  # Unknown eligibility
        
        eligibility = trial.eligibility_criteria
        score = 1.0
        
        # Age eligibility
        if patient_data.age:
            age_fit = self._check_age_eligibility(patient_data.age, eligibility)
            score *= age_fit
        
        # Gender eligibility
        if patient_data.gender:
            gender_fit = self._check_gender_eligibility(patient_data.gender, eligibility)
            score *= gender_fit
        
        # Medication contraindications (simplified)
        if patient_data.medications:
            medication_fit = self._check_medication_compatibility(patient_data.medications, eligibility)
            score *= medication_fit
        
        # Comorbidities check
        if patient_data.comorbidities:
            comorbidity_fit = self._check_comorbidity_compatibility(patient_data.comorbidities, eligibility)
            score *= comorbidity_fit
        
        return max(0.0, min(1.0, score))
    
    def _calculate_geographic_proximity(self, trial: Trial, patient_data: PatientData) -> float:
        """Calculate geographic proximity score"""
        
        if not trial.locations or not patient_data.location:
            return 0.3  # Unknown location
        
        patient_location = patient_data.location
        
        # Find the closest trial location
        min_distance = float('inf')
        
        for location in trial.locations:
            distance = self._calculate_distance(patient_location, location)
            if distance < min_distance:
                min_distance = distance
        
        if min_distance == float('inf'):
            return 0.3
        
        # Convert distance to score (closer = higher score)
        # Score decreases exponentially with distance
        if min_distance <= 10:
            return 1.0
        elif min_distance <= 25:
            return 0.8
        elif min_distance <= 50:
            return 0.6
        elif min_distance <= 100:
            return 0.4
        else:
            return 0.2
    
    def _calculate_phase_appropriateness(self, trial: Trial, patient_data: PatientData) -> float:
        """Calculate phase appropriateness based on patient condition"""
        
        if not trial.phase:
            return 0.5
        
        # Phase scoring based on condition severity and treatment history
        phase_scores = {
            'EARLY_PHASE_1': 0.3,  # Very experimental
            'PHASE_1': 0.4,        # Safety testing
            'PHASE_2': 0.7,        # Efficacy testing
            'PHASE_3': 0.9,        # Large scale testing
            'PHASE_4': 0.8,        # Post-market surveillance
            'NOT_APPLICABLE': 0.6  # Device studies, etc.
        }
        
        base_score = phase_scores.get(trial.phase.value, 0.5)
        
        # Adjust based on patient factors
        # More aggressive conditions might benefit from earlier phase trials
        if patient_data.primary_diagnosis:
            diagnosis_lower = patient_data.primary_diagnosis.lower()
            
            # Higher risk conditions might justify earlier phase trials
            high_risk_conditions = ['cancer', 'carcinoma', 'lymphoma', 'leukemia', 'sarcoma']
            if any(condition in diagnosis_lower for condition in high_risk_conditions):
                if trial.phase.value in ['EARLY_PHASE_1', 'PHASE_1', 'PHASE_2']:
                    base_score += 0.2
        
        return min(1.0, base_score)
    
    def _calculate_enrollment_status(self, trial: Trial) -> float:
        """Calculate enrollment status score"""
        
        status_scores = {
            TrialStatus.RECRUITING: 1.0,
            TrialStatus.NOT_YET_RECRUITING: 0.8,
            TrialStatus.ACTIVE_NOT_RECRUITING: 0.6,
            TrialStatus.ENROLLING_BY_INVITATION: 0.4,
            TrialStatus.COMPLETED: 0.0,
            TrialStatus.SUSPENDED: 0.1,
            TrialStatus.TERMINATED: 0.0,
            TrialStatus.WITHDRAWN: 0.0
        }
        
        return status_scores.get(trial.status, 0.3)
    
    def _calculate_semantic_similarity(self, condition: str, text: str) -> float:
        """Calculate semantic similarity between condition and text"""
        
        # Simple keyword-based similarity
        condition_keywords = condition.split()
        matches = 0
        
        for keyword in condition_keywords:
            if len(keyword) > 2 and keyword in text:
                matches += 1
        
        if not condition_keywords:
            return 0.0
        
        return matches / len(condition_keywords)
    
    def _check_age_eligibility(self, patient_age: int, eligibility) -> float:
        """Check if patient age fits eligibility criteria"""
        
        min_age = eligibility.age_min
        max_age = eligibility.age_max
        
        if min_age is None and max_age is None:
            return 1.0
        
        if min_age is not None and patient_age < min_age:
            return 0.0
        
        if max_age is not None and patient_age > max_age:
            return 0.0
        
        return 1.0
    
    def _check_gender_eligibility(self, patient_gender: str, eligibility) -> float:
        """Check if patient gender fits eligibility criteria"""
        
        if not eligibility.gender or eligibility.gender == 'ALL':
            return 1.0
        
        if patient_gender == eligibility.gender:
            return 1.0
        
        return 0.0
    
    def _check_medication_compatibility(self, medications: List[str], eligibility) -> float:
        """Check medication compatibility (simplified)"""
        
        # This is a simplified check
        # In a real system, we'd have a comprehensive drug interaction database
        
        if not eligibility.exclusion_criteria:
            return 1.0
        
        exclusion_text = ' '.join(eligibility.exclusion_criteria).lower()
        
        # Check for common medication exclusions
        for medication in medications:
            med_lower = medication.lower()
            if med_lower in exclusion_text:
                return 0.5  # Potential exclusion
        
        return 1.0
    
    def _check_comorbidity_compatibility(self, comorbidities: List[str], eligibility) -> float:
        """Check comorbidity compatibility"""
        
        if not eligibility.exclusion_criteria:
            return 1.0
        
        exclusion_text = ' '.join(eligibility.exclusion_criteria).lower()
        
        # Check for comorbidity exclusions
        for comorbidity in comorbidities:
            comorb_lower = comorbidity.lower()
            if comorb_lower in exclusion_text:
                return 0.7  # Potential exclusion
        
        return 1.0
    
    def _calculate_distance(self, patient_location, trial_location) -> float:
        """Calculate distance between patient and trial location"""
        
        # Simple city/state matching for now
        # In a real system, we'd use geocoding and proper distance calculation
        
        if (patient_location.city and trial_location.city and 
            patient_location.state and trial_location.state):
            
            if (patient_location.city.lower() == trial_location.city.lower() and
                patient_location.state.lower() == trial_location.state.lower()):
                return 0.0  # Same city
            
            if patient_location.state.lower() == trial_location.state.lower():
                return 50.0  # Same state
            
            return 200.0  # Different state
        
        return 100.0  # Unknown
    
    def _generate_reasoning(self, match_factors: Dict[str, float], trial: Trial, patient_data: PatientData) -> str:
        """Generate human-readable reasoning for the match"""
        
        reasoning_parts = []
        
        # Condition match
        condition_score = match_factors['condition_match']
        if condition_score > 0.8:
            reasoning_parts.append("Excellent condition match")
        elif condition_score > 0.6:
            reasoning_parts.append("Good condition match")
        elif condition_score > 0.4:
            reasoning_parts.append("Moderate condition match")
        else:
            reasoning_parts.append("Limited condition match")
        
        # Eligibility
        eligibility_score = match_factors['eligibility_fit']
        if eligibility_score > 0.8:
            reasoning_parts.append("meets eligibility criteria")
        elif eligibility_score > 0.6:
            reasoning_parts.append("likely meets eligibility criteria")
        else:
            reasoning_parts.append("eligibility uncertain")
        
        # Location
        location_score = match_factors['geographic_proximity']
        if location_score > 0.8:
            reasoning_parts.append("convenient location")
        elif location_score > 0.5:
            reasoning_parts.append("accessible location")
        else:
            reasoning_parts.append("distant location")
        
        # Status
        status_score = match_factors['enrollment_status']
        if status_score > 0.8:
            reasoning_parts.append("actively recruiting")
        elif status_score > 0.5:
            reasoning_parts.append("enrollment available")
        else:
            reasoning_parts.append("limited enrollment")
        
        return ", ".join(reasoning_parts).capitalize()