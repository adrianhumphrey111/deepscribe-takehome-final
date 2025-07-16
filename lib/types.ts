// TypeScript interfaces for the clinical trials app

export interface PatientData {
  age?: number
  gender?: 'MALE' | 'FEMALE' | 'OTHER'
  primary_diagnosis?: string
  cancer_stage?: string
  conditions?: string[]
  medications?: string[]
  allergies?: string[]
  comorbidities?: string[]
  previous_treatments?: string[]
  tumor_markers?: Record<string, any>
  tumor_size?: string
  menopausal_status?: string
  willing_to_travel?: boolean
  preferred_distance?: number
  location?: {
    city?: string
    state?: string
    zip_code?: string
    latitude?: number
    longitude?: number
  }
}

export interface ConfidenceScores {
  overall?: number
  age?: number
  gender?: number
  primary_diagnosis?: number
  conditions?: number
  medications?: number
  location?: number
}

export interface ExtractionResult {
  success: boolean
  patient_data?: PatientData
  confidence_scores?: ConfidenceScores
  provider_used?: string
  extraction_time_ms?: number
  error_message?: string
}

export interface TrialLocation {
  city?: string
  state?: string
  country?: string
  facility?: string
  latitude?: number
  longitude?: number
}

export interface ContactInfo {
  name?: string
  phone?: string
  email?: string
}

export interface EligibilityCriteria {
  age_min?: number
  age_max?: number
  gender?: string
  healthy_volunteers?: boolean
  inclusion_criteria?: string[]
  exclusion_criteria?: string[]
}

export interface Trial {
  nct_id: string
  title: string
  brief_summary?: string
  detailed_description?: string
  status: string
  phase?: string
  study_type?: string
  primary_outcome?: string
  secondary_outcomes?: string[]
  enrollment_target?: number
  estimated_completion?: string
  sponsor?: string
  locations?: TrialLocation[]
  contact_info?: ContactInfo
  eligibility_criteria?: EligibilityCriteria
  distance_miles?: number
}

export interface MatchFactors {
  condition_match?: number
  eligibility_fit?: number
  enrollment_status?: number
  geographic_proximity?: number
  phase_appropriateness?: number
}

export interface RankedTrial {
  trial: Trial
  match_score: number
  match_factors?: MatchFactors
  reasoning?: string
}

export interface TrialsSearchResult {
  success: boolean
  trials?: RankedTrial[]
  total_found?: number
  search_metadata?: {
    query_used?: string
    search_time_ms?: number
    patient_location?: PatientData['location']
  }
  error_message?: string
}