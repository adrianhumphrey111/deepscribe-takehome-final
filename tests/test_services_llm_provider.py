import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from api.services.llm_provider import LLMProvider, OpenAIProvider, ClaudeProvider
from api.models.patient_data import PatientData, Gender, ConfidenceScores, ExtractionResult
from api.config import Config


class TestLLMProviderAbstract:
    """Test abstract LLMProvider class"""
    
    def test_llm_provider_abstract_instantiation(self):
        """Test that LLMProvider cannot be instantiated directly"""
        with pytest.raises(TypeError):
            LLMProvider(Mock())
    
    def test_llm_provider_abstract_methods(self):
        """Test abstract methods are properly defined"""
        class ConcreteProvider(LLMProvider):
            async def extract_patient_data(self, transcript: str):
                pass
            
            async def generate_qa_response(self, question: str, context: str):
                pass
            
            @property
            def provider_name(self):
                return "test"
        
        config = Mock()
        provider = ConcreteProvider(config)
        assert provider.config == config
        assert provider.provider_name == "test"


class TestOpenAIProvider:
    """Test OpenAI provider implementation"""
    
    def test_openai_provider_initialization_success(self, mock_config):
        """Test successful OpenAI provider initialization"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            assert provider.config == mock_config
            assert provider.client == mock_client
            assert provider.provider_name == "openai"
            mock_openai.assert_called_once_with(api_key="test_key")
    
    def test_openai_provider_initialization_no_key(self, mock_config):
        """Test OpenAI provider initialization without API key"""
        mock_config.OPENAI_API_KEY = None
        
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            OpenAIProvider(mock_config)
    
    @pytest.mark.asyncio
    async def test_openai_extract_patient_data_success(self, mock_config, sample_openai_response):
        """Test successful patient data extraction with OpenAI"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        # Mock OpenAI response
        sample_openai_response.choices[0].message.content = json.dumps({
            "age": 45,
            "gender": "FEMALE",
            "conditions": ["Type 2 Diabetes"],
            "primary_diagnosis": "Type 2 Diabetes",
            "medications": ["Metformin"],
            "allergies": ["Penicillin"],
            "location": {"city": "San Francisco", "state": "CA"},
            "overall_confidence": 0.85  # Our improved prompts use overall_confidence
        })
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = sample_openai_response
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            transcript = "45-year-old female with Type 2 diabetes, taking Metformin, allergic to Penicillin"
            result = await provider.extract_patient_data(transcript)
            
            assert result.__class__.__name__ == 'ExtractionResult'
            assert result.success is True
            assert result.provider_used == "openai"
            assert result.patient_data.age == 45
            assert result.patient_data.gender == Gender.FEMALE
            assert result.patient_data.conditions == ["Type 2 Diabetes"]
            assert result.patient_data.primary_diagnosis == "Type 2 Diabetes"
            assert result.patient_data.medications == ["Metformin"]
            assert result.patient_data.allergies == ["Penicillin"]
            assert result.confidence_scores.age == 0.85  # All fields use overall_confidence
            assert result.confidence_scores.gender == 0.85
            assert result.confidence_scores.overall == 0.85
            assert result.extraction_time_ms >= 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_openai_extract_patient_data_json_parse_error(self, mock_config):
        """Test OpenAI extraction with JSON parsing error"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Invalid JSON response"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            result = await provider.extract_patient_data("test transcript")
            
            assert result.success is False
            assert result.provider_used == "openai"
            assert "Could not parse JSON" in result.error_message
    
    @pytest.mark.asyncio
    async def test_openai_extract_patient_data_json_extraction(self, mock_config):
        """Test OpenAI extraction with JSON embedded in text"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        json_data = {
            "age": 30,
            "gender": "MALE",
            "conditions": ["Asthma"],
            "confidence_scores": {"age": 0.8, "overall": 0.7}
        }
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = f"Here is the extracted data: {json.dumps(json_data)} Hope this helps!"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            result = await provider.extract_patient_data("test transcript")
            
            assert result.success is True
            assert result.patient_data.age == 30
            assert result.patient_data.gender == Gender.MALE
            assert result.patient_data.conditions == ["Asthma"]
    
    @pytest.mark.asyncio
    async def test_openai_extract_patient_data_api_error(self, mock_config):
        """Test OpenAI extraction with API error"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            result = await provider.extract_patient_data("test transcript")
            
            assert result.success is False
            assert result.provider_used == "openai"
            assert "API rate limit exceeded" in result.error_message
            assert result.patient_data.__class__.__name__ == 'PatientData'
            assert result.confidence_scores.__class__.__name__ == 'ConfidenceScores'
    
    @pytest.mark.asyncio
    async def test_openai_generate_qa_response_success(self, mock_config):
        """Test successful Q&A response generation with OpenAI"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "This trial is for patients with Type 2 diabetes aged 18-65."
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            question = "What are the eligibility criteria?"
            context = "Clinical trial for diabetes treatment"
            response = await provider.generate_qa_response(question, context)
            
            assert response == "This trial is for patients with Type 2 diabetes aged 18-65."
            mock_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_openai_generate_qa_response_error(self, mock_config):
        """Test Q&A response generation with error"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_client.chat.completions.create.side_effect = Exception("API error")
            mock_openai.return_value = mock_client
            
            provider = OpenAIProvider(mock_config)
            
            response = await provider.generate_qa_response("test question", "test context")
            
            assert "I apologize, but I encountered an error" in response
            assert "API error" in response
    
    def test_openai_build_extraction_prompt(self, mock_config):
        """Test extraction prompt building"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI'):
            provider = OpenAIProvider(mock_config)
            
            transcript = "Patient is 45 years old with diabetes"
            prompt = provider._build_extraction_prompt(transcript)
            
            assert "extracting patient information" in prompt
            assert transcript in prompt
            assert "age (integer)" in prompt
            assert "gender" in prompt
            assert "conditions" in prompt
            assert "Return only valid JSON" in prompt
    
    def test_openai_convert_to_patient_data(self, mock_config):
        """Test conversion of extracted data to PatientData"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI'):
            provider = OpenAIProvider(mock_config)
            
            extracted_data = {
                "age": 50,
                "gender": "MALE",
                "conditions": ["Hypertension", "Diabetes"],
                "primary_diagnosis": "Hypertension",
                "medications": ["Lisinopril"],
                "allergies": ["Sulfa"],
                "location": {"city": "Boston", "state": "MA"}
            }
            
            patient_data = provider._convert_to_patient_data(extracted_data)
            
            assert patient_data.__class__.__name__ == 'PatientData'
            assert patient_data.age == 50
            assert patient_data.gender == Gender.MALE
            assert patient_data.conditions == ["Hypertension", "Diabetes"]
            assert patient_data.primary_diagnosis == "Hypertension"
            assert patient_data.medications == ["Lisinopril"]
            assert patient_data.allergies == ["Sulfa"]
            assert patient_data.location.city == "Boston"
            assert patient_data.location.state == "MA"
    
    def test_openai_calculate_confidence_scores(self, mock_config):
        """Test confidence score calculation"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI'):
            provider = OpenAIProvider(mock_config)
            
            extracted_data = {
                "overall_confidence": 0.88  # Our improved prompts use overall_confidence
            }
            
            confidence_scores = provider._calculate_confidence_scores(extracted_data)
            
            assert confidence_scores.__class__.__name__ == 'ConfidenceScores'
            assert confidence_scores.age == 0.88  # All fields use overall_confidence
            assert confidence_scores.gender == 0.88
            assert confidence_scores.primary_diagnosis == 0.88
            assert confidence_scores.conditions == 0.88
            assert confidence_scores.medications == 0.88
            assert confidence_scores.location == 0.88
            assert confidence_scores.overall == 0.88
    
    def test_openai_calculate_confidence_scores_defaults(self, mock_config):
        """Test confidence score calculation with missing data"""
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('openai.OpenAI'):
            provider = OpenAIProvider(mock_config)
            
            extracted_data = {}
            
            confidence_scores = provider._calculate_confidence_scores(extracted_data)
            
            assert confidence_scores.__class__.__name__ == 'ConfidenceScores'
            assert confidence_scores.age == 0.5
            assert confidence_scores.gender == 0.5
            assert confidence_scores.primary_diagnosis == 0.5
            assert confidence_scores.conditions == 0.5
            assert confidence_scores.medications == 0.5
            assert confidence_scores.location == 0.5
            assert confidence_scores.overall == 0.5


