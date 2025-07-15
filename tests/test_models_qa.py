import pytest
from pydantic import ValidationError
from api.models.qa_models import QARequest, QAResponse, QASession


class TestQARequest:
    """Test QARequest model"""
    
    def test_qa_request_minimal(self):
        """Test creating QA request with minimal required fields"""
        qa_request = QARequest(
            trial_id="NCT12345678",
            question="What are the eligibility criteria for this trial?"
        )
        assert qa_request.trial_id == "NCT12345678"
        assert qa_request.question == "What are the eligibility criteria for this trial?"
        assert qa_request.patient_context is None
    
    def test_qa_request_with_patient_context(self):
        """Test QA request with patient context"""
        patient_context = {
            "age": 45,
            "gender": "female",
            "conditions": ["Type 2 Diabetes", "Hypertension"],
            "location": {"city": "San Francisco", "state": "CA"}
        }
        
        qa_request = QARequest(
            trial_id="NCT12345678",
            question="Am I eligible for this trial?",
            patient_context=patient_context
        )
        
        assert qa_request.trial_id == "NCT12345678"
        assert qa_request.question == "Am I eligible for this trial?"
        assert qa_request.patient_context == patient_context
        assert qa_request.patient_context["age"] == 45
        assert qa_request.patient_context["gender"] == "female"
        assert len(qa_request.patient_context["conditions"]) == 2
    
    def test_qa_request_trial_id_required(self):
        """Test that trial_id is required"""
        with pytest.raises(ValidationError):
            QARequest(question="What are the side effects?")
    
    def test_qa_request_question_required(self):
        """Test that question is required"""
        with pytest.raises(ValidationError):
            QARequest(trial_id="NCT12345678")
    
    def test_qa_request_empty_strings(self):
        """Test QA request with empty strings"""
        qa_request = QARequest(
            trial_id="NCT12345678",
            question=""
        )
        assert qa_request.trial_id == "NCT12345678"
        assert qa_request.question == ""
    
    def test_qa_request_complex_patient_context(self):
        """Test QA request with complex patient context"""
        patient_context = {
            "demographics": {
                "age": 55,
                "gender": "male",
                "location": {"city": "Boston", "state": "MA", "zip": "02101"}
            },
            "medical_history": {
                "conditions": ["Diabetes", "Heart Disease"],
                "medications": ["Metformin", "Aspirin"],
                "allergies": ["Penicillin"]
            },
            "preferences": {
                "willing_to_travel": True,
                "max_distance_miles": 50
            }
        }
        
        qa_request = QARequest(
            trial_id="NCT87654321",
            question="What is the time commitment for this trial?",
            patient_context=patient_context
        )
        
        assert qa_request.patient_context["demographics"]["age"] == 55
        assert qa_request.patient_context["medical_history"]["conditions"] == ["Diabetes", "Heart Disease"]
        assert qa_request.patient_context["preferences"]["willing_to_travel"] is True
    
    def test_qa_request_serialization(self):
        """Test QA request serialization"""
        patient_context = {"age": 30, "condition": "Asthma"}
        
        qa_request = QARequest(
            trial_id="NCT11111111",
            question="How long is the treatment period?",
            patient_context=patient_context
        )
        
        request_dict = qa_request.model_dump()
        
        assert request_dict["trial_id"] == "NCT11111111"
        assert request_dict["question"] == "How long is the treatment period?"
        assert request_dict["patient_context"]["age"] == 30
        assert request_dict["patient_context"]["condition"] == "Asthma"


