import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import PredictionResult from '../components/PredictionResult.jsx'

const sampleResult = {
  prediction: {
    id: 'abc123',
    plant: 'Tomato',
    disease: 'Tomato Early Blight',
    is_healthy: false,
    confidence: 94.72,
    image_name: 'leaf.jpg',
    thumbnail: null,
    processing_time: 0.42,
    model_name: 'SVM (RBF)',
    top_predictions: [
      { label: 'Tomato Early Blight', confidence: 94.72 },
      { label: 'Tomato Late Blight', confidence: 3.1 },
    ],
    created_at: '2026-09-22T10:00:00Z',
  },
  recommendation: {
    description: 'Fungal disease caused by Alternaria solani.',
    symptoms: ['Brown spots with concentric rings'],
    prevention: ['Mulch to stop soil splash'],
    treatment: ['Apply fungicides'],
    severity: 'medium',
  },
}

describe('PredictionResult', () => {
  it('renders plant, disease and confidence', () => {
    render(<PredictionResult result={sampleResult} imageUrl="blob:x" onAnalyzeAnother={() => {}} />)

    expect(screen.getByText('Tomato')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Tomato Early Blight' })).toBeInTheDocument()
    expect(screen.getAllByText('94.72%').length).toBeGreaterThan(0)
    expect(screen.getByText(/medium severity/i)).toBeInTheDocument()
  })

  it('renders agronomic guidance sections', () => {
    render(<PredictionResult result={sampleResult} imageUrl="blob:x" onAnalyzeAnother={() => {}} />)

    expect(screen.getByText('Symptoms')).toBeInTheDocument()
    expect(screen.getByText('Prevention')).toBeInTheDocument()
    expect(screen.getByText('Treatment')).toBeInTheDocument()
    expect(screen.getByText('Brown spots with concentric rings')).toBeInTheDocument()
  })

  it('calls onAnalyzeAnother from the CTA', () => {
    const onAnalyzeAnother = vi.fn()
    render(
      <PredictionResult result={sampleResult} imageUrl="blob:x" onAnalyzeAnother={onAnalyzeAnother} />,
    )
    screen.getByText('Analyze Another Image').click()
    expect(onAnalyzeAnother).toHaveBeenCalledTimes(1)
  })
})
