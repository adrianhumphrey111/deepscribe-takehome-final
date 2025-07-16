"use client"

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card } from '@/components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Heart, 
  MessageSquare, 
  MapPin, 
  Users, 
  Calendar, 
  Target,
  Phone,
  Mail,
  Building,
  Activity,
  Clock,
  Award
} from 'lucide-react'

interface TrialDetailsDialogProps {
  trial: any
  open: boolean
  onOpenChange: (open: boolean) => void
  onSave: () => void
  onQA: () => void
  isSaved: boolean
}

export function TrialDetailsDialog({ 
  trial, 
  open, 
  onOpenChange, 
  onSave, 
  onQA, 
  isSaved 
}: TrialDetailsDialogProps) {
  if (!trial) return null

  const trialData = trial.trial
  const matchFactors = trial.match_factors
  const matchScore = trial.match_score
  const reasoning = trial.reasoning

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-none sm:max-w-4xl h-screen sm:h-[90vh] w-screen sm:w-auto p-0 sm:rounded-lg rounded-none sm:m-6 m-0 left-0 top-0 translate-x-0 translate-y-0 sm:left-1/2 sm:top-1/2 sm:-translate-x-1/2 sm:-translate-y-1/2 overflow-y-scroll">
        <div className="flex flex-col h-full">
          <DialogHeader className="p-4 sm:p-6 pb-3 sm:pb-4">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
              <div className="flex-1 min-w-0">
                <DialogTitle className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white pr-2 sm:pr-8 line-clamp-2">
                  {trialData.title}
                </DialogTitle>
                <div className="flex flex-wrap items-center gap-1 sm:gap-2 mt-2">
                  <Badge variant="outline">{trialData.nct_id}</Badge>
                  <Badge variant={trialData.status === 'RECRUITING' ? 'default' : 'secondary'}>
                    {trialData.status}
                  </Badge>
                  {trialData.phase && (
                    <Badge variant="outline">
                      {trialData.phase.replace('_', ' ')}
                    </Badge>
                  )}
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {Math.round(matchScore * 100)}% match
                  </Badge>
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-2 sm:space-x-0">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onSave}
                  className={`${isSaved ? 'bg-red-50 border-red-200 text-red-700' : ''} w-full sm:w-auto`}
                >
                  <Heart className={`h-4 w-4 mr-2 ${isSaved ? 'fill-current' : ''}`} />
                  {isSaved ? 'Saved' : 'Save'}
                </Button>
                <Button
                  size="sm"
                  onClick={onQA}
                  className="w-full sm:w-auto"
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  <span className="hidden sm:inline">Ask Questions</span>
                  <span className="sm:hidden">Ask</span>
                </Button>
              </div>
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-hidden px-4 sm:px-6">
            <Tabs defaultValue="overview" className="w-full h-full flex flex-col">
              <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 flex-shrink-0 h-auto">
                <TabsTrigger value="overview" className="text-xs sm:text-sm">Overview</TabsTrigger>
                <TabsTrigger value="eligibility" className="text-xs sm:text-sm">Eligibility</TabsTrigger>
                <TabsTrigger value="locations" className="text-xs sm:text-sm">Locations</TabsTrigger>
                <TabsTrigger value="match" className="text-xs sm:text-sm">
                  <span className="hidden sm:inline">Match Analysis</span>
                  <span className="sm:hidden">Match</span>
                </TabsTrigger>
              </TabsList>
              
              <div className="flex-1 overflow-hidden mt-4">
                <ScrollArea className="h-full">
                  <div className="pb-6">

                    <TabsContent value="overview" className="space-y-6 mt-6">
                      {/* Brief Summary */}
                <Card className="p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                    Study Summary
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                    {trialData.brief_summary || 'No summary available'}
                  </p>
                </Card>

                {/* Key Details */}
                <div className="grid gap-4 md:grid-cols-2">
                  <Card className="p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <Target className="h-5 w-5 text-blue-600" />
                      <h3 className="font-semibold">Study Details</h3>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-300">Study Type:</span>
                        <span className="text-sm font-medium">{trialData.study_type || 'N/A'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-300">Phase:</span>
                        <span className="text-sm font-medium">
                          {trialData.phase?.replace('_', ' ') || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-300">Status:</span>
                        <Badge variant={trialData.status === 'RECRUITING' ? 'default' : 'secondary'} className="text-xs">
                          {trialData.status}
                        </Badge>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <Users className="h-5 w-5 text-green-600" />
                      <h3 className="font-semibold">Enrollment</h3>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-300">Target:</span>
                        <span className="text-sm font-medium">
                          {trialData.enrollment_target || 'N/A'} participants
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-300">Sponsor:</span>
                        <span className="text-sm font-medium">{trialData.sponsor || 'N/A'}</span>
                      </div>
                    </div>
                  </Card>
                </div>

                {/* Outcomes */}
                {(trialData.primary_outcome || trialData.secondary_outcomes?.length > 0) && (
                  <Card className="p-4">
                    <div className="flex items-center space-x-2 mb-3">
                      <Award className="h-5 w-5 text-purple-600" />
                      <h3 className="font-semibold">Study Outcomes</h3>
                    </div>
                    <div className="space-y-3">
                      {trialData.primary_outcome && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            Primary Outcome
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {trialData.primary_outcome}
                          </p>
                        </div>
                      )}
                      {trialData.secondary_outcomes?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            Secondary Outcomes
                          </h4>
                          <ul className="text-sm text-gray-600 dark:text-gray-300 list-disc list-inside space-y-1">
                            {(trialData.secondary_outcomes || []).map((outcome: string, index: number) => (
                              <li key={index}>{outcome}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </Card>
                )}

                {/* Detailed Description */}
                {trialData.detailed_description && (
                  <Card className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                      Detailed Description
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
                      {trialData.detailed_description}
                    </p>
                  </Card>
                )}
                    </TabsContent>

                    <TabsContent value="eligibility" className="space-y-6 mt-6">
                      {trialData.eligibility_criteria ? (
                  <Card className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                      Eligibility Criteria
                    </h3>
                    
                    <div className="space-y-4">
                      {/* Basic Criteria */}
                      <div className="grid gap-4 md:grid-cols-3">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">Age Range</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {trialData.eligibility_criteria.age_min || 'No min'} - {trialData.eligibility_criteria.age_max || 'No max'}
                          </p>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">Gender</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {trialData.eligibility_criteria.gender || 'All'}
                          </p>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">Healthy Volunteers</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {trialData.eligibility_criteria.healthy_volunteers ? 'Yes' : 'No'}
                          </p>
                        </div>
                      </div>

                      <Separator />

                      {/* Inclusion Criteria */}
                      {trialData.eligibility_criteria.inclusion_criteria?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                            Inclusion Criteria
                          </h4>
                          <ul className="text-sm text-gray-600 dark:text-gray-300 list-disc list-inside space-y-1">
                            {(trialData.eligibility_criteria?.inclusion_criteria || []).map((criterion: string, index: number) => (
                              <li key={index}>{criterion}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Exclusion Criteria */}
                      {trialData.eligibility_criteria.exclusion_criteria?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                            Exclusion Criteria
                          </h4>
                          <ul className="text-sm text-gray-600 dark:text-gray-300 list-disc list-inside space-y-1">
                            {(trialData.eligibility_criteria?.exclusion_criteria || []).map((criterion: string, index: number) => (
                              <li key={index}>{criterion}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </Card>
                ) : (
                  <Card className="p-4">
                    <p className="text-center text-gray-500 dark:text-gray-400">
                      No eligibility criteria information available
                    </p>
                  </Card>
                )}
                    </TabsContent>

                    <TabsContent value="locations" className="space-y-4 mt-6">
                      {trialData.locations?.length > 0 ? (
                  <div className="space-y-4">
                    {(trialData.locations || []).map((location: any, index: number) => (
                      <Card key={index} className="p-4">
                        <div className="flex items-start space-x-3">
                          <MapPin className="h-5 w-5 text-blue-600 mt-1" />
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900 dark:text-white">
                              {location.facility || 'Medical Facility'}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              {location.city}, {location.state} {location.country && `(${location.country})`}
                            </p>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <Card className="p-4">
                    <p className="text-center text-gray-500 dark:text-gray-400">
                      No location information available
                    </p>
                  </Card>
                )}

                {/* Contact Information */}
                {trialData.contact_info && (
                  <Card className="p-4">
                    <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                      Contact Information
                    </h3>
                    <div className="space-y-2">
                      {trialData.contact_info.name && (
                        <div className="flex items-center space-x-2">
                          <Users className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{trialData.contact_info.name}</span>
                        </div>
                      )}
                      {trialData.contact_info.phone && (
                        <div className="flex items-center space-x-2">
                          <Phone className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{trialData.contact_info.phone}</span>
                        </div>
                      )}
                      {trialData.contact_info.email && (
                        <div className="flex items-center space-x-2">
                          <Mail className="h-4 w-4 text-gray-500" />
                          <span className="text-sm">{trialData.contact_info.email}</span>
                        </div>
                      )}
                    </div>
                  </Card>
                )}
                    </TabsContent>

                    <TabsContent value="match" className="space-y-6 mt-6">
                      {/* Match Score */}
                <Card className="p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                    Overall Match Score
                  </h3>
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl font-bold text-blue-600">
                      {Math.round(matchScore * 100)}%
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-gray-600 dark:text-gray-300">
                        {reasoning}
                      </div>
                    </div>
                  </div>
                </Card>

                {/* Match Factors */}
                <Card className="p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
                    Match Factors Breakdown
                  </h3>
                  <div className="space-y-3">
                    {Object.entries(matchFactors || {}).map(([factor, score]) => (
                      <div key={factor} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium capitalize">
                            {factor.replace('_', ' ')}
                          </span>
                          <div className={`h-3 w-3 rounded-full ${
                            (score as number) > 0.7 ? 'bg-green-500' : 
                            (score as number) > 0.4 ? 'bg-yellow-500' : 
                            'bg-red-500'
                          }`} />
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                (score as number) > 0.7 ? 'bg-green-500' : 
                                (score as number) > 0.4 ? 'bg-yellow-500' : 
                                'bg-red-500'
                              }`}
                              style={{ width: `${(score as number) * 100}%` }}
                            />
                          </div>
                          <span className="text-sm font-medium">
                            {Math.round((score as number) * 100)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
                    </TabsContent>
                  </div>
                </ScrollArea>
              </div>
            </Tabs>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}