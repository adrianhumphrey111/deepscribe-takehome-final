"use client"

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Heart, MessageSquare, MapPin, Calendar, Users } from 'lucide-react'

interface TrialCardProps {
  trial: any
  onSelect: () => void
  onSave: () => void
  onQA: () => void
  isSaved: boolean
}

export function TrialCard({ trial, onSelect, onSave, onQA, isSaved }: TrialCardProps) {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="space-y-4">
        {/* Header with title and match score */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-base leading-tight text-gray-900 dark:text-white mb-2">
              {trial.trial.title}
            </h4>
          </div>
          <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 font-medium flex-shrink-0">
            {Math.round(trial.match_score * 100)}% match
          </Badge>
        </div>
        
        {/* Trial info badges */}
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline" className="text-xs font-medium">
            {trial.trial.nct_id}
          </Badge>
          <Badge variant={trial.trial.status === 'RECRUITING' ? 'default' : 'secondary'} className="text-xs font-medium">
            {trial.trial.status}
          </Badge>
          {trial.trial.phase && (
            <Badge variant="outline" className="text-xs">
              {trial.trial.phase.replace('_', ' ')}
            </Badge>
          )}
        </div>
        
        {/* Brief summary */}
        <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
          {trial.trial.brief_summary}
        </p>
        
        {/* Reasoning */}
        {trial.reasoning && (
          <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded-lg">
            <div className="text-sm">
              <span className="font-medium text-gray-700 dark:text-gray-300">Reasoning: </span>
              <span className="text-gray-600 dark:text-gray-400">{trial.reasoning}</span>
            </div>
          </div>
        )}
        
        {/* Location and enrollment info */}
        <div className="space-y-2">
          {trial.trial.locations && trial.trial.locations.length > 0 && (
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <MapPin className="h-4 w-4 flex-shrink-0" />
              <span className="font-medium">Locations:</span>
              <span>{trial.trial.locations[0].city}, {trial.trial.locations[0].state}</span>
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
            {Object.entries(trial.match_factors).map(([factor, score]) => (
              <div key={factor} className="text-center">
                <div className="text-xs text-gray-500 mb-1 capitalize">
                  {factor.replace('_', ' ')}:
                </div>
                <div className="flex items-center justify-center gap-1">
                  <div className={`h-2 w-2 rounded-full ${
                    score > 0.7 ? 'bg-green-500' : 
                    score > 0.4 ? 'bg-yellow-500' : 
                    'bg-red-500'
                  }`} />
                  <span className="text-sm font-medium">
                    {Math.round(score * 100)}%
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
            <Button
              variant="outline"
              size="sm"
              onClick={onSave}
              className={`${isSaved ? 'bg-red-50 border-red-200 text-red-700' : ''} px-3`}
            >
              <Heart className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
            </Button>
          </div>
        </div>
      </div>
    </Card>
  )
}