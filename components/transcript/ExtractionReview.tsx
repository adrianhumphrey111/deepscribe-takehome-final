"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { CheckCircle, AlertCircle, Edit3, User, MapPin, Pill, Activity, RefreshCw } from 'lucide-react'
import { ProcessingStatus } from './ProcessingStatus'

interface ExtractionReviewProps {
  extractedData: any
  onConfirm: (data: any) => void
  onStartOver: () => void
  processing: boolean
  progressStep?: string
  progressMessage?: string
  progressPercent?: number
}

export function ExtractionReview({ extractedData, onConfirm, onStartOver, processing, progressStep, progressMessage, progressPercent }: ExtractionReviewProps) {
  const [editedData, setEditedData] = useState(extractedData?.patient_data || {})
  const [isEditing, setIsEditing] = useState(false)

  const handleFieldChange = (field: string, value: any) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleLocationChange = (field: string, value: string) => {
    setEditedData(prev => ({
      ...prev,
      location: {
        ...prev.location,
        [field]: value
      }
    }))
  }

  const handleArrayFieldChange = (field: string, index: number, value: string) => {
    setEditedData(prev => ({
      ...prev,
      [field]: prev[field].map((item, i) => i === index ? value : item)
    }))
  }

  const addArrayItem = (field: string) => {
    setEditedData(prev => ({
      ...prev,
      [field]: [...(prev[field] || []), '']
    }))
  }

  const removeArrayItem = (field: string, index: number) => {
    setEditedData(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index)
    }))
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500'
    if (score >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getConfidenceText = (score: number) => {
    if (score >= 0.8) return 'High'
    if (score >= 0.6) return 'Medium'
    return 'Low'
  }

  const confidenceScores = extractedData?.confidence_scores || {}
  const overallConfidence = confidenceScores.overall || 0

  // Show progress status when processing
  if (processing && progressStep && progressMessage) {
    return (
      <ProcessingStatus 
        message="Searching for clinical trials..."
        progress={progressPercent || 0}
        progressStep={progressStep}
        progressMessage={progressMessage}
      />
    )
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className={`flex h-12 w-12 items-center justify-center rounded-full ${
            extractedData?.success 
              ? 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300'
              : 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300'
          }`}>
            {extractedData?.success ? (
              <CheckCircle className="h-6 w-6" />
            ) : (
              <AlertCircle className="h-6 w-6" />
            )}
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Review Extracted Data
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          {extractedData?.success 
            ? 'Please review and confirm the extracted patient information'
            : 'Please review and complete the patient information below'
          }
        </p>
      </div>

      {/* Overall Status */}
      <Card className={`p-4 ${
        extractedData?.success 
          ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
          : 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className={`h-3 w-3 rounded-full ${getConfidenceColor(overallConfidence)}`} />
              <span className="font-semibold">
                Overall Confidence: {getConfidenceText(overallConfidence)} ({Math.round(overallConfidence * 100)}%)
              </span>
            </div>
            <Badge variant="secondary">
              Provider: {extractedData?.provider_used || 'Unknown'}
            </Badge>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit3 className="mr-2 h-4 w-4" />
            {isEditing ? 'View Mode' : 'Edit Mode'}
          </Button>
        </div>
        
        {extractedData?.error_message && (
          <Alert className="mt-3">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {extractedData.error_message}
            </AlertDescription>
          </Alert>
        )}
      </Card>

      {/* Patient Information */}
      <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
        {/* Demographics */}
        <Card className="p-4 sm:p-6">
          <div className="flex items-center space-x-2 mb-4">
            <User className="h-4 w-4 sm:h-5 sm:w-5 text-blue-600" />
            <h3 className="text-base sm:text-lg font-semibold">Demographics</h3>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="age" className="font-semibold">Age</Label>
                <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-2 mt-1">
                  {isEditing ? (
                    <Input
                      id="age"
                      type="number"
                      value={editedData.age || ''}
                      onChange={(e) => handleFieldChange('age', parseInt(e.target.value) || null)}
                      placeholder="Enter age"
                      className="flex-1"
                    />
                  ) : (
                    <span className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">{editedData.age || 'Not specified'}</span>
                  )}
                  <div className="flex items-center space-x-1 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded self-start">
                    <div className={`h-3 w-3 rounded-full ${getConfidenceColor(confidenceScores.age || 0)}`} />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {Math.round((confidenceScores.age || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="gender" className="font-semibold">Gender</Label>
                <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-2 mt-1">
                  {isEditing ? (
                    <Select value={editedData.gender || ''} onValueChange={(value) => handleFieldChange('gender', value)}>
                      <SelectTrigger className="flex-1">
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MALE">Male</SelectItem>
                        <SelectItem value="FEMALE">Female</SelectItem>
                        <SelectItem value="ALL">All</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <span className="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">{editedData.gender || 'Not specified'}</span>
                  )}
                  <div className="flex items-center space-x-1 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded self-start">
                    <div className={`h-3 w-3 rounded-full ${getConfidenceColor(confidenceScores.gender || 0)}`} />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {Math.round((confidenceScores.gender || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Location */}
        <Card className="p-4 sm:p-6">
          <div className="flex items-center space-x-2 mb-4">
            <MapPin className="h-4 w-4 sm:h-5 sm:w-5 text-green-600" />
            <h3 className="text-base sm:text-lg font-semibold">Location</h3>
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="city" className="font-semibold">City</Label>
                <div className="flex items-center space-x-2 mt-1">
                  {isEditing ? (
                    <Input
                      id="city"
                      value={editedData.location?.city || ''}
                      onChange={(e) => handleLocationChange('city', e.target.value)}
                      placeholder="Enter city"
                    />
                  ) : (
                    <span className="text-lg font-semibold text-gray-900 dark:text-white">{editedData.location?.city || 'Not specified'}</span>
                  )}
                  <div className="flex items-center space-x-1 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                    <div className={`h-3 w-3 rounded-full ${getConfidenceColor(confidenceScores.location || 0)}`} />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {Math.round((confidenceScores.location || 0) * 100)}%
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="state" className="font-semibold">State</Label>
                {isEditing ? (
                  <Input
                    id="state"
                    value={editedData.location?.state || ''}
                    onChange={(e) => handleLocationChange('state', e.target.value)}
                    placeholder="Enter state"
                    className="mt-1"
                  />
                ) : (
                  <span className="text-lg font-semibold text-gray-900 dark:text-white block mt-1">{editedData.location?.state || 'Not specified'}</span>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Medical Information */}
        <Card className="p-4 sm:p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Activity className="h-4 w-4 sm:h-5 sm:w-5 text-red-600" />
            <h3 className="text-base sm:text-lg font-semibold">Medical Information</h3>
          </div>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="primary_diagnosis" className="text-base font-semibold">Primary Diagnosis</Label>
              <div className="flex items-center space-x-3 mt-2">
                {isEditing ? (
                  <Input
                    id="primary_diagnosis"
                    value={editedData.primary_diagnosis || ''}
                    onChange={(e) => handleFieldChange('primary_diagnosis', e.target.value)}
                    placeholder="Enter primary diagnosis"
                    className="text-lg"
                  />
                ) : (
                  <div className="flex-1">
                    <div className="text-lg font-semibold text-gray-900 dark:text-white bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-md border-l-4 border-blue-500">
                      {editedData.primary_diagnosis || 'Not specified'}
                    </div>
                  </div>
                )}
                <div className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-800 px-2 py-1 rounded">
                  <div className={`h-3 w-3 rounded-full ${getConfidenceColor(confidenceScores.primary_diagnosis || 0)}`} />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {Math.round((confidenceScores.primary_diagnosis || 0) * 100)}%
                  </span>
                </div>
              </div>
            </div>

            <div>
              <Label>Conditions</Label>
              <div className="mt-1 space-y-2">
                {(editedData.conditions || []).map((condition, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    {isEditing ? (
                      <>
                        <Input
                          value={condition}
                          onChange={(e) => handleArrayFieldChange('conditions', index, e.target.value)}
                          placeholder="Enter condition"
                        />
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeArrayItem('conditions', index)}
                        >
                          Remove
                        </Button>
                      </>
                    ) : (
                      <Badge variant="secondary">{condition}</Badge>
                    )}
                  </div>
                ))}
                {isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => addArrayItem('conditions')}
                  >
                    Add Condition
                  </Button>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Medications */}
        <Card className="p-4 sm:p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Pill className="h-4 w-4 sm:h-5 sm:w-5 text-orange-600" />
            <h3 className="text-base sm:text-lg font-semibold">Medications</h3>
          </div>
          
          <div className="space-y-2">
            {(editedData.medications || []).map((medication, index) => (
              <div key={index} className="flex items-center space-x-2">
                {isEditing ? (
                  <>
                    <Input
                      value={medication}
                      onChange={(e) => handleArrayFieldChange('medications', index, e.target.value)}
                      placeholder="Enter medication"
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeArrayItem('medications', index)}
                    >
                      Remove
                    </Button>
                  </>
                ) : (
                  <Badge variant="outline">{medication}</Badge>
                )}
              </div>
            ))}
            {isEditing && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => addArrayItem('medications')}
              >
                Add Medication
              </Button>
            )}
          </div>
        </Card>
      </div>

      <Separator />

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-0">
        <Button
          variant="outline"
          onClick={onStartOver}
          disabled={processing}
          className="w-full sm:w-auto"
        >
          <RefreshCw className="mr-2 h-4 w-4" />
          Start Over
        </Button>
        
        <Button
          onClick={() => onConfirm(editedData)}
          disabled={processing}
          className="w-full sm:w-auto sm:px-8"
        >
          {processing ? (
            <>
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
              <span className="hidden sm:inline">Searching Trials...</span>
              <span className="sm:hidden">Searching...</span>
            </>
          ) : (
            <>
              <CheckCircle className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">Find Clinical Trials</span>
              <span className="sm:hidden">Find Trials</span>
            </>
          )}
        </Button>
      </div>
    </div>
  )
}