class TestClaudeProvider:
    """Test Claude provider implementation"""
    
    def test_claude_provider_initialization_success(self, mock_config):
        """Test successful Claude provider initialization"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client') as mock_anthropic:
            mock_client = Mock()
            mock_anthropic.return_value = mock_client
            
            provider = ClaudeProvider(mock_config)
            
            assert provider.config == mock_config
            assert provider.client == mock_client
            assert provider.provider_name == "claude"
            mock_anthropic.assert_called_once_with(api_key="test_key")
    
    def test_claude_provider_initialization_no_key(self, mock_config):
        """Test Claude provider initialization without API key"""
        mock_config.ANTHROPIC_API_KEY = None
        
        with pytest.raises(ValueError, match="Anthropic API key is required"):
            ClaudeProvider(mock_config)
    
    @pytest.mark.asyncio
    async def test_claude_extract_patient_data_success(self, mock_config, sample_anthropic_response):
        """Test successful patient data extraction with Claude"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        # Mock Claude response
        sample_anthropic_response.content[0].text = json.dumps({
            "age": 35,
            "gender": "MALE",
            "conditions": ["Asthma"],
            "primary_diagnosis": "Asthma",
            "medications": ["Albuterol"],
            "allergies": ["Peanuts"],
            "location": {"city": "New York", "state": "NY"},
            "overall_confidence": 0.85  # Our improved prompts use overall_confidence
        })
        
        with patch('anthropic.Client') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = sample_anthropic_response
            mock_anthropic.return_value = mock_client
            
            provider = ClaudeProvider(mock_config)
            
            transcript = "35-year-old male with asthma, using albuterol, allergic to peanuts"
            result = await provider.extract_patient_data(transcript)
            
            assert result.__class__.__name__ == 'ExtractionResult'
            assert result.success is True
            assert result.provider_used == "claude"
            assert result.patient_data.age == 35
            assert result.patient_data.gender == Gender.MALE
            assert result.patient_data.conditions == ["Asthma"]
            assert result.patient_data.primary_diagnosis == "Asthma"
            assert result.patient_data.medications == ["Albuterol"]
            assert result.patient_data.allergies == ["Peanuts"]
            assert result.confidence_scores.age == 0.85  # All fields use overall_confidence
            assert result.confidence_scores.gender == 0.85
            assert result.confidence_scores.overall == 0.85
            assert result.extraction_time_ms >= 0
            assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_claude_extract_patient_data_json_parse_error(self, mock_config):
        """Test Claude extraction with JSON parsing error"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client') as mock_anthropic:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "Invalid JSON response"
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            provider = ClaudeProvider(mock_config)
            
            result = await provider.extract_patient_data("test transcript")
            
            assert result.success is False
            assert result.provider_used == "claude"
            assert "Could not parse JSON" in result.error_message
    
    @pytest.mark.asyncio
    async def test_claude_extract_patient_data_api_error(self, mock_config):
        """Test Claude extraction with API error"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API rate limit exceeded")
            mock_anthropic.return_value = mock_client
            
            provider = ClaudeProvider(mock_config)
            
            result = await provider.extract_patient_data("test transcript")
            
            assert result.success is False
            assert result.provider_used == "claude"
            assert "API rate limit exceeded" in result.error_message
            assert result.patient_data.__class__.__name__ == 'PatientData'
            assert result.confidence_scores.__class__.__name__ == 'ConfidenceScores'
    
    @pytest.mark.asyncio
    async def test_claude_generate_qa_response_success(self, mock_config):
        """Test successful Q&A response generation with Claude"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client') as mock_anthropic:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.content = [Mock()]
            mock_response.content[0].text = "This trial requires patients to be 21-70 years old with diabetes."
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            provider = ClaudeProvider(mock_config)
            
            question = "What are the age requirements?"
            context = "Clinical trial for diabetes treatment"
            response = await provider.generate_qa_response(question, context)
            
            assert response == "This trial requires patients to be 21-70 years old with diabetes."
            mock_client.messages.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_claude_generate_qa_response_error(self, mock_config):
        """Test Q&A response generation with error"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.side_effect = Exception("API error")
            mock_anthropic.return_value = mock_client
            
            provider = ClaudeProvider(mock_config)
            
            response = await provider.generate_qa_response("test question", "test context")
            
            assert "I apologize, but I encountered an error" in response
            assert "API error" in response
    
    def test_claude_build_extraction_prompt(self, mock_config):
        """Test extraction prompt building"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client'):
            provider = ClaudeProvider(mock_config)
            
            transcript = "Patient is 35 years old with asthma"
            prompt = provider._build_extraction_prompt(transcript)
            
            assert "extracting patient information" in prompt
            assert transcript in prompt
            assert "age (integer)" in prompt
            assert "gender" in prompt
            assert "conditions" in prompt
            assert "Return only valid JSON" in prompt
    
    def test_claude_convert_to_patient_data(self, mock_config):
        """Test conversion of extracted data to PatientData"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client'):
            provider = ClaudeProvider(mock_config)
            
            extracted_data = {
                "age": 40,
                "gender": "FEMALE",
                "conditions": ["Migraine"],
                "primary_diagnosis": "Migraine",
                "medications": ["Sumatriptan"],
                "allergies": ["Aspirin"],
                "location": {"city": "Chicago", "state": "IL"}
            }
            
            patient_data = provider._convert_to_patient_data(extracted_data)
            
            assert patient_data.__class__.__name__ == 'PatientData'
            assert patient_data.age == 40
            assert patient_data.gender == Gender.FEMALE
            assert patient_data.conditions == ["Migraine"]
            assert patient_data.primary_diagnosis == "Migraine"
            assert patient_data.medications == ["Sumatriptan"]
            assert patient_data.allergies == ["Aspirin"]
            assert patient_data.location.city == "Chicago"
            assert patient_data.location.state == "IL"
    
    def test_claude_calculate_confidence_scores(self, mock_config):
        """Test confidence score calculation"""
        mock_config.ANTHROPIC_API_KEY = "test_key"
        
        with patch('anthropic.Client'):
            provider = ClaudeProvider(mock_config)
            
            extracted_data = {
                "overall_confidence": 0.78  # Our improved prompts use overall_confidence
            }
            
            confidence_scores = provider._calculate_confidence_scores(extracted_data)
            
            assert confidence_scores.__class__.__name__ == 'ConfidenceScores'
            assert confidence_scores.age == 0.78  # All fields use overall_confidence
            assert confidence_scores.gender == 0.78
            assert confidence_scores.primary_diagnosis == 0.78
            assert confidence_scores.conditions == 0.78
            assert confidence_scores.medications == 0.78
            assert confidence_scores.location == 0.78
            assert confidence_scores.overall == 0.78