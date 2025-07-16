"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ScrollArea } from '@/components/ui/scroll-area'
import { TrialCard } from '@/components/trials/TrialCard'
import { TrialDetailsDialog } from '@/components/trials/TrialDetailsDialog'
import { TrialQADialog } from '@/components/trials/TrialQADialog'
import { Search, AlertCircle, Target, RefreshCw, Heart, MessageSquare, MapPin, Users, ChevronDown, ChevronUp } from 'lucide-react'

interface TopMatchCardProps {
  trial: any
  rank: number
  onSelect: () => void
  onSave: () => void
  onQA: () => void
  isSaved: boolean
}

function TopMatchCard({ trial, rank, onSelect, onSave, onQA, isSaved }: TopMatchCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1: return 'bg-yellow-500'
      case 2: return 'bg-gray-400'
      case 3: return 'bg-orange-600'
      default: return 'bg-gray-500'
    }
  }

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="space-y-4">
        {/* Header with rank and match score */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <div className={`flex h-8 w-8 items-center justify-center rounded-full text-white text-sm font-bold ${getRankColor(rank)} flex-shrink-0`}>
              {rank}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white leading-tight mb-2">
                {trial.trial.title}
              </h3>
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 font-medium">
                  {Math.round(trial.match_score * 100)}% match
                </Badge>
                <Badge variant="outline" className="text-xs">
                  {trial.trial.nct_id}
                </Badge>
                <Badge variant={trial.trial.status === 'RECRUITING' ? 'default' : 'secondary'} className="text-xs">
                  {trial.trial.status}
                </Badge>
                {trial.trial.phase && (
                  <Badge variant="outline" className="text-xs">
                    {trial.trial.phase.replace('_', ' ')}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onSave}
            className={`${isSaved ? 'bg-red-50 border-red-200 text-red-700' : ''} flex-shrink-0`}
          >
            <Heart className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
          </Button>
        </div>

        {/* Brief summary with expand/collapse */}
        <div className="space-y-2">
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
            {isExpanded ? trial.trial.brief_summary : truncateText(trial.trial.brief_summary, 150)}
          </p>
          {trial.trial.brief_summary.length > 150 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="text-blue-600 hover:text-blue-800 p-0 h-auto font-normal"
            >
              {isExpanded ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-1" />
                  Show Less
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-1" />
                  See More
                </>
              )}
            </Button>
          )}
        </div>

        {/* Reasoning */}
        <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
          <div className="text-sm">
            <span className="font-medium text-gray-700 dark:text-gray-300">Reasoning: </span>
            <span className="text-gray-600 dark:text-gray-400">{trial.reasoning}</span>
          </div>
        </div>

        {/* Location and enrollment info */}
        <div className="space-y-2">
          {trial.trial.locations && trial.trial.locations.length > 0 && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <MapPin className="h-4 w-4 flex-shrink-0" />
              <span className="font-medium">Locations:</span>
              <div className="flex flex-wrap gap-1">
                {(trial.trial.locations || []).slice(0, 3).map((location: any, locIndex: number) => (
                  <Badge key={locIndex} variant="outline" className="text-xs">
                    {location.city}, {location.state}
                  </Badge>
                ))}
                {trial.trial.locations.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{trial.trial.locations.length - 3} more
                  </Badge>
                )}
              </div>
            </div>
          )}
          {trial.trial.enrollment_target && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <Users className="h-4 w-4 flex-shrink-0" />
              <span>{trial.trial.enrollment_target} participants</span>
            </div>
          )}
        </div>

        {/* Match factors */}
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(trial.match_factors || {}).map(([factor, score]) => (
              <div key={factor} className="text-center">
                <div className="text-xs text-gray-500 mb-1 capitalize">
                  {factor.replace('_', ' ')}:
                </div>
                <div className="flex items-center justify-center gap-1">
                  <div className={`h-2 w-2 rounded-full ${
                    (score as number) > 0.7 ? 'bg-green-500' : 
                    (score as number) > 0.4 ? 'bg-yellow-500' : 
                    'bg-red-500'
                  }`} />
                  <span className="text-sm font-medium">
                    {Math.round((score as number) * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
          
          {/* Action buttons */}
          <div className="flex items-center gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onQA}
              className="flex-1"
            >
              <MessageSquare className="h-4 w-4 mr-2" />
              Ask Questions
            </Button>
            <Button
              size="sm"
              onClick={onSelect}
              className="flex-1"
            >
              View Details
            </Button>
          </div>
        </div>
      </div>
    </Card>
  )
}

interface TrialsListProps {
  trials: any[]
  onStartOver: () => void
  extractedData: any
}

export function TrialsList({ trials, onStartOver, extractedData }: TrialsListProps) {
  const [selectedTrial, setSelectedTrial] = useState<any>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [showQA, setShowQA] = useState(false)
  const [savedTrials, setSavedTrials] = useState<Set<string>>(new Set())

  const handleTrialSelect = (trial: any) => {
    setSelectedTrial(trial)
    setShowDetails(true)
  }

  const handleQAOpen = (trial: any) => {
    setSelectedTrial(trial)
    setShowQA(true)
  }

  const handleSaveTrial = (trialId: string) => {
    setSavedTrials(prev => {
      const newSet = new Set(prev)
      if (newSet.has(trialId)) {
        newSet.delete(trialId)
      } else {
        newSet.add(trialId)
      }
      return newSet
    })
  }

  const hasResults = trials && trials.length > 0
  const patientLocation = extractedData?.patient_data?.location

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className={`flex h-12 w-12 items-center justify-center rounded-full ${
            hasResults 
              ? 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300'
              : 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300'
          }`}>
            {hasResults ? (
              <Target className="h-6 w-6" />
            ) : (
              <Search className="h-6 w-6" />
            )}
          </div>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
          Clinical Trial Results
        </h2>
        <p className="mt-2 text-sm sm:text-base text-gray-600 dark:text-gray-300">
          {hasResults 
            ? `Found ${trials.length} matching clinical trial${trials.length !== 1 ? 's' : ''}`
            : 'No matching trials found for the current patient profile'
          }
        </p>
      </div>

      {/* Results Summary */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
            <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
              <span className="font-medium">Search criteria:</span> {' '}
              <span className="break-words">{extractedData?.patient_data?.primary_diagnosis || 'General search'}</span>
            </div>
            {patientLocation && (
              <div className="text-xs sm:text-sm text-gray-600 dark:text-gray-300">
                <span className="font-medium">Location:</span> {' '}
                {patientLocation.city}, {patientLocation.state}
              </div>
            )}
          </div>
          <div className="flex items-center justify-between sm:justify-end space-x-2">
            <Badge variant="outline" className="text-xs">
              {trials.length} result{trials.length !== 1 ? 's' : ''}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={onStartOver}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">New Search</span>
              <span className="sm:hidden">New</span>
            </Button>
          </div>
        </div>
      </Card>

      {/* No Results State */}
      {!hasResults && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            No clinical trials were found matching the current patient profile. 
            This could be due to specific eligibility criteria, geographic limitations, 
            or the nature of the medical condition. Consider:
            <ul className="mt-2 ml-4 list-disc space-y-1">
              <li>Expanding the search to nearby cities or states</li>
              <li>Checking for trials with broader eligibility criteria</li>
              <li>Looking for trials in related medical specialties</li>
              <li>Contacting research coordinators for additional opportunities</li>
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Trials List */}
      {hasResults && (
        <div className="space-y-4">
          {/* Top Matches */}
          {trials.slice(0, 3).map((rankedTrial, index) => (
            <TopMatchCard 
              key={rankedTrial.trial.nct_id}
              trial={rankedTrial}
              rank={index + 1}
              onSelect={() => handleTrialSelect(rankedTrial)}
              onSave={() => handleSaveTrial(rankedTrial.trial.nct_id)}
              onQA={() => handleQAOpen(rankedTrial)}
              isSaved={savedTrials.has(rankedTrial.trial.nct_id)}
            />
          ))}

          {/* Additional Matches */}
          {trials.length > 3 && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Additional Matches</h3>
              <div className="space-y-3">
                {trials.slice(3).map((rankedTrial) => (
                  <TrialCard 
                    key={rankedTrial.trial.nct_id}
                    trial={rankedTrial}
                    onSelect={() => handleTrialSelect(rankedTrial)}
                    onSave={() => handleSaveTrial(rankedTrial.trial.nct_id)}
                    onQA={() => handleQAOpen(rankedTrial)}
                    isSaved={savedTrials.has(rankedTrial.trial.nct_id)}
                  />
                ))}
              </div>
            </Card>
          )}
        </div>
      )}

      {/* Dialogs */}
      <TrialDetailsDialog
        trial={selectedTrial}
        open={showDetails}
        onOpenChange={setShowDetails}
        onSave={() => selectedTrial && handleSaveTrial(selectedTrial.trial.nct_id)}
        onQA={() => {
          setShowDetails(false)
          setShowQA(true)
        }}
        isSaved={selectedTrial ? savedTrials.has(selectedTrial.trial.nct_id) : false}
      />

      <TrialQADialog
        trial={selectedTrial}
        open={showQA}
        onOpenChange={setShowQA}
        patientData={extractedData?.patient_data}
      />
    </div>
  )
}