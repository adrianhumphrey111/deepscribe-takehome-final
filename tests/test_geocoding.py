import pytest
from unittest.mock import Mock, patch
from api.services.trials_client import ClinicalTrialsClient
from api.config import Config


class TestGeocoding:
    """Test geocoding functionality"""
    
    def test_geocoding_api_success(self, mock_config):
        """Test successful geocoding API call"""
        mock_config.CLINICAL_TRIALS_API_URL = "https://test-api.gov"
        
        # Mock successful geocoding response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'lat': '42.3601',
                'lon': '-71.0589',
                'display_name': 'Boston, Massachusetts, United States'
            }
        ]
        
        with patch.object(ClinicalTrialsClient, '__init__', lambda x, y: None):
            client = ClinicalTrialsClient.__new__(ClinicalTrialsClient)
            client.session = Mock()
            client.session.get.return_value = mock_response
            
            coords = client._get_city_coordinates("Boston", "MA")
            
            assert coords == (42.3601, -71.0589)
            client.session.get.assert_called_once()
    
    def test_geocoding_api_failure_returns_none(self, mock_config):
        """Test that API failure returns None"""
        mock_config.CLINICAL_TRIALS_API_URL = "https://test-api.gov"
        
        # Mock failed geocoding response
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(ClinicalTrialsClient, '__init__', lambda x, y: None):
            client = ClinicalTrialsClient.__new__(ClinicalTrialsClient)
            client.session = Mock()
            client.session.get.return_value = mock_response
            
            coords = client._get_city_coordinates("San Francisco", "CA")
            
            # Should return None when API fails
            assert coords is None
    
    def test_geocoding_timeout_returns_none(self, mock_config):
        """Test that timeout returns None"""
        mock_config.CLINICAL_TRIALS_API_URL = "https://test-api.gov"
        
        with patch.object(ClinicalTrialsClient, '__init__', lambda x, y: None):
            client = ClinicalTrialsClient.__new__(ClinicalTrialsClient)
            client.session = Mock()
            client.session.get.side_effect = Exception("Timeout")
            
            coords = client._get_city_coordinates("Seattle", "WA")
            
            # Should return None when timeout occurs
            assert coords is None
    
    def test_geocoding_unknown_city_returns_none(self, mock_config):
        """Test behavior for unknown cities"""
        mock_config.CLINICAL_TRIALS_API_URL = "https://test-api.gov"
        
        # Mock empty geocoding response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        
        with patch.object(ClinicalTrialsClient, '__init__', lambda x, y: None):
            client = ClinicalTrialsClient.__new__(ClinicalTrialsClient)
            client.session = Mock()
            client.session.get.return_value = mock_response
            
            coords = client._get_city_coordinates("UnknownCity", "ZZ")
            
            # Should return None for unknown cities
            assert coords is None
    
    def test_geocoding_empty_response_returns_none(self, mock_config):
        """Test that empty API response returns None"""
        mock_config.CLINICAL_TRIALS_API_URL = "https://test-api.gov"
        
        # Mock empty geocoding response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        
        with patch.object(ClinicalTrialsClient, '__init__', lambda x, y: None):
            client = ClinicalTrialsClient.__new__(ClinicalTrialsClient)
            client.session = Mock()
            client.session.get.return_value = mock_response
            
            coords = client._get_city_coordinates("NonExistentCity", "XX")
            
            # Should return None for empty responses
            assert coords is None