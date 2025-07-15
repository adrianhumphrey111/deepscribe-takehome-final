"use client"

import { useEffect, useState } from 'react'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Brain, Search, Target, Sparkles, Clock } from 'lucide-react'

interface ProcessingStatusProps {
  message: string
  progress: number
  progressStep?: string
  progressMessage?: string
}

export function ProcessingStatus({ message, progress, progressStep, progressMessage }: ProcessingStatusProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [animatedProgress, setAnimatedProgress] = useState(0)

  // Use dynamic progress info if provided, otherwise use default steps
  const isTrialSearch = progressStep && progressMessage
  
  const steps = isTrialSearch ? [
    {
      icon: Search,
      title: 'Searching Trials',
      description: 'Finding relevant trials from ClinicalTrials.gov database',
      duration: 1000
    },
    {
      icon: Brain,
      title: 'AI Analysis',
      description: 'Evaluating each trial against patient criteria',
      duration: 3000
    },
    {
      icon: Target,
      title: 'Ranking Results',
      description: 'Organizing trials by relevance and match quality',
      duration: 1000
    }
  ] : [
    {
      icon: Brain,
      title: 'AI Analysis',
      description: 'Analyzing transcript with advanced language models',
      duration: 2000
    },
    {
      icon: Search,
      title: 'Data Extraction',
      description: 'Extracting patient demographics and medical information',
      duration: 1500
    },
    {
      icon: Target,
      title: 'Quality Check',
      description: 'Validating extracted data and confidence scores',
      duration: 1000
    },
    {
      icon: Sparkles,
      title: 'Finalizing',
      description: 'Preparing results for review',
      duration: 500
    }
  ]

  useEffect(() => {
    // Animate progress bar
    const timer = setInterval(() => {
      setAnimatedProgress(prev => {
        if (prev >= progress) {
          clearInterval(timer)
          return progress
        }
        return prev + 2
      })
    }, 50)

    return () => clearInterval(timer)
  }, [progress])

  useEffect(() => {
    // For trial search, determine current step based on progress
    if (isTrialSearch) {
      if (progressStep?.includes('Searching')) {
        setCurrentStep(0)
      } else if (progressStep?.includes('Analyzing')) {
        setCurrentStep(1)
      } else if (progressStep?.includes('Ranking')) {
        setCurrentStep(2)
      }
    } else {
      // For transcript processing, cycle through steps
      const stepTimer = setInterval(() => {
        setCurrentStep(prev => (prev + 1) % steps.length)
      }, 2000)

      return () => clearInterval(stepTimer)
    }
  }, [isTrialSearch, progressStep])

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="flex items-center justify-center mb-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300 animate-pulse">
            <Brain className="h-6 w-6" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {isTrialSearch ? progressStep : 'Processing Transcript'}
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          {isTrialSearch ? progressMessage : message}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Progress
          </span>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {animatedProgress}%
          </span>
        </div>
        <Progress value={animatedProgress} className="h-2" />
      </div>

      {/* Processing Steps */}
      <div className="grid gap-4 md:grid-cols-2">
        {steps.map((step, index) => (
          <Card 
            key={index}
            className={`p-4 transition-all duration-300 ${
              index === currentStep 
                ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                : 'opacity-60'
            }`}
          >
            <div className="flex items-start space-x-3">
              <div className={`flex h-8 w-8 items-center justify-center rounded-full ${
                index === currentStep 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-400 dark:bg-gray-800'
              }`}>
                <step.icon className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {step.title}
                  </h3>
                  {index === currentStep && (
                    <Badge variant="secondary" className="text-xs">
                      <Clock className="mr-1 h-3 w-3" />
                      Active
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  {step.description}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* AI Provider Info */}
      <Card className="bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 dark:from-purple-900/20 dark:to-blue-900/20 dark:border-purple-800">
        <div className="p-4">
          <div className="flex items-center space-x-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100 text-purple-600 dark:bg-purple-800 dark:text-purple-200">
              <Brain className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-semibold text-purple-900 dark:text-purple-100">
                AI-Powered Analysis
              </h3>
              <p className="text-sm text-purple-800 dark:text-purple-200">
                {isTrialSearch 
                  ? "Using advanced language models to match patients with relevant clinical trials"
                  : "Using advanced language models to ensure accurate medical data extraction"
                }
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}