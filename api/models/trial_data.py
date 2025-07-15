from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class TrialStatus(str, Enum):
    RECRUITING = "RECRUITING"
    NOT_YET_RECRUITING = "NOT_YET_RECRUITING"
    ENROLLING_BY_INVITATION = "ENROLLING_BY_INVITATION"
    ACTIVE_NOT_RECRUITING = "ACTIVE_NOT_RECRUITING"
    COMPLETED = "COMPLETED"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    WITHDRAWN = "WITHDRAWN"

class TrialPhase(str, Enum):
    EARLY_PHASE_1 = "EARLY_PHASE_1"
    PHASE_1 = "PHASE_1"
    PHASE_2 = "PHASE_2"
    PHASE_3 = "PHASE_3"
    PHASE_4 = "PHASE_4"
    NOT_APPLICABLE = "NOT_APPLICABLE"

class ContactInfo(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class TrialLocation(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    facility: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class EligibilityCriteria(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    gender: Optional[str] = None
    healthy_volunteers: Optional[bool] = None
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)

class Trial(BaseModel):
    nct_id: str
    title: str
    status: TrialStatus
    phase: Optional[TrialPhase] = None
    brief_summary: Optional[str] = None
    detailed_description: Optional[str] = None
    
    # Location and contact
    locations: List[TrialLocation] = Field(default_factory=list)
    contact_info: Optional[ContactInfo] = None
    
    # Eligibility
    eligibility_criteria: Optional[EligibilityCriteria] = None
    
    # Study details
    study_type: Optional[str] = None
    primary_outcome: Optional[str] = None
    secondary_outcomes: List[str] = Field(default_factory=list)
    enrollment_target: Optional[int] = None
    estimated_completion: Optional[str] = None
    sponsor: Optional[str] = None
    
    # Computed fields
    distance_miles: Optional[float] = None
    match_score: Optional[float] = None

class RankedTrial(BaseModel):
    trial: Trial
    match_score: float
    match_factors: Dict[str, float]
    reasoning: Optional[str] = None

class TrialSearchResult(BaseModel):
    trials: List[RankedTrial]
    total_found: int
    search_metadata: Dict
    success: bool = True
    error_message: Optional[str] = None