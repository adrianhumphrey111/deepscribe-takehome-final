from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    ALL = "ALL"

class MenopausalStatus(str, Enum):
    PREMENOPAUSAL = "PREMENOPAUSAL"
    POSTMENOPAUSAL = "POSTMENOPAUSAL"
    PERIMENOPAUSAL = "PERIMENOPAUSAL"
    UNKNOWN = "UNKNOWN"

class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PatientData(BaseModel):
    # Demographics
    age: Optional[int] = None
    gender: Optional[Gender] = None
    menopausal_status: Optional[MenopausalStatus] = None
    
    # Medical Information
    conditions: List[str] = Field(default_factory=list)
    primary_diagnosis: Optional[str] = None
    comorbidities: List[str] = Field(default_factory=list)
    
    # Cancer-specific information
    cancer_stage: Optional[str] = None
    tumor_markers: Optional[Dict[str, Optional[str]]] = Field(default_factory=dict)  # e.g., {"ER": "positive", "HER2": "negative"}
    tumor_size: Optional[str] = None
    
    # Location
    location: Optional[Location] = None
    
    # Eligibility Factors
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    previous_treatments: List[str] = Field(default_factory=list)
    
    # Trial Preferences
    willing_to_travel: Optional[bool] = None
    preferred_distance: Optional[int] = None
    
    def infer_menopausal_status(self) -> MenopausalStatus:
        """Infer menopausal status based on age and gender"""
        if self.menopausal_status and self.menopausal_status != MenopausalStatus.UNKNOWN:
            return self.menopausal_status
        
        if self.gender == Gender.MALE:
            return MenopausalStatus.UNKNOWN
        
        if self.age:
            if self.age < 45:
                return MenopausalStatus.PREMENOPAUSAL
            elif self.age >= 55:
                return MenopausalStatus.POSTMENOPAUSAL
            else:
                return MenopausalStatus.PERIMENOPAUSAL
        
        return MenopausalStatus.UNKNOWN

class ConfidenceScores(BaseModel):
    age: float = 0.0
    gender: float = 0.0
    primary_diagnosis: float = 0.0
    conditions: float = 0.0
    medications: float = 0.0
    location: float = 0.0
    overall: float = 0.0

class ExtractionResult(BaseModel):
    patient_data: PatientData
    confidence_scores: ConfidenceScores
    provider_used: str
    extraction_time_ms: int
    success: bool = True
    error_message: Optional[str] = None