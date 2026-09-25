import { useState } from 'react'
import ClaimForm from '../components/ClaimForm'
import ResultCard from '../components/ResultCard'
import { analyzeClaim } from '../services/api'

function ClaimAnalysis({ onAnalysis, result }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (claim) => {
    setLoading(true)
    setError('')
    try {
      const analysis = await analyzeClaim(claim)
      onAnalysis(analysis)
    } catch (requestError) {
      const message = requestError.response?.data?.detail || 'The claim could not be analyzed. Check the backend connection and try again.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return <div className="analysis-layout"><div><div className="section-heading"><p className="eyebrow">NEW ANALYSIS</p><h2>Analyze claim</h2><p>Enter the information available on the submitted claim.</p></div>{error && <p className="form-error" role="alert">{error}</p>}<ClaimForm onSubmit={handleSubmit} loading={loading} /></div><ResultCard result={result} /></div>
}

export default ClaimAnalysis
