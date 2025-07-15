import pytest
from pydantic import ValidationError
from api.models.patient_data import (
    PatientData, 
    Location, 
    Gender, 
    ConfidenceScores, 
    ExtractionResult
)


class TestGenderEnum:
    """Test Gender enumeration"""
    
    def test_gender_values(self):
        """Test that Gender enum has correct values"""
        assert Gender.MALE == "MALE"
        assert Gender.FEMALE == "FEMALE"
        assert Gender.ALL == "ALL"
    
    def test_gender_validation(self):
        """Test gender validation in PatientData"""
        # Valid genders
        patient = PatientData(gender=Gender.MALE)
        assert patient.gender == Gender.MALE
        
        patient = PatientData(gender="FEMALE")
        assert patient.gender == Gender.FEMALE
        
        # Invalid gender should raise ValidationError
        with pytest.raises(ValidationError):
            PatientData(gender="INVALID")


class TestLocation:
    """Test Location model"""
    
    def test_location_creation_empty(self):
        """Test creating empty location"""
        location = Location()
        assert location.city is None
        assert location.state is None
        assert location.zip_code is None
        assert location.latitude is None
        assert location.longitude is None
    
    def test_location_creation_with_data(self):
        """Test creating location with data"""
        location = Location(
            city="San Francisco",
            state="CA",
            zip_code="94105",
            latitude=37.7749,
            longitude=-122.4194
        )
        assert location.city == "San Francisco"
        assert location.state == "CA"
        assert location.zip_code == "94105"
        assert location.latitude == 37.7749
        assert location.longitude == -122.4194
    
    def test_location_partial_data(self):
        """Test location with partial data"""
        location = Location(city="Boston", state="MA")
        assert location.city == "Boston"
        assert location.state == "MA"
        assert location.zip_code is None
        assert location.latitude is None
        assert location.longitude is None
    
    def test_location_coordinate_validation(self):
        """Test coordinate validation"""
        # Valid coordinates
        location = Location(latitude=40.7128, longitude=-74.0060)
        assert location.latitude == 40.7128
        assert location.longitude == -74.0060
        
        # Invalid coordinates should raise ValidationError
        with pytest.raises(ValidationError):
            Location(latitude="invalid")
        
        with pytest.raises(ValidationError):
            Location(longitude="invalid")


class TestPatientData:
    """Test PatientData model"""
    
    def test_patient_data_empty(self):
        """Test creating empty patient data"""
        patient = PatientData()
        assert patient.age is None
        assert patient.gender is None
        assert patient.conditions == []
        assert patient.primary_diagnosis is None
        assert patient.comorbidities == []
        assert patient.location is None
        assert patient.medications == []
        assert patient.allergies == []
        assert patient.previous_treatments == []
        assert patient.willing_to_travel is None
        assert patient.preferred_distance is None
    
    def test_patient_data_with_demographics(self):
        """Test patient data with demographics"""
        patient = PatientData(
            age=45,
            gender=Gender.FEMALE
        )
        assert patient.age == 45
        assert patient.gender == Gender.FEMALE
    
    def test_patient_data_with_medical_info(self):
        """Test patient data with medical information"""
        patient = PatientData(
            conditions=["Type 2 Diabetes", "Hypertension"],
            primary_diagnosis="Type 2 Diabetes",
            comorbidities=["Obesity"],
            medications=["Metformin", "Lisinopril"],
            allergies=["Penicillin"],
            previous_treatments=["Insulin therapy"]
        )
        assert patient.conditions == ["Type 2 Diabetes", "Hypertension"]
        assert patient.primary_diagnosis == "Type 2 Diabetes"
        assert patient.comorbidities == ["Obesity"]
        assert patient.medications == ["Metformin", "Lisinopril"]
        assert patient.allergies == ["Penicillin"]
        assert patient.previous_treatments == ["Insulin therapy"]
    
    def test_patient_data_with_location(self):
        """Test patient data with location"""
        location = Location(city="New York", state="NY")
        patient = PatientData(location=location)
        assert patient.location.city == "New York"
        assert patient.location.state == "NY"
    
    def test_patient_data_with_preferences(self):
        """Test patient data with trial preferences"""
        patient = PatientData(
            willing_to_travel=True,
            preferred_distance=50
        )
        assert patient.willing_to_travel is True
        assert patient.preferred_distance == 50
    
    def test_patient_data_full_example(self):
        """Test complete patient data example"""
        location = Location(
            city="San Francisco",
            state="CA",
            zip_code="94105"
        )
        
        patient = PatientData(
            age=45,
            gender=Gender.FEMALE,
            conditions=["Type 2 Diabetes", "Hypertension"],
            primary_diagnosis="Type 2 Diabetes",
            comorbidities=["Obesity"],
            location=location,
            medications=["Metformin", "Lisinopril"],
            allergies=["Penicillin"],
            previous_treatments=["Diet modification"],
            willing_to_travel=True,
            preferred_distance=25
        )
        
        assert patient.age == 45
        assert patient.gender == Gender.FEMALE
        assert len(patient.conditions) == 2
        assert patient.primary_diagnosis == "Type 2 Diabetes"
        assert patient.location.city == "San Francisco"
        assert len(patient.medications) == 2
        assert patient.willing_to_travel is True
    
    def test_patient_data_age_validation(self):
        """Test age validation"""
        # Valid ages
        patient = PatientData(age=25)
        assert patient.age == 25
        
        patient = PatientData(age=100)
        assert patient.age == 100
        
        # Negative age is allowed by the model (no constraint defined)
        patient = PatientData(age=-5)
        assert patient.age == -5
        
        # Invalid age should raise ValidationError
        with pytest.raises(ValidationError):
            PatientData(age="invalid")
    
    def test_patient_data_lists_default_empty(self):
        """Test that list fields default to empty lists"""
        patient = PatientData()
        assert isinstance(patient.conditions, list)
        assert isinstance(patient.comorbidities, list)
        assert isinstance(patient.medications, list)
        assert isinstance(patient.allergies, list)
        assert isinstance(patient.previous_treatments, list)
        assert len(patient.conditions) == 0
        assert len(patient.comorbidities) == 0
        assert len(patient.medications) == 0
        assert len(patient.allergies) == 0
        assert len(patient.previous_treatments) == 0


