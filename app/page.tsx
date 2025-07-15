"use client"

import { useState } from 'react'
import { TranscriptInput } from '@/components/transcript/TranscriptInput'
import { ExtractionReview } from '@/components/transcript/ExtractionReview'
import { TrialsList } from '@/components/trials/TrialsList'
import { ProcessingStatus } from '@/components/transcript/ProcessingStatus'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Stethoscope, Users, Target } from 'lucide-react'

export default function Home() {
  const [currentStep, setCurrentStep] = useState<'input' | 'processing' | 'review' | 'results'>('input')
  const [transcript, setTranscript] = useState('')
  const [extractedData, setExtractedData] = useState<any>(null)
  const [trials, setTrials] = useState<any[]>([])
  const [processing, setProcessing] = useState(false)
  const [progressStep, setProgressStep] = useState('')
  const [progressMessage, setProgressMessage] = useState('')
  const [progressPercent, setProgressPercent] = useState(0)

  const handleTranscriptSubmit = async (transcriptText: string) => {
    setTranscript(transcriptText)
    setCurrentStep('processing')
    setProcessing(true)
    // Don't set progressStep/progressMessage for transcript processing
    // The ProcessingStatus component will use its default transcript processing flow

    try {
      // Extract patient data
      const extractResponse = await fetch('/api/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript: transcriptText })
      })

      const extractResult = await extractResponse.json()

      if (extractResult.success) {
        setExtractedData(extractResult)
        setCurrentStep('review')
      } else {
        // Handle extraction failure
        setExtractedData(extractResult)
        setCurrentStep('review')
      }
    } catch (error) {
      console.error('Error during extraction:', error)
      setCurrentStep('input')
    } finally {
      setProcessing(false)
      setProgressStep('')
      setProgressMessage('')
      setProgressPercent(0)
    }
  }

  const handleDataConfirm = async (confirmedData: any) => {
    setProcessing(true)
    setProgressPercent(0)
    setProgressStep('Searching clinical trials...')
    setProgressMessage('Finding relevant trials from ClinicalTrials.gov database.')

    try {
      // Step 1: Initial search setup
      setProgressPercent(10)
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setProgressPercent(20)
      setProgressStep('Analyzing eligibility...')
      setProgressMessage('Our AI is evaluating each trial against patient criteria. This may take up to 2 minutes.')

      // Step 2: Make the actual API call
      setProgressPercent(30)
      const searchResponse = await fetch('/api/trials/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_data: confirmedData })
      })

      // Step 3: Processing response
      setProgressPercent(80)
      const searchResult = await searchResponse.json()

      setProgressPercent(90)
      setProgressStep('Ranking matches...')
      setProgressMessage('Organizing results by relevance and match quality.')

      // Step 4: Final processing
      await new Promise(resolve => setTimeout(resolve, 500))
      setProgressPercent(100)

      if (searchResult.success) {
        setTrials(searchResult.trials)
        setCurrentStep('results')
      } else {
        console.error('Trial search failed:', searchResult.error_message)
        setTrials([])
        setCurrentStep('results')
      }
    } catch (error) {
      console.error('Error during trial search:', error)
      setTrials([])
      setCurrentStep('results')
    } finally {
      setProcessing(false)
      setProgressStep('')
      setProgressMessage('')
      setProgressPercent(0)
    }
  }

  const handleStartOver = () => {
    setCurrentStep('input')
    setTranscript('')
    setExtractedData(null)
    setTrials([])
    setProcessing(false)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-md dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4 sm:py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
                <Stethoscope className="h-4 w-4 sm:h-6 sm:w-6" />
              </div>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white">
                  Clinical Trials Matcher
                </h1>
                <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-300 hidden sm:block">
                  AI-powered trial matching for healthcare providers
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 sm:space-x-4">
              <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
                <Users className="h-4 w-4" />
                <span>Healthcare Provider</span>
              </div>
              <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 text-xs">
                <Target className="mr-1 h-3 w-3" />
                Active
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-6xl">
          {/* Progress Steps */}
          <div className="mb-6 sm:mb-8">
            <div className="flex items-center justify-between overflow-x-auto pb-2">
              {[
                { step: 'input', label: 'Input Transcript', icon: '📝' },
                { step: 'processing', label: 'Processing', icon: '⚡' },
                { step: 'review', label: 'Review Data', icon: '👀' },
                { step: 'results', label: 'Trial Results', icon: '🎯' }
              ].map((item, index) => (
                <div key={item.step} className="flex items-center flex-shrink-0">
                  <div className={`flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-full border-2 ${
                    currentStep === item.step 
                      ? 'border-blue-600 bg-blue-600 text-white' 
                      : index < ['input', 'processing', 'review', 'results'].indexOf(currentStep)
                      ? 'border-green-500 bg-green-500 text-white'
                      : 'border-gray-300 bg-white text-gray-400'
                  }`}>
                    <span className="text-xs sm:text-sm">{item.icon}</span>
                  </div>
                  <div className="ml-1 sm:ml-2 hidden sm:block">
                    <p className={`text-xs sm:text-sm font-medium ${
                      currentStep === item.step ? 'text-blue-600' : 'text-gray-600'
                    }`}>
                      {item.label}
                    </p>
                  </div>
                  {index < 3 && (
                    <div className={`mx-2 sm:mx-4 h-px w-8 sm:w-16 ${
                      index < ['input', 'processing', 'review', 'results'].indexOf(currentStep)
                        ? 'bg-green-500'
                        : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              ))}
            </div>
            
            {/* Mobile step indicator */}
            <div className="sm:hidden text-center mt-2">
              <p className="text-sm font-medium text-gray-600">
                {[
                  { step: 'input', label: 'Input Transcript' },
                  { step: 'processing', label: 'Processing' },
                  { step: 'review', label: 'Review Data' },
                  { step: 'results', label: 'Trial Results' }
                ].find(item => item.step === currentStep)?.label}
              </p>
            </div>
          </div>

          {/* Step Content */}
          <div className="space-y-8">
            {currentStep === 'input' && (
              <Card className="p-8">
                <TranscriptInput onSubmit={handleTranscriptSubmit} />
              </Card>
            )}

            {currentStep === 'processing' && (
              <Card className="p-8">
                <ProcessingStatus 
                  message="Analyzing transcript and extracting patient information..."
                  progress={65}
                />
              </Card>
            )}

            {currentStep === 'review' && extractedData && (
              <Card className="p-8">
                <ExtractionReview 
                  extractedData={extractedData}
                  onConfirm={handleDataConfirm}
                  onStartOver={handleStartOver}
                  processing={processing}
                  progressStep={progressStep}
                  progressMessage={progressMessage}
                  progressPercent={progressPercent}
                />
              </Card>
            )}

            {currentStep === 'results' && (
              <TrialsList 
                trials={trials}
                onStartOver={handleStartOver}
                extractedData={extractedData}
              />
            )}
          </div>
        </div>
      </main>
    </div>
  )
}