class TestQAResponse:
    """Test QAResponse model"""
    
    def test_qa_response_success(self):
        """Test successful QA response"""
        qa_response = QAResponse(
            answer="The trial is for patients aged 18-65 with Type 2 diabetes.",
            confidence=0.9,
            sources=["Protocol document", "Eligibility criteria"],
            response_time_ms=1500,
            success=True
        )
        
        assert qa_response.answer == "The trial is for patients aged 18-65 with Type 2 diabetes."
        assert qa_response.confidence == 0.9
        assert qa_response.sources == ["Protocol document", "Eligibility criteria"]
        assert qa_response.response_time_ms == 1500
        assert qa_response.success is True
        assert qa_response.error_message is None
    
    def test_qa_response_failure(self):
        """Test failed QA response"""
        qa_response = QAResponse(
            answer="",
            confidence=0.0,
            sources=[],
            response_time_ms=500,
            success=False,
            error_message="Unable to process question"
        )
        
        assert qa_response.answer == ""
        assert qa_response.confidence == 0.0
        assert qa_response.sources == []
        assert qa_response.response_time_ms == 500
        assert qa_response.success is False
        assert qa_response.error_message == "Unable to process question"
    
    def test_qa_response_default_success(self):
        """Test that success defaults to True"""
        qa_response = QAResponse(
            answer="The trial runs for 6 months.",
            confidence=0.8,
            sources=["Study protocol"],
            response_time_ms=1000
        )
        
        assert qa_response.success is True
        assert qa_response.error_message is None
    
    def test_qa_response_multiple_sources(self):
        """Test QA response with multiple sources"""
        sources = [
            "Protocol document section 3.2",
            "Inclusion criteria list",
            "Principal investigator notes",
            "FDA approval documentation"
        ]
        
        qa_response = QAResponse(
            answer="Based on multiple sources, the eligibility criteria include...",
            confidence=0.95,
            sources=sources,
            response_time_ms=2000
        )
        
        assert len(qa_response.sources) == 4
        assert "Protocol document section 3.2" in qa_response.sources
        assert "FDA approval documentation" in qa_response.sources
    
    def test_qa_response_empty_sources(self):
        """Test QA response with empty sources"""
        qa_response = QAResponse(
            answer="General information about the trial.",
            confidence=0.5,
            sources=[],
            response_time_ms=800
        )
        
        assert qa_response.sources == []
        assert len(qa_response.sources) == 0
    
    def test_qa_response_confidence_validation(self):
        """Test confidence validation"""
        # Valid confidence values
        qa_response = QAResponse(
            answer="Test answer",
            confidence=0.0,
            sources=["Test source"],
            response_time_ms=1000
        )
        assert qa_response.confidence == 0.0
        
        qa_response = QAResponse(
            answer="Test answer",
            confidence=1.0,
            sources=["Test source"],
            response_time_ms=1000
        )
        assert qa_response.confidence == 1.0
        
        # Confidence outside typical range (should still work as float)
        qa_response = QAResponse(
            answer="Test answer",
            confidence=1.5,
            sources=["Test source"],
            response_time_ms=1000
        )
        assert qa_response.confidence == 1.5
        
        # Invalid confidence should raise ValidationError
        with pytest.raises(ValidationError):
            QAResponse(
                answer="Test answer",
                confidence="invalid",
                sources=["Test source"],
                response_time_ms=1000
            )
    
    def test_qa_response_response_time_validation(self):
        """Test response time validation"""
        # Valid response time
        qa_response = QAResponse(
            answer="Test answer",
            confidence=0.8,
            sources=["Test source"],
            response_time_ms=1500
        )
        assert qa_response.response_time_ms == 1500
        
        # Invalid response time should raise ValidationError
        with pytest.raises(ValidationError):
            QAResponse(
                answer="Test answer",
                confidence=0.8,
                sources=["Test source"],
                response_time_ms="invalid"
            )
    
    def test_qa_response_required_fields(self):
        """Test that required fields are validated"""
        # Missing answer
        with pytest.raises(ValidationError):
            QAResponse(
                confidence=0.8,
                sources=["Test source"],
                response_time_ms=1000
            )
        
        # Missing confidence
        with pytest.raises(ValidationError):
            QAResponse(
                answer="Test answer",
                sources=["Test source"],
                response_time_ms=1000
            )
        
        # Missing sources
        with pytest.raises(ValidationError):
            QAResponse(
                answer="Test answer",
                confidence=0.8,
                response_time_ms=1000
            )
        
        # Missing response_time_ms
        with pytest.raises(ValidationError):
            QAResponse(
                answer="Test answer",
                confidence=0.8,
                sources=["Test source"]
            )
    
    def test_qa_response_serialization(self):
        """Test QA response serialization"""
        qa_response = QAResponse(
            answer="This trial is for adults with diabetes.",
            confidence=0.88,
            sources=["Protocol", "Eligibility docs"],
            response_time_ms=1200,
            success=True
        )
        
        response_dict = qa_response.model_dump()
        
        assert response_dict["answer"] == "This trial is for adults with diabetes."
        assert response_dict["confidence"] == 0.88
        assert response_dict["sources"] == ["Protocol", "Eligibility docs"]
        assert response_dict["response_time_ms"] == 1200
        assert response_dict["success"] is True
        assert response_dict["error_message"] is None