class TestConfidenceScores:
    """Test ConfidenceScores model"""
    
    def test_confidence_scores_defaults(self):
        """Test default confidence scores"""
        scores = ConfidenceScores()
        assert scores.age == 0.0
        assert scores.gender == 0.0
        assert scores.primary_diagnosis == 0.0
        assert scores.conditions == 0.0
        assert scores.medications == 0.0
        assert scores.location == 0.0
        assert scores.overall == 0.0
    
    def test_confidence_scores_with_values(self):
        """Test confidence scores with specific values"""
        scores = ConfidenceScores(
            age=0.9,
            gender=0.95,
            primary_diagnosis=0.8,
            conditions=0.85,
            medications=0.7,
            location=0.6,
            overall=0.8
        )
        assert scores.age == 0.9
        assert scores.gender == 0.95
        assert scores.primary_diagnosis == 0.8
        assert scores.conditions == 0.85
        assert scores.medications == 0.7
        assert scores.location == 0.6
        assert scores.overall == 0.8
    
    def test_confidence_scores_validation(self):
        """Test confidence scores validation"""
        # Valid scores (0.0 to 1.0)
        scores = ConfidenceScores(age=0.5, gender=1.0, overall=0.0)
        assert scores.age == 0.5
        assert scores.gender == 1.0
        assert scores.overall == 0.0
        
        # Test with values outside typical range (should still work as floats)
        scores = ConfidenceScores(age=1.5, gender=-0.1)
        assert scores.age == 1.5
        assert scores.gender == -0.1
        
        # Invalid types should raise ValidationError
        with pytest.raises(ValidationError):
            ConfidenceScores(age="invalid")


class TestExtractionResult:
    """Test ExtractionResult model"""
    
    def test_extraction_result_success(self):
        """Test successful extraction result"""
        patient_data = PatientData(age=45, gender=Gender.FEMALE)
        confidence_scores = ConfidenceScores(age=0.9, gender=0.95, overall=0.85)
        
        result = ExtractionResult(
            patient_data=patient_data,
            confidence_scores=confidence_scores,
            provider_used="openai",
            extraction_time_ms=1500,
            success=True
        )
        
        assert result.patient_data.age == 45
        assert result.patient_data.gender == Gender.FEMALE
        assert result.confidence_scores.age == 0.9
        assert result.provider_used == "openai"
        assert result.extraction_time_ms == 1500
        assert result.success is True
        assert result.error_message is None
    
    def test_extraction_result_failure(self):
        """Test failed extraction result"""
        patient_data = PatientData()
        confidence_scores = ConfidenceScores()
        
        result = ExtractionResult(
            patient_data=patient_data,
            confidence_scores=confidence_scores,
            provider_used="anthropic",
            extraction_time_ms=500,
            success=False,
            error_message="API rate limit exceeded"
        )
        
        assert result.success is False
        assert result.error_message == "API rate limit exceeded"
        assert result.provider_used == "anthropic"
        assert result.extraction_time_ms == 500
    
    def test_extraction_result_default_success(self):
        """Test that success defaults to True"""
        patient_data = PatientData()
        confidence_scores = ConfidenceScores()
        
        result = ExtractionResult(
            patient_data=patient_data,
            confidence_scores=confidence_scores,
            provider_used="openai",
            extraction_time_ms=1000
        )
        
        assert result.success is True
        assert result.error_message is None
    
    def test_extraction_result_validation(self):
        """Test extraction result validation"""
        patient_data = PatientData()
        confidence_scores = ConfidenceScores()
        
        # Valid extraction time
        result = ExtractionResult(
            patient_data=patient_data,
            confidence_scores=confidence_scores,
            provider_used="openai",
            extraction_time_ms=1000
        )
        assert result.extraction_time_ms == 1000
        
        # Invalid extraction time should raise ValidationError
        with pytest.raises(ValidationError):
            ExtractionResult(
                patient_data=patient_data,
                confidence_scores=confidence_scores,
                provider_used="openai",
                extraction_time_ms="invalid"
            )
    
    def test_extraction_result_serialization(self):
        """Test extraction result can be serialized to dict"""
        location = Location(city="Boston", state="MA")
        patient_data = PatientData(
            age=30,
            gender=Gender.MALE,
            conditions=["Asthma"],
            location=location
        )
        confidence_scores = ConfidenceScores(age=0.8, gender=0.9, overall=0.75)
        
        result = ExtractionResult(
            patient_data=patient_data,
            confidence_scores=confidence_scores,
            provider_used="openai",
            extraction_time_ms=1200
        )
        
        result_dict = result.model_dump()
        
        assert result_dict['patient_data']['age'] == 30
        assert result_dict['patient_data']['gender'] == 'MALE'
        assert result_dict['confidence_scores']['age'] == 0.8
        assert result_dict['provider_used'] == 'openai'
        assert result_dict['success'] is True