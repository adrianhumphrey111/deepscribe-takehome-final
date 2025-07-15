import re
import logging
from typing import List, Optional
from models.patient_data import PatientData, MenopausalStatus
from models.trial_data import Trial

logger = logging.getLogger(__name__)

class EligibilityFilter:
    """Filter trials based on eligibility criteria"""
    
    def filter_eligible_trials(self, trials: List[Trial], patient: PatientData) -> List[Trial]:
        """Filter trials based on patient eligibility"""
        eligible_trials = []
        
        for trial in trials:
            if self._is_patient_eligible(trial, patient):
                eligible_trials.append(trial)
            else:
                logger.info(f"Filtered out trial {trial.nct_id}: eligibility mismatch")
        
        return eligible_trials
    
    def _is_patient_eligible(self, trial: Trial, patient: PatientData) -> bool:
        """Check if patient meets basic eligibility criteria for a trial"""
        if not trial.eligibility_criteria:
            return True  # No criteria to check
        
        # Check age requirements
        if not self._check_age_eligibility(trial, patient):
            logger.debug(f"Age mismatch for {trial.nct_id}: patient {patient.age}")
            return False
        
        # Check gender requirements
        if not self._check_gender_eligibility(trial, patient):
            logger.debug(f"Gender mismatch for {trial.nct_id}")
            return False
        
        # Check menopausal status for breast cancer trials
        if not self._check_menopausal_status_eligibility(trial, patient):
            logger.debug(f"Menopausal status mismatch for {trial.nct_id}")
            return False
        
        # Check for obvious exclusion criteria
        if not self._check_exclusion_criteria(trial, patient):
            logger.debug(f"Exclusion criteria triggered for {trial.nct_id}")
            return False
        
        return True
    
    def _check_age_eligibility(self, trial: Trial, patient: PatientData) -> bool:
        """Check age eligibility"""
        if not patient.age or not trial.eligibility_criteria:
            return True
        
        criteria = trial.eligibility_criteria
        patient_age = patient.age
        
        # Check minimum age
        if criteria.age_min and patient_age < criteria.age_min:
            return False
        
        # Check maximum age
        if criteria.age_max and patient_age > criteria.age_max:
            return False
        
        return True
    
    def _check_gender_eligibility(self, trial: Trial, patient: PatientData) -> bool:
        """Check gender eligibility"""
        if not patient.gender or not trial.eligibility_criteria:
            return True
        
        trial_gender = trial.eligibility_criteria.gender
        if trial_gender == "ALL":
            return True
        
        return trial_gender == patient.gender.value
    
    def _check_menopausal_status_eligibility(self, trial: Trial, patient: PatientData) -> bool:
        """Check menopausal status eligibility for relevant trials"""
        if not trial.eligibility_criteria or not patient.gender:
            return True
        
        # Only check for female patients
        if patient.gender.value != "FEMALE":
            return True
        
        # Look for menopausal requirements in inclusion criteria
        inclusion_text = " ".join(trial.eligibility_criteria.inclusion_criteria or []).lower()
        exclusion_text = " ".join(trial.eligibility_criteria.exclusion_criteria or []).lower()
        
        # Check for premenopausal requirements
        premenopausal_keywords = [
            "premenopausal", "pre-menopausal", "functioning ovaries", 
            "menstruating", "reproductive age"
        ]
        
        postmenopausal_keywords = [
            "postmenopausal", "post-menopausal", "amenorrhea", 
            "no menstrual periods", "natural menopause"
        ]
        
        requires_premenopausal = any(keyword in inclusion_text for keyword in premenopausal_keywords)
        requires_postmenopausal = any(keyword in inclusion_text for keyword in postmenopausal_keywords)
        
        # If trial has specific menopausal requirements, check patient status
        if requires_premenopausal or requires_postmenopausal:
            # Infer patient's menopausal status
            if patient.menopausal_status:
                patient_status = patient.menopausal_status
            else:
                patient_status = patient.infer_menopausal_status()
            
            if requires_premenopausal:
                return patient_status == MenopausalStatus.PREMENOPAUSAL
            elif requires_postmenopausal:
                return patient_status == MenopausalStatus.POSTMENOPAUSAL
        
        return True
    
    def _check_exclusion_criteria(self, trial: Trial, patient: PatientData) -> bool:
        """Check if patient meets exclusion criteria (returns False if excluded)"""
        if not trial.eligibility_criteria or not trial.eligibility_criteria.exclusion_criteria:
            return True
        
        exclusion_text = " ".join(trial.eligibility_criteria.exclusion_criteria).lower()
        
        # Check for metastatic disease exclusion
        if patient.cancer_stage and "metastatic" in patient.cancer_stage.lower():
            metastatic_exclusions = [
                "metastatic disease", "evidence of metastatic", "distant metastases",
                "stage iv", "stage 4"
            ]
            if any(exclusion in exclusion_text for exclusion in metastatic_exclusions):
                return False
        
        # Check for medication conflicts
        if patient.medications:
            medication_conflicts = self._check_medication_conflicts(exclusion_text, patient.medications)
            if medication_conflicts:
                return False
        
        # Check for comorbidity exclusions
        if patient.comorbidities:
            comorbidity_conflicts = self._check_comorbidity_conflicts(exclusion_text, patient.comorbidities)
            if comorbidity_conflicts:
                return False
        
        return True
    
    def _check_medication_conflicts(self, exclusion_text: str, medications: List[str]) -> bool:
        """Check for medication conflicts in exclusion criteria"""
        medication_exclusions = [
            "anticoagulant", "blood thinner", "warfarin", "heparin",
            "immunosuppressive", "corticosteroid", "chemotherapy"
        ]
        
        for medication in medications:
            med_lower = medication.lower()
            # Check direct medication name matches
            if med_lower in exclusion_text:
                return True
            # Check category matches
            for exclusion in medication_exclusions:
                if exclusion in exclusion_text and self._medication_in_category(med_lower, exclusion):
                    return True
        
        return False
    
    def _check_comorbidity_conflicts(self, exclusion_text: str, comorbidities: List[str]) -> bool:
        """Check for comorbidity conflicts in exclusion criteria"""
        for comorbidity in comorbidities:
            comorbidity_lower = comorbidity.lower()
            if comorbidity_lower in exclusion_text:
                return True
        
        # Check for specific high-risk conditions
        high_risk_conditions = [
            "cardiac disease", "heart failure", "liver disease", "renal disease",
            "kidney disease", "hepatic", "cardiac"
        ]
        
        for condition in high_risk_conditions:
            if condition in exclusion_text:
                for comorbidity in comorbidities:
                    if self._condition_matches_category(comorbidity.lower(), condition):
                        return True
        
        return False
    
    def _medication_in_category(self, medication: str, category: str) -> bool:
        """Check if medication belongs to excluded category"""
        medication_categories = {
            "anticoagulant": ["warfarin", "heparin", "apixaban", "rivaroxaban"],
            "corticosteroid": ["prednisone", "prednisolone", "dexamethasone"],
            "immunosuppressive": ["methotrexate", "azathioprine", "cyclosporine"]
        }
        
        category_meds = medication_categories.get(category, [])
        return any(med in medication for med in category_meds)
    
    def _condition_matches_category(self, condition: str, category: str) -> bool:
        """Check if condition matches excluded category"""
        condition_categories = {
            "cardiac": ["heart", "cardiac", "cardiovascular"],
            "hepatic": ["liver", "hepatic"],
            "renal": ["kidney", "renal"]
        }
        
        category_terms = condition_categories.get(category, [])
        return any(term in condition for term in category_terms)
    
    def calculate_eligibility_score(self, trial: Trial, patient: PatientData) -> float:
        """Calculate eligibility score (0-1) based on how well patient matches criteria"""
        if not trial.eligibility_criteria:
            return 0.5  # Neutral score when no criteria available
        
        score_components = []
        
        # Age score
        age_score = self._calculate_age_score(trial, patient)
        score_components.append(age_score)
        
        # Gender score
        gender_score = self._calculate_gender_score(trial, patient)
        score_components.append(gender_score)
        
        # Menopausal status score
        menopausal_score = self._calculate_menopausal_score(trial, patient)
        if menopausal_score is not None:
            score_components.append(menopausal_score)
        
        # Overall eligibility
        if not self._is_patient_eligible(trial, patient):
            return 0.0  # Not eligible
        
        return sum(score_components) / len(score_components) if score_components else 0.5
    
    def _calculate_age_score(self, trial: Trial, patient: PatientData) -> float:
        """Calculate age matching score"""
        if not patient.age or not trial.eligibility_criteria:
            return 0.5
        
        criteria = trial.eligibility_criteria
        age = patient.age
        
        # Perfect match if within range
        if ((not criteria.age_min or age >= criteria.age_min) and 
            (not criteria.age_max or age <= criteria.age_max)):
            return 1.0
        
        # Partial score based on how close to acceptable range
        if criteria.age_min and age < criteria.age_min:
            diff = criteria.age_min - age
            return max(0.0, 1.0 - (diff / 10.0))  # Penalty for each year under minimum
        
        if criteria.age_max and age > criteria.age_max:
            diff = age - criteria.age_max
            return max(0.0, 1.0 - (diff / 10.0))  # Penalty for each year over maximum
        
        return 0.5
    
    def _calculate_gender_score(self, trial: Trial, patient: PatientData) -> float:
        """Calculate gender matching score"""
        if not patient.gender or not trial.eligibility_criteria:
            return 0.5
        
        trial_gender = trial.eligibility_criteria.gender
        if trial_gender == "ALL":
            return 1.0
        
        return 1.0 if trial_gender == patient.gender.value else 0.0
    
    def _calculate_menopausal_score(self, trial: Trial, patient: PatientData) -> Optional[float]:
        """Calculate menopausal status matching score"""
        if not trial.eligibility_criteria or not patient.gender or patient.gender.value != "FEMALE":
            return None
        
        inclusion_text = " ".join(trial.eligibility_criteria.inclusion_criteria or []).lower()
        
        premenopausal_keywords = ["premenopausal", "pre-menopausal"]
        postmenopausal_keywords = ["postmenopausal", "post-menopausal"]
        
        requires_premenopausal = any(keyword in inclusion_text for keyword in premenopausal_keywords)
        requires_postmenopausal = any(keyword in inclusion_text for keyword in postmenopausal_keywords)
        
        if not (requires_premenopausal or requires_postmenopausal):
            return None  # No specific requirement
        
        # Infer patient status
        if patient.menopausal_status:
            patient_status = patient.menopausal_status
        else:
            patient_status = patient.infer_menopausal_status()
        
        if requires_premenopausal:
            return 1.0 if patient_status == MenopausalStatus.PREMENOPAUSAL else 0.0
        elif requires_postmenopausal:
            return 1.0 if patient_status == MenopausalStatus.POSTMENOPAUSAL else 0.0
        
        return 0.5