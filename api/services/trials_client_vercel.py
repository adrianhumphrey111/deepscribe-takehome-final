import requests
import logging
from typing import Dict, List, Optional, Any
from config import Config
from models.patient_data import PatientData
from models.trial_data import Trial, TrialStatus, TrialPhase, TrialLocation, ContactInfo, EligibilityCriteria

# Try to import LangChain services, fall back to simple versions if not available
try:
    from services.langchain_rag_service import LangChainRAGService
    from services.llm_eligibility_filter import LLMEligibilityFilter
    USE_ADVANCED_SERVICES = True
except ImportError:
    from services.simple_rag_service import SimpleRAGService
    USE_ADVANCED_SERVICES = False

logger = logging.getLogger(__name__)

class ClinicalTrialsClient:
    """Client for interacting with ClinicalTrials.gov API - Vercel compatible"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.CLINICAL_TRIALS_API_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Clinical-Trials-Matcher/1.0'
        })
        
        # Use appropriate service based on availability
        if USE_ADVANCED_SERVICES:
            self.rag_service = LangChainRAGService(config)
            self.llm_eligibility_filter = LLMEligibilityFilter(config)
        else:
            self.rag_service = SimpleRAGService(config)
            self.llm_eligibility_filter = None
        
        logger.info(f"Initialized ClinicalTrialsClient with advanced services: {USE_ADVANCED_SERVICES}")
    
    async def search_trials(self, patient_data: PatientData, max_results: int = 25) -> List[Trial]:
        """Search for clinical trials based on patient data"""
        try:
            # Build search query
            query_params = await self._build_search_params(patient_data, max_results)
            
            # Make API request
            logger.info(f"Searching with params: {query_params}")
            response = self.session.get(
                f"{self.base_url}/studies",
                params=query_params,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"API response status: {response.status_code}, URL: {response.url}")
            
            # Parse response
            data = response.json()
            trials = []
            
            for study_data in data.get('studies', []):
                trial = self._convert_to_trial(study_data)
                if trial:
                    trials.append(trial)
            
            logger.info(f"Found {len(trials)} trials")
            
            # Use LLM filtering if available, otherwise return raw results
            if USE_ADVANCED_SERVICES and self.llm_eligibility_filter:
                # Pass patient coordinates to eligibility filter for location-based ranking
                self.llm_eligibility_filter.patient_coords = self.patient_coords
                
                # Use LLM to analyze eligibility and rank trials
                ranked_trial_data = await self.llm_eligibility_filter.rank_and_filter_trials(trials, patient_data)
                
                # Extract just the trials from the ranked data
                eligible_trials = [item["trial"] for item in ranked_trial_data]
                
                logger.info(f"Found {len(eligible_trials)} eligible trials after LLM analysis")
                return eligible_trials
            else:
                # Simple ranking by basic criteria
                ranked_trials = self._simple_ranking(trials, patient_data)
                logger.info(f"Returning {len(ranked_trials)} trials with simple ranking")
                return ranked_trials
                
        except requests.exceptions.RequestException as e:
            logger.error(f"ClinicalTrials.gov API request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching trials: {str(e)}")
            return []
    
    def _simple_ranking(self, trials: List[Trial], patient_data: PatientData) -> List[Trial]:
        """Simple ranking algorithm when LLM services aren't available"""
        # Basic scoring based on location proximity and basic matching
        scored_trials = []
        
        for trial in trials:
            score = 0.5  # Base score
            
            # Location scoring
            if patient_data.location and trial.locations:
                patient_state = patient_data.location.state
                for location in trial.locations:
                    if location.state == patient_state:
                        score += 0.3  # Same state bonus
                        break
            
            # Basic condition matching
            if patient_data.primary_diagnosis and trial.brief_summary:
                condition_words = patient_data.primary_diagnosis.lower().split()
                summary_lower = trial.brief_summary.lower()
                matches = sum(1 for word in condition_words if word in summary_lower)
                score += min(0.2, matches * 0.05)  # Up to 0.2 bonus for keyword matches
            
            scored_trials.append((trial, score))
        
        # Sort by score (highest first) and return trials
        scored_trials.sort(key=lambda x: x[1], reverse=True)
        return [trial for trial, score in scored_trials]
    
    async def get_trial_details(self, nct_id: str) -> Optional[Trial]:
        """Get detailed information about a specific trial"""
        try:
            # Use simple endpoint without field specification to get all available data
            response = self.session.get(
                f"{self.base_url}/studies/{nct_id}",
                params={'format': 'json'},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            trial = self._convert_to_trial(data)
            
            logger.info(f"Retrieved comprehensive details for trial {nct_id}")
            return trial
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get trial details for {nct_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting trial details: {str(e)}")
            return None
    
    async def get_trial_dict(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """Get trial details as dictionary for Q&A service"""
        trial = await self.get_trial_details(nct_id)
        if trial:
            return trial.dict()
        return None
    
    async def _build_search_params(self, patient_data: PatientData, max_results: int) -> Dict[str, Any]:
        """Build search parameters from patient data"""
        params = {
            'format': 'json',
            'pageSize': max_results,
            'fields': ','.join([
                'NCTId', 'BriefTitle', 'DetailedDescription', 'OverallStatus',
                'Phase', 'StudyType', 'BriefSummary', 'Condition', 'InterventionName',
                'PrimaryOutcomeMeasure', 'SecondaryOutcomeMeasure', 'EnrollmentCount',
                'StudyFirstPostDate', 'LastUpdatePostDate', 'CompletionDate',
                'LocationFacility', 'LocationCity', 'LocationState', 'LocationCountry',
                'CentralContactName', 'CentralContactPhone', 'CentralContactEMail',
                'LeadSponsorName', 'CollaboratorName', 'EligibilityCriteria',
                'MinimumAge', 'MaximumAge', 'Gender', 'HealthyVolunteers'
            ])
        }
        
        # Add condition-based query using RAG service
        if patient_data.primary_diagnosis:
            # Build comprehensive context for targeted RAG query generation
            additional_context = {
                'age': patient_data.age,
                'age_group': self._get_age_group(patient_data.age),
                'cancer_stage': patient_data.cancer_stage,
                'tumor_markers': patient_data.tumor_markers,
                'secondary_conditions': patient_data.conditions[:3] if patient_data.conditions else None,
                'previous_treatments': patient_data.previous_treatments[:3] if patient_data.previous_treatments else None
            }
            # Remove None values for cleaner context
            additional_context = {k: v for k, v in additional_context.items() if v is not None}
            
            params['query.cond'] = await self.rag_service.generate_search_query(
                patient_data.primary_diagnosis, 
                additional_context
            )
        elif patient_data.conditions:
            # Generate query for primary condition with context (exclude location - handled separately)
            primary_condition = patient_data.conditions[0]
            additional_context = {
                'age': patient_data.age,
                'age_group': self._get_age_group(patient_data.age),
                'related_conditions': patient_data.conditions[1:4] if len(patient_data.conditions) > 1 else None
            }
            # Remove None values for cleaner context
            additional_context = {k: v for k, v in additional_context.items() if v is not None}
            params['query.cond'] = await self.rag_service.generate_search_query(
                primary_condition,
                additional_context
            )
        
        # Add filters
        filters = []
        
        # Status filter - only trials patients can actually join
        params['filter.overallStatus'] = 'RECRUITING,NOT_YET_RECRUITING,ENROLLING_BY_INVITATION'
        
        # Store patient coordinates for ranking (don't filter by geography)
        self.patient_coords = None
        if patient_data.location and patient_data.location.city and patient_data.location.state:
            self.patient_coords = self._get_city_coordinates(patient_data.location.city, patient_data.location.state)
        
        # Build advanced eligibility filters
        advanced_filters = []
        
        # Gender filter - include both specific gender and "ALL" trials
        if patient_data.gender and patient_data.gender.value in ["MALE", "FEMALE"]:
            gender_filter = f"AREA[Gender]{patient_data.gender.value} OR AREA[Gender]ALL"
            advanced_filters.append(f"({gender_filter})")
        
        # Exclude healthy volunteer studies for patients with conditions
        if patient_data.primary_diagnosis or patient_data.conditions:
            healthy_volunteers_filter = "AREA[HealthyVolunteers]No"
            advanced_filters.append(healthy_volunteers_filter)
        
        # Combine all advanced filters
        if advanced_filters:
            params['filter.advanced'] = " AND ".join(advanced_filters)
        
        # Sort by relevance
        params['sort'] = ['@relevance']
        
        return params
    
    def _get_city_coordinates(self, city: str, state: str) -> Optional[tuple]:
        """Get coordinates for cities using Nominatim geocoding API"""
        try:
            # Use Nominatim (OpenStreetMap) geocoding API - free and no API key required
            query = f"{city}, {state}, United States"
            geocoding_url = "https://nominatim.openstreetmap.org/search"
            
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'us'
            }
            
            headers = {
                'User-Agent': 'Clinical-Trials-Matcher/1.0 (medical research application)'
            }
            
            response = self.session.get(
                geocoding_url,
                params=params,
                headers=headers,
                timeout=5  # Short timeout for geocoding
            )
            
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    lat = float(results[0]['lat'])
                    lon = float(results[0]['lon'])
                    logger.info(f"Geocoded {city}, {state} to ({lat}, {lon})")
                    return (lat, lon)
                    
        except Exception as e:
            logger.warning(f"Geocoding failed for {city}, {state}: {str(e)}")
        
        # Return None if geocoding fails - no geographic filter will be applied
        logger.info(f"No coordinates found for {city}, {state} - skipping geographic filter")
        return None
    
    def _convert_to_trial(self, study_data: Dict[str, Any]) -> Optional[Trial]:
        """Convert API response to Trial model"""
        try:
            protocol_section = study_data.get('protocolSection', {})
            
            # Basic information
            identification = protocol_section.get('identificationModule', {})
            status_module = protocol_section.get('statusModule', {})
            design_module = protocol_section.get('designModule', {})
            
            # Extract basic fields
            nct_id = identification.get('nctId', '')
            title = identification.get('briefTitle', '')
            
            # Status
            status_str = status_module.get('overallStatus', 'UNKNOWN')
            try:
                status = TrialStatus(status_str)
            except ValueError:
                status = TrialStatus.RECRUITING  # Default fallback
            
            # Phase
            phase_list = design_module.get('phases', [])
            phase = None
            if phase_list:
                phase_str = phase_list[0]
                try:
                    phase = TrialPhase(phase_str)
                except ValueError:
                    phase = TrialPhase.NOT_APPLICABLE
            
            # Description
            description_module = protocol_section.get('descriptionModule', {})
            brief_summary = description_module.get('briefSummary', '')
            detailed_description = description_module.get('detailedDescription', '')
            
            # Eligibility
            eligibility_module = protocol_section.get('eligibilityModule', {})
            eligibility_criteria = self._extract_eligibility_criteria(eligibility_module)
            
            # Locations
            contacts_locations = protocol_section.get('contactsLocationsModule', {})
            locations = self._extract_locations(contacts_locations)
            
            # Contact info
            contact_info = self._extract_contact_info(contacts_locations)
            
            # Study details
            outcomes_module = protocol_section.get('outcomesModule', {})
            primary_outcomes = outcomes_module.get('primaryOutcomes', [])
            secondary_outcomes = outcomes_module.get('secondaryOutcomes', [])
            
            primary_outcome = primary_outcomes[0].get('measure', '') if primary_outcomes else None
            secondary_outcome_list = [outcome.get('measure', '') for outcome in secondary_outcomes]
            
            # Sponsor
            sponsor_module = protocol_section.get('sponsorCollaboratorsModule', {})
            lead_sponsor = sponsor_module.get('leadSponsor', {})
            sponsor_name = lead_sponsor.get('name', '')
            
            # Enrollment
            design_module = protocol_section.get('designModule', {})
            enrollment_info = design_module.get('enrollmentInfo', {})
            enrollment_count = enrollment_info.get('count')
            
            # Create trial object
            trial = Trial(
                nct_id=nct_id,
                title=title,
                status=status,
                phase=phase,
                brief_summary=brief_summary,
                detailed_description=detailed_description,
                locations=locations,
                contact_info=contact_info,
                eligibility_criteria=eligibility_criteria,
                study_type=design_module.get('studyType', ''),
                primary_outcome=primary_outcome,
                secondary_outcomes=secondary_outcome_list,
                enrollment_target=enrollment_count,
                sponsor=sponsor_name
            )
            
            return trial
            
        except Exception as e:
            logger.error(f"Error converting study data to Trial: {str(e)}")
            return None
    
    def _extract_eligibility_criteria(self, eligibility_module: Dict[str, Any]) -> Optional[EligibilityCriteria]:
        """Extract eligibility criteria from API response"""
        try:
            criteria = EligibilityCriteria()
            
            # Age
            minimum_age = eligibility_module.get('minimumAge', '')
            maximum_age = eligibility_module.get('maximumAge', '')
            
            if minimum_age and minimum_age != 'N/A':
                # Parse age string like "18 Years"
                age_parts = minimum_age.split()
                if age_parts and age_parts[0].isdigit():
                    criteria.age_min = int(age_parts[0])
            
            if maximum_age and maximum_age != 'N/A':
                age_parts = maximum_age.split()
                if age_parts and age_parts[0].isdigit():
                    criteria.age_max = int(age_parts[0])
            
            # Gender
            gender = eligibility_module.get('gender', 'ALL')
            criteria.gender = gender
            
            # Healthy volunteers
            healthy_volunteers = eligibility_module.get('healthyVolunteers', 'No')
            if isinstance(healthy_volunteers, bool):
                criteria.healthy_volunteers = healthy_volunteers
            else:
                criteria.healthy_volunteers = str(healthy_volunteers).lower() == 'yes'
            
            # Criteria text
            criteria_text = eligibility_module.get('eligibilityCriteria', '')
            if criteria_text:
                # Simple parsing of inclusion/exclusion criteria
                sections = criteria_text.split('Exclusion Criteria:')
                if len(sections) > 1:
                    inclusion_text = sections[0].replace('Inclusion Criteria:', '').strip()
                    exclusion_text = sections[1].strip()
                    
                    # Split by common delimiters
                    inclusion_items = [item.strip() for item in inclusion_text.split('\n') if item.strip()]
                    exclusion_items = [item.strip() for item in exclusion_text.split('\n') if item.strip()]
                    
                    criteria.inclusion_criteria = inclusion_items
                    criteria.exclusion_criteria = exclusion_items
            
            return criteria
            
        except Exception as e:
            logger.error(f"Error extracting eligibility criteria: {str(e)}")
            return None
    
    def _get_age_group(self, age: Optional[int]) -> Optional[str]:
        """Categorize age for better trial targeting"""
        if age is None:
            return None
        
        if age < 18:
            return "pediatric"
        elif age < 25:
            return "young_adult"
        elif age < 65:
            return "adult"
        else:
            return "elderly"
    
    def _extract_locations(self, contacts_locations: Dict[str, Any]) -> List[TrialLocation]:
        """Extract trial locations from API response"""
        locations = []
        
        try:
            location_list = contacts_locations.get('locations', [])
            
            for loc_data in location_list:
                location = TrialLocation(
                    city=loc_data.get('city', ''),
                    state=loc_data.get('state', ''),
                    country=loc_data.get('country', ''),
                    facility=loc_data.get('facility', '')
                )
                
                # Note: Coordinates not needed for display purposes
                # Geographic filtering already applied in API query
                
                locations.append(location)
            
        except Exception as e:
            logger.error(f"Error extracting locations: {str(e)}")
        
        return locations
    
    def _extract_contact_info(self, contacts_locations: Dict[str, Any]) -> Optional[ContactInfo]:
        """Extract contact information from API response"""
        try:
            central_contacts = contacts_locations.get('centralContacts', [])
            
            if central_contacts:
                contact_data = central_contacts[0]  # Use first contact
                
                return ContactInfo(
                    name=contact_data.get('name', ''),
                    phone=contact_data.get('phone', ''),
                    email=contact_data.get('email', '')
                )
                
        except Exception as e:
            logger.error(f"Error extracting contact info: {str(e)}")
        
        return None