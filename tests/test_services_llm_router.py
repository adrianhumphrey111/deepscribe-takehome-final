import pytest
from unittest.mock import Mock, patch
from api.services.llm_router import SmartLLMRouter
from api.services.llm_provider import LLMProvider, OpenAIProvider, ClaudeProvider
from api.config import Config


class TestSmartLLMRouter:
    """Test SmartLLMRouter class"""
    
    def test_router_initialization_both_providers(self, mock_config):
        """Test router initialization with both providers enabled"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai_instance = Mock()
            mock_claude_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            assert len(router.providers) == 2
            assert "openai" in router.providers
            assert "claude" in router.providers
            mock_openai.assert_called_once_with(mock_config)
            mock_claude.assert_called_once_with(mock_config)
    
    def test_router_initialization_openai_only(self, mock_config):
        """Test router initialization with only OpenAI provider"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = False
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = None
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai:
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            
            router = SmartLLMRouter(mock_config)
            
            assert len(router.providers) == 1
            assert "openai" in router.providers
            assert "claude" not in router.providers
    
    def test_router_initialization_claude_only(self, mock_config):
        """Test router initialization with only Claude provider"""
        mock_config.ENABLE_OPENAI_PROVIDER = False
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = None
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            mock_claude_instance = Mock()
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            assert len(router.providers) == 1
            assert "claude" in router.providers
            assert "openai" not in router.providers
    
    def test_router_initialization_no_providers(self, mock_config):
        """Test router initialization with no providers available"""
        mock_config.ENABLE_OPENAI_PROVIDER = False
        mock_config.ENABLE_CLAUDE_PROVIDER = False
        mock_config.OPENAI_API_KEY = None
        mock_config.ANTHROPIC_API_KEY = None
        
        with pytest.raises(ValueError, match="No LLM providers available"):
            SmartLLMRouter(mock_config)
    
    def test_router_initialization_provider_failure(self, mock_config):
        """Test router initialization with provider initialization failure"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai.side_effect = Exception("OpenAI API error")
            mock_claude_instance = Mock()
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            assert len(router.providers) == 1
            assert "claude" in router.providers
            assert "openai" not in router.providers
    
    def test_select_provider_single_provider(self, mock_config):
        """Test provider selection with only one provider available"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = False
        mock_config.OPENAI_API_KEY = "test_key"
        mock_config.ANTHROPIC_API_KEY = None
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai:
            mock_openai_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            
            router = SmartLLMRouter(mock_config)
            
            transcript = "Simple medical transcript"
            selected_provider = router.select_provider(transcript)
            
            assert selected_provider == mock_openai_instance
    
    def test_select_provider_long_transcript(self, mock_config):
        """Test provider selection for long transcript (should prefer Claude)"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai_instance = Mock()
            mock_claude_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            # Create a long transcript (>2000 words)
            transcript = "Patient presents with symptoms. " * 600  # ~3000 words
            selected_provider = router.select_provider(transcript)
            
            assert selected_provider == mock_claude_instance
    
    def test_select_provider_high_complexity(self, mock_config):
        """Test provider selection for high medical complexity (should prefer Claude)"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai_instance = Mock()
            mock_claude_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            # Create a high complexity transcript
            transcript = """
            Patient with metastatic adenocarcinoma lymphoma sarcoma presenting with neurological symptoms.
            Complex pathophysiology involving multiple cardiovascular pulmonary hepatic renal systems.
            Oncologist cardiologist neurologist endocrinologist pulmonologist consulted. 
            Patient on chemotherapy immunotherapy radiation biomarker genetic mutation therapy.
            Prognosis uncertain. Surgical resection biopsy catheterization transplant planned.
            Multiple medications including atorvastatin lisinopril omeprazole prednisone levothyroxine
            simvastatin amlodipine metoprolol insulin warfarin hydrochlorothiazide aspirin tylenol.
            Autoimmune congenital dystrophy syndrome involvement. Gastrointestinal endocrine 
            hematologic dermatologic systems affected. Dialysis endoscopy angiography laparoscopy required.
            """
            selected_provider = router.select_provider(transcript)
            
            assert selected_provider == mock_claude_instance
    
    def test_select_provider_standard_case(self, mock_config):
        """Test provider selection for standard case (should prefer OpenAI)"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai_instance = Mock()
            mock_claude_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            # Create a standard transcript
            transcript = "45-year-old female with Type 2 diabetes. Taking metformin. No complications."
            selected_provider = router.select_provider(transcript)
            
            assert selected_provider == mock_openai_instance
    
    def test_select_provider_fallback_to_claude(self, mock_config):
        """Test provider selection fallback when OpenAI is not available"""
        mock_config.ENABLE_OPENAI_PROVIDER = False
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = None
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            mock_claude_instance = Mock()
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            transcript = "Simple medical transcript"
            selected_provider = router.select_provider(transcript)
            
            assert selected_provider == mock_claude_instance
    
    def test_get_alternate_provider(self, mock_config):
        """Test getting alternate provider for fallback"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai_instance = Mock()
            mock_claude_instance = Mock()
            mock_openai_instance.provider_name = "openai"
            mock_claude_instance.provider_name = "claude"
            mock_openai.return_value = mock_openai_instance
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            # Test alternate provider selection
            alternate_to_openai = router.get_alternate_provider(mock_openai_instance)
            assert alternate_to_openai == mock_claude_instance
            
            alternate_to_claude = router.get_alternate_provider(mock_claude_instance)
            assert alternate_to_claude == mock_openai_instance
    
    def test_get_alternate_provider_single_provider(self, mock_config):
        """Test getting alternate provider when only one is available"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = False
        mock_config.OPENAI_API_KEY = "test_key"
        mock_config.ANTHROPIC_API_KEY = None
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai:
            mock_openai_instance = Mock()
            mock_openai_instance.provider_name = "openai"
            mock_openai.return_value = mock_openai_instance
            
            router = SmartLLMRouter(mock_config)
            
            # Should return the same provider when no alternate is available
            alternate = router.get_alternate_provider(mock_openai_instance)
            assert alternate == mock_openai_instance
    
    def test_calculate_medical_complexity_simple(self, mock_config):
        """Test medical complexity calculation for simple case"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            simple_transcript = "Patient has diabetes and takes metformin."
            complexity = router._calculate_medical_complexity(simple_transcript)
            
            assert 0.0 <= complexity <= 1.0
            assert complexity < 0.5  # Should be low complexity
    
    def test_calculate_medical_complexity_complex(self, mock_config):
        """Test medical complexity calculation for complex case"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            complex_transcript = """
            Patient with metastatic adenocarcinoma lymphoma sarcoma and autoimmune syndrome dystrophy.
            Neurological cardiovascular pulmonary hepatic renal involvement. Oncologist cardiologist
            neurologist endocrinologist pulmonologist pathologist radiologist consulted. 
            On chemotherapy immunotherapy radiation biomarker genetic mutation therapy and multiple medications including
            atorvastatin lisinopril omeprazole prednisone levothyroxine simvastatin amlodipine metoprolol
            insulin warfarin hydrochlorothiazide aspirin tylenol ibuprofen acetaminophen.
            Surgical resection biopsy catheterization transplant dialysis endoscopy angiography laparoscopy
            radiation therapy planned. Pathophysiology pharmacokinetics complex. Gastrointestinal endocrine
            hematologic dermatologic systems affected. Congenital malignant prognosis uncertain.
            """
            complexity = router._calculate_medical_complexity(complex_transcript)
            
            assert 0.0 <= complexity <= 1.0
            assert complexity > 0.7  # Should be high complexity
    
    def test_count_medications(self, mock_config):
        """Test medication counting"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            # Test with known medications
            transcript_with_meds = """
            Patient is taking aspirin, metformin, lisinopril, and atorvastatin.
            Also prescribed omeprazole and levothyroxine.
            """
            med_count = router._count_medications(transcript_with_meds)
            
            assert med_count >= 6  # Should count at least 6 medications
            
            # Test with no medications
            transcript_no_meds = "Patient has no current medications."
            med_count_zero = router._count_medications(transcript_no_meds)
            
            assert med_count_zero == 0
    
    def test_count_medications_patterns(self, mock_config):
        """Test medication counting with pattern matching"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            # Test with medication patterns
            transcript_with_patterns = """
            Patient is on amoxicillin, simvastatin, and amlodipine.
            Also taking metoprolol and omeprazole.
            """
            med_count = router._count_medications(transcript_with_patterns)
            
            assert med_count >= 5  # Should count pattern-based medications
    
    def test_count_specialists(self, mock_config):
        """Test specialist counting"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            # Test with multiple specialists
            transcript_with_specialists = """
            Patient was referred to cardiologist and oncologist.
            Also consulting with neurologist and endocrinologist.
            Surgeon will evaluate for possible intervention.
            """
            specialist_count = router._count_specialists(transcript_with_specialists)
            
            assert specialist_count >= 5  # Should count at least 5 specialists
            
            # Test with no specialists
            transcript_no_specialists = "Patient seen by primary care physician."
            specialist_count_zero = router._count_specialists(transcript_no_specialists)
            
            assert specialist_count_zero == 0
    
    def test_get_available_providers(self, mock_config):
        """Test getting available provider names"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai.return_value = Mock()
            mock_claude.return_value = Mock()
            
            router = SmartLLMRouter(mock_config)
            
            available_providers = router.get_available_providers()
            
            assert len(available_providers) == 2
            assert "openai" in available_providers
            assert "claude" in available_providers
    
    def test_get_provider_by_name(self, mock_config):
        """Test getting provider by name"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_openai_key"
        mock_config.ANTHROPIC_API_KEY = "test_claude_key"
        
        with patch('api.services.llm_router.OpenAIProvider') as mock_openai, \
             patch('api.services.llm_router.ClaudeProvider') as mock_claude:
            
            mock_openai_instance = Mock()
            mock_claude_instance = Mock()
            mock_openai.return_value = mock_openai_instance
            mock_claude.return_value = mock_claude_instance
            
            router = SmartLLMRouter(mock_config)
            
            # Test valid provider names
            openai_provider = router.get_provider_by_name("openai")
            assert openai_provider == mock_openai_instance
            
            claude_provider = router.get_provider_by_name("claude")
            assert claude_provider == mock_claude_instance
    
    def test_get_provider_by_name_invalid(self, mock_config):
        """Test getting provider by invalid name"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.ENABLE_CLAUDE_PROVIDER = False
        mock_config.OPENAI_API_KEY = "test_key"
        mock_config.ANTHROPIC_API_KEY = None
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            # Test invalid provider name
            with pytest.raises(ValueError, match="Provider 'invalid' not available"):
                router.get_provider_by_name("invalid")
    
    def test_complexity_calculation_edge_cases(self, mock_config):
        """Test complexity calculation edge cases"""
        mock_config.ENABLE_OPENAI_PROVIDER = True
        mock_config.OPENAI_API_KEY = "test_key"
        
        with patch('api.services.llm_router.OpenAIProvider'):
            router = SmartLLMRouter(mock_config)
            
            # Test empty transcript
            empty_transcript = ""
            complexity = router._calculate_medical_complexity(empty_transcript)
            assert complexity == 0.0
            
            # Test transcript with only common words
            simple_transcript = "The patient feels good today and is happy."
            complexity = router._calculate_medical_complexity(simple_transcript)
            assert complexity == 0.0
            
            # Test transcript with repeated complex terms (should not exceed 1.0)
            repeated_complex = "metastatic " * 100 + "adenocarcinoma " * 100
            complexity = router._calculate_medical_complexity(repeated_complex)
            assert complexity <= 1.0