class TestQASession:
    """Test QASession model"""
    
    def test_qa_session_creation(self):
        """Test creating QA session"""
        conversation_history = [
            {"role": "user", "content": "What are the eligibility criteria?"},
            {"role": "assistant", "content": "You must be 18-65 years old with Type 2 diabetes."}
        ]
        
        qa_session = QASession(
            session_id="session_12345",
            trial_id="NCT12345678",
            conversation_history=conversation_history,
            created_at="2024-01-15T10:30:00Z"
        )
        
        assert qa_session.session_id == "session_12345"
        assert qa_session.trial_id == "NCT12345678"
        assert len(qa_session.conversation_history) == 2
        assert qa_session.conversation_history[0]["role"] == "user"
        assert qa_session.conversation_history[1]["role"] == "assistant"
        assert qa_session.created_at == "2024-01-15T10:30:00Z"
    
    def test_qa_session_empty_history(self):
        """Test QA session with empty conversation history"""
        qa_session = QASession(
            session_id="session_empty",
            trial_id="NCT87654321",
            conversation_history=[],
            created_at="2024-01-15T11:00:00Z"
        )
        
        assert qa_session.session_id == "session_empty"
        assert qa_session.trial_id == "NCT87654321"
        assert qa_session.conversation_history == []
        assert len(qa_session.conversation_history) == 0
        assert qa_session.created_at == "2024-01-15T11:00:00Z"
    
    def test_qa_session_long_conversation(self):
        """Test QA session with long conversation history"""
        conversation_history = []
        for i in range(10):
            conversation_history.append({
                "role": "user",
                "content": f"Question {i + 1}",
                "timestamp": f"2024-01-15T10:{30 + i}:00Z"
            })
            conversation_history.append({
                "role": "assistant",
                "content": f"Answer {i + 1}",
                "timestamp": f"2024-01-15T10:{30 + i}:30Z"
            })
        
        qa_session = QASession(
            session_id="session_long",
            trial_id="NCT11111111",
            conversation_history=conversation_history,
            created_at="2024-01-15T10:30:00Z"
        )
        
        assert len(qa_session.conversation_history) == 20
        assert qa_session.conversation_history[0]["content"] == "Question 1"
        assert qa_session.conversation_history[1]["content"] == "Answer 1"
        assert qa_session.conversation_history[-2]["content"] == "Question 10"
        assert qa_session.conversation_history[-1]["content"] == "Answer 10"
    
    def test_qa_session_complex_conversation(self):
        """Test QA session with complex conversation entries"""
        conversation_history = [
            {
                "role": "user",
                "content": "What are the side effects?",
                "timestamp": "2024-01-15T10:30:00Z",
                "metadata": {"source": "web_interface"}
            },
            {
                "role": "assistant",
                "content": "Common side effects include nausea and headache.",
                "timestamp": "2024-01-15T10:30:15Z",
                "confidence": 0.85,
                "sources": ["Protocol section 4.3", "Safety data"],
                "metadata": {"response_time_ms": 1200}
            },
            {
                "role": "user",
                "content": "How severe are these side effects?",
                "timestamp": "2024-01-15T10:31:00Z",
                "metadata": {"source": "web_interface"}
            }
        ]
        
        qa_session = QASession(
            session_id="session_complex",
            trial_id="NCT22222222",
            conversation_history=conversation_history,
            created_at="2024-01-15T10:30:00Z"
        )
        
        assert len(qa_session.conversation_history) == 3
        assert qa_session.conversation_history[1]["confidence"] == 0.85
        assert qa_session.conversation_history[1]["sources"] == ["Protocol section 4.3", "Safety data"]
        assert qa_session.conversation_history[2]["content"] == "How severe are these side effects?"
    
    def test_qa_session_required_fields(self):
        """Test that required fields are validated"""
        # Missing session_id
        with pytest.raises(ValidationError):
            QASession(
                trial_id="NCT12345678",
                conversation_history=[],
                created_at="2024-01-15T10:30:00Z"
            )
        
        # Missing trial_id
        with pytest.raises(ValidationError):
            QASession(
                session_id="session_12345",
                conversation_history=[],
                created_at="2024-01-15T10:30:00Z"
            )
        
        # Missing conversation_history
        with pytest.raises(ValidationError):
            QASession(
                session_id="session_12345",
                trial_id="NCT12345678",
                created_at="2024-01-15T10:30:00Z"
            )
        
        # Missing created_at
        with pytest.raises(ValidationError):
            QASession(
                session_id="session_12345",
                trial_id="NCT12345678",
                conversation_history=[]
            )
    
    def test_qa_session_serialization(self):
        """Test QA session serialization"""
        conversation_history = [
            {"role": "user", "content": "Test question"},
            {"role": "assistant", "content": "Test answer"}
        ]
        
        qa_session = QASession(
            session_id="session_serialize",
            trial_id="NCT33333333",
            conversation_history=conversation_history,
            created_at="2024-01-15T12:00:00Z"
        )
        
        session_dict = qa_session.model_dump()
        
        assert session_dict["session_id"] == "session_serialize"
        assert session_dict["trial_id"] == "NCT33333333"
        assert len(session_dict["conversation_history"]) == 2
        assert session_dict["conversation_history"][0]["role"] == "user"
        assert session_dict["created_at"] == "2024-01-15T12:00:00Z"