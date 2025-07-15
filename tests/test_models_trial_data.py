import pytest
from pydantic import ValidationError
from api.models.trial_data import (
    Trial,
    TrialStatus,
    TrialPhase,
    ContactInfo,
    TrialLocation,
    EligibilityCriteria,
    RankedTrial,
    TrialSearchResult
)


class TestTrialStatus:
    """Test TrialStatus enumeration"""
    
    def test_trial_status_values(self):
        """Test that TrialStatus enum has correct values"""
        assert TrialStatus.RECRUITING == "RECRUITING"
        assert TrialStatus.NOT_YET_RECRUITING == "NOT_YET_RECRUITING"
        assert TrialStatus.ACTIVE_NOT_RECRUITING == "ACTIVE_NOT_RECRUITING"
        assert TrialStatus.COMPLETED == "COMPLETED"
        assert TrialStatus.SUSPENDED == "SUSPENDED"
        assert TrialStatus.TERMINATED == "TERMINATED"
        assert TrialStatus.WITHDRAWN == "WITHDRAWN"
    
    def test_trial_status_validation(self):
        """Test trial status validation"""
        # Valid status
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING
        )
        assert trial.status == TrialStatus.RECRUITING
        
        # Invalid status should raise ValidationError
        with pytest.raises(ValidationError):
            Trial(
                nct_id="NCT12345678",
                title="Test Trial",
                status="INVALID_STATUS"
            )


class TestTrialPhase:
    """Test TrialPhase enumeration"""
    
    def test_trial_phase_values(self):
        """Test that TrialPhase enum has correct values"""
        assert TrialPhase.EARLY_PHASE_1 == "EARLY_PHASE_1"
        assert TrialPhase.PHASE_1 == "PHASE_1"
        assert TrialPhase.PHASE_2 == "PHASE_2"
        assert TrialPhase.PHASE_3 == "PHASE_3"
        assert TrialPhase.PHASE_4 == "PHASE_4"
        assert TrialPhase.NOT_APPLICABLE == "NOT_APPLICABLE"
    
    def test_trial_phase_validation(self):
        """Test trial phase validation"""
        # Valid phase
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            phase=TrialPhase.PHASE_2
        )
        assert trial.phase == TrialPhase.PHASE_2
        
        # Invalid phase should raise ValidationError
        with pytest.raises(ValidationError):
            Trial(
                nct_id="NCT12345678",
                title="Test Trial",
                status=TrialStatus.RECRUITING,
                phase="INVALID_PHASE"
            )


class TestContactInfo:
    """Test ContactInfo model"""
    
    def test_contact_info_empty(self):
        """Test creating empty contact info"""
        contact = ContactInfo()
        assert contact.name is None
        assert contact.phone is None
        assert contact.email is None
    
    def test_contact_info_with_data(self):
        """Test creating contact info with data"""
        contact = ContactInfo(
            name="Dr. Smith",
            phone="555-123-4567",
            email="dr.smith@hospital.com"
        )
        assert contact.name == "Dr. Smith"
        assert contact.phone == "555-123-4567"
        assert contact.email == "dr.smith@hospital.com"
    
    def test_contact_info_partial(self):
        """Test contact info with partial data"""
        contact = ContactInfo(name="Dr. Johnson", email="dr.johnson@clinic.org")
        assert contact.name == "Dr. Johnson"
        assert contact.phone is None
        assert contact.email == "dr.johnson@clinic.org"


class TestTrialLocation:
    """Test TrialLocation model"""
    
    def test_trial_location_empty(self):
        """Test creating empty trial location"""
        location = TrialLocation()
        assert location.city is None
        assert location.state is None
        assert location.country is None
        assert location.facility is None
        assert location.latitude is None
        assert location.longitude is None
    
    def test_trial_location_with_data(self):
        """Test creating trial location with data"""
        location = TrialLocation(
            city="Boston",
            state="MA",
            country="United States",
            facility="Massachusetts General Hospital",
            latitude=42.3601,
            longitude=-71.0589
        )
        assert location.city == "Boston"
        assert location.state == "MA"
        assert location.country == "United States"
        assert location.facility == "Massachusetts General Hospital"
        assert location.latitude == 42.3601
        assert location.longitude == -71.0589
    
    def test_trial_location_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        location = TrialLocation(latitude=40.7128, longitude=-74.0060)
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060
        
        # Invalid coordinates should raise ValidationError
        with pytest.raises(ValidationError):
            TrialLocation(latitude="invalid")
        
        with pytest.raises(ValidationError):
            TrialLocation(longitude="invalid")


class TestEligibilityCriteria:
    """Test EligibilityCriteria model"""
    
    def test_eligibility_criteria_empty(self):
        """Test creating empty eligibility criteria"""
        criteria = EligibilityCriteria()
        assert criteria.age_min is None
        assert criteria.age_max is None
        assert criteria.gender is None
        assert criteria.healthy_volunteers is None
        assert criteria.inclusion_criteria == []
        assert criteria.exclusion_criteria == []
    
    def test_eligibility_criteria_with_data(self):
        """Test creating eligibility criteria with data"""
        criteria = EligibilityCriteria(
            age_min=18,
            age_max=65,
            gender="All",
            healthy_volunteers=False,
            inclusion_criteria=["Type 2 diabetes diagnosis", "HbA1c > 7%"],
            exclusion_criteria=["Pregnancy", "Severe kidney disease"]
        )
        assert criteria.age_min == 18
        assert criteria.age_max == 65
        assert criteria.gender == "All"
        assert criteria.healthy_volunteers is False
        assert len(criteria.inclusion_criteria) == 2
        assert len(criteria.exclusion_criteria) == 2
        assert "Type 2 diabetes diagnosis" in criteria.inclusion_criteria
        assert "Pregnancy" in criteria.exclusion_criteria
    
    def test_eligibility_criteria_age_validation(self):
        """Test age validation"""
        # Valid ages
        criteria = EligibilityCriteria(age_min=18, age_max=65)
        assert criteria.age_min == 18
        assert criteria.age_max == 65
        
        # Invalid ages should raise ValidationError
        with pytest.raises(ValidationError):
            EligibilityCriteria(age_min="invalid")
        
        with pytest.raises(ValidationError):
            EligibilityCriteria(age_max="invalid")
    
    def test_eligibility_criteria_lists_default_empty(self):
        """Test that list fields default to empty lists"""
        criteria = EligibilityCriteria()
        assert isinstance(criteria.inclusion_criteria, list)
        assert isinstance(criteria.exclusion_criteria, list)
        assert len(criteria.inclusion_criteria) == 0
        assert len(criteria.exclusion_criteria) == 0


class TestTrial:
    """Test Trial model"""
    
    def test_trial_minimal(self):
        """Test creating trial with minimal required fields"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Diabetes Trial",
            status=TrialStatus.RECRUITING
        )
        assert trial.nct_id == "NCT12345678"
        assert trial.title == "Test Diabetes Trial"
        assert trial.status == TrialStatus.RECRUITING
        assert trial.phase is None
        assert trial.brief_summary is None
        assert trial.locations == []
        assert trial.contact_info is None
        assert trial.eligibility_criteria is None
    
    def test_trial_with_phase(self):
        """Test trial with phase"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            phase=TrialPhase.PHASE_2
        )
        assert trial.phase == TrialPhase.PHASE_2
    
    def test_trial_with_descriptions(self):
        """Test trial with descriptions"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            brief_summary="This is a brief summary",
            detailed_description="This is a detailed description of the trial"
        )
        assert trial.brief_summary == "This is a brief summary"
        assert trial.detailed_description == "This is a detailed description of the trial"
    
    def test_trial_with_locations(self):
        """Test trial with locations"""
        location1 = TrialLocation(city="Boston", state="MA", facility="MGH")
        location2 = TrialLocation(city="New York", state="NY", facility="NYU")
        
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            locations=[location1, location2]
        )
        assert len(trial.locations) == 2
        assert trial.locations[0].city == "Boston"
        assert trial.locations[1].city == "New York"
    
    def test_trial_with_contact_info(self):
        """Test trial with contact info"""
        contact = ContactInfo(name="Dr. Smith", phone="555-123-4567")
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            contact_info=contact
        )
        assert trial.contact_info.name == "Dr. Smith"
        assert trial.contact_info.phone == "555-123-4567"
    
    def test_trial_with_eligibility(self):
        """Test trial with eligibility criteria"""
        criteria = EligibilityCriteria(
            age_min=18,
            age_max=65,
            gender="All",
            inclusion_criteria=["Type 2 diabetes"]
        )
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            eligibility_criteria=criteria
        )
        assert trial.eligibility_criteria.age_min == 18
        assert trial.eligibility_criteria.age_max == 65
        assert trial.eligibility_criteria.gender == "All"
    
    def test_trial_with_study_details(self):
        """Test trial with study details"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            study_type="Interventional",
            primary_outcome="Change in HbA1c",
            secondary_outcomes=["Safety", "Quality of life"],
            enrollment_target=100,
            estimated_completion="2024-12-31",
            sponsor="Pharmaceutical Company"
        )
        assert trial.study_type == "Interventional"
        assert trial.primary_outcome == "Change in HbA1c"
        assert len(trial.secondary_outcomes) == 2
        assert trial.enrollment_target == 100
        assert trial.estimated_completion == "2024-12-31"
        assert trial.sponsor == "Pharmaceutical Company"
    
    def test_trial_with_computed_fields(self):
        """Test trial with computed fields"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING,
            distance_miles=25.5,
            match_score=0.85
        )
        assert trial.distance_miles == 25.5
        assert trial.match_score == 0.85
    
    def test_trial_nct_id_required(self):
        """Test that NCT ID is required"""
        with pytest.raises(ValidationError):
            Trial(title="Test Trial", status=TrialStatus.RECRUITING)
    
    def test_trial_title_required(self):
        """Test that title is required"""
        with pytest.raises(ValidationError):
            Trial(nct_id="NCT12345678", status=TrialStatus.RECRUITING)
    
    def test_trial_status_required(self):
        """Test that status is required"""
        with pytest.raises(ValidationError):
            Trial(nct_id="NCT12345678", title="Test Trial")
    
    def test_trial_full_example(self):
        """Test complete trial example"""
        location = TrialLocation(
            city="San Francisco",
            state="CA",
            country="United States",
            facility="UCSF Medical Center"
        )
        contact = ContactInfo(
            name="Dr. Jane Doe",
            phone="555-987-6543",
            email="jane.doe@ucsf.edu"
        )
        criteria = EligibilityCriteria(
            age_min=21,
            age_max=70,
            gender="All",
            healthy_volunteers=False,
            inclusion_criteria=["Type 2 diabetes", "HbA1c >= 7%"],
            exclusion_criteria=["Pregnancy", "Severe complications"]
        )
        
        trial = Trial(
            nct_id="NCT12345678",
            title="Novel Diabetes Treatment Study",
            status=TrialStatus.RECRUITING,
            phase=TrialPhase.PHASE_3,
            brief_summary="A study of a new diabetes medication",
            detailed_description="Detailed description of the study protocol",
            locations=[location],
            contact_info=contact,
            eligibility_criteria=criteria,
            study_type="Interventional",
            primary_outcome="Change in HbA1c from baseline",
            secondary_outcomes=["Safety endpoints", "Quality of life"],
            enrollment_target=500,
            estimated_completion="2025-06-30",
            sponsor="Big Pharma Inc",
            distance_miles=15.2,
            match_score=0.92
        )
        
        assert trial.nct_id == "NCT12345678"
        assert trial.title == "Novel Diabetes Treatment Study"
        assert trial.status == TrialStatus.RECRUITING
        assert trial.phase == TrialPhase.PHASE_3
        assert len(trial.locations) == 1
        assert trial.locations[0].city == "San Francisco"
        assert trial.contact_info.name == "Dr. Jane Doe"
        assert trial.eligibility_criteria.age_min == 21
        assert trial.enrollment_target == 500
        assert trial.match_score == 0.92


class TestRankedTrial:
    """Test RankedTrial model"""
    
    def test_ranked_trial_creation(self):
        """Test creating ranked trial"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING
        )
        
        ranked_trial = RankedTrial(
            trial=trial,
            match_score=0.85,
            match_factors={"age": 0.9, "location": 0.8, "condition": 0.95},
            reasoning="Good match based on age and condition"
        )
        
        assert ranked_trial.trial.nct_id == "NCT12345678"
        assert ranked_trial.match_score == 0.85
        assert ranked_trial.match_factors["age"] == 0.9
        assert ranked_trial.match_factors["location"] == 0.8
        assert ranked_trial.match_factors["condition"] == 0.95
        assert ranked_trial.reasoning == "Good match based on age and condition"
    
    def test_ranked_trial_without_reasoning(self):
        """Test ranked trial without reasoning"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING
        )
        
        ranked_trial = RankedTrial(
            trial=trial,
            match_score=0.75,
            match_factors={"age": 0.8, "location": 0.7}
        )
        
        assert ranked_trial.reasoning is None
        assert ranked_trial.match_score == 0.75
    
    def test_ranked_trial_validation(self):
        """Test ranked trial validation"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING
        )
        
        # Valid match score
        ranked_trial = RankedTrial(
            trial=trial,
            match_score=0.5,
            match_factors={}
        )
        assert ranked_trial.match_score == 0.5
        
        # Invalid match score should raise ValidationError
        with pytest.raises(ValidationError):
            RankedTrial(
                trial=trial,
                match_score="invalid",
                match_factors={}
            )
    
    def test_ranked_trial_match_factors_dict(self):
        """Test match factors as dictionary"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING
        )
        
        match_factors = {
            "age_match": 0.9,
            "location_match": 0.7,
            "condition_match": 0.95,
            "eligibility_match": 0.8
        }
        
        ranked_trial = RankedTrial(
            trial=trial,
            match_score=0.85,
            match_factors=match_factors
        )
        
        assert len(ranked_trial.match_factors) == 4
        assert ranked_trial.match_factors["age_match"] == 0.9
        assert ranked_trial.match_factors["condition_match"] == 0.95


class TestTrialSearchResult:
    """Test TrialSearchResult model"""
    
    def test_trial_search_result_success(self):
        """Test successful trial search result"""
        trial = Trial(
            nct_id="NCT12345678",
            title="Test Trial",
            status=TrialStatus.RECRUITING
        )
        
        ranked_trial = RankedTrial(
            trial=trial,
            match_score=0.85,
            match_factors={"age": 0.9}
        )
        
        search_result = TrialSearchResult(
            trials=[ranked_trial],
            total_found=1,
            search_metadata={"query_time_ms": 500, "provider": "clinicaltrials.gov"},
            success=True
        )
        
        assert len(search_result.trials) == 1
        assert search_result.trials[0].trial.nct_id == "NCT12345678"
        assert search_result.total_found == 1
        assert search_result.search_metadata["query_time_ms"] == 500
        assert search_result.success is True
        assert search_result.error_message is None
    
    def test_trial_search_result_failure(self):
        """Test failed trial search result"""
        search_result = TrialSearchResult(
            trials=[],
            total_found=0,
            search_metadata={"query_time_ms": 1000},
            success=False,
            error_message="API connection failed"
        )
        
        assert len(search_result.trials) == 0
        assert search_result.total_found == 0
        assert search_result.success is False
        assert search_result.error_message == "API connection failed"
    
    def test_trial_search_result_default_success(self):
        """Test that success defaults to True"""
        search_result = TrialSearchResult(
            trials=[],
            total_found=0,
            search_metadata={}
        )
        
        assert search_result.success is True
        assert search_result.error_message is None
    
    def test_trial_search_result_multiple_trials(self):
        """Test search result with multiple trials"""
        trial1 = Trial(
            nct_id="NCT12345678",
            title="Test Trial 1",
            status=TrialStatus.RECRUITING
        )
        
        trial2 = Trial(
            nct_id="NCT87654321",
            title="Test Trial 2",
            status=TrialStatus.ACTIVE_NOT_RECRUITING
        )
        
        ranked_trial1 = RankedTrial(
            trial=trial1,
            match_score=0.9,
            match_factors={"age": 0.95}
        )
        
        ranked_trial2 = RankedTrial(
            trial=trial2,
            match_score=0.7,
            match_factors={"age": 0.8}
        )
        
        search_result = TrialSearchResult(
            trials=[ranked_trial1, ranked_trial2],
            total_found=2,
            search_metadata={"query_time_ms": 750}
        )
        
        assert len(search_result.trials) == 2
        assert search_result.total_found == 2
        assert search_result.trials[0].match_score == 0.9
        assert search_result.trials[1].match_score == 0.7
    
    def test_trial_search_result_validation(self):
        """Test trial search result validation"""
        # Valid total_found
        search_result = TrialSearchResult(
            trials=[],
            total_found=0,
            search_metadata={}
        )
        assert search_result.total_found == 0
        
        # Invalid total_found should raise ValidationError
        with pytest.raises(ValidationError):
            TrialSearchResult(
                trials=[],
                total_found="invalid",
                search_metadata={}
            )