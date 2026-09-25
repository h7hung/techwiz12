import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import StatusBadge from '../components/StatusBadge'
import { getClaims } from '../services/api'

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

function Dashboard() {
  const [claims, setClaims] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getClaims()
      .then((response) => setClaims(response.items || []))
      .catch(() => setError('Claims could not be loaded right now.'))
      .finally(() => setLoading(false))
  }, [])

  const counts = useMemo(() => ({
    total: claims.length,
    valid: claims.filter((claim) => claim.analyses?.at(-1)?.final_decision === 'Valid Claim').length,
    invalid: claims.filter((claim) => claim.analyses?.at(-1)?.final_decision === 'Invalid Claim').length,
    review: claims.filter((claim) => claim.analyses?.at(-1)?.final_decision === 'Manual Review').length,
  }), [claims])

  return <div className="page-stack">
    <div className="page-intro"><div><p className="eyebrow">OVERVIEW</p><h2>Dashboard</h2><p className="page-copy">Warranty claim overview</p></div><Link className="primary-button" to="/analyze">Analyze new claim <span aria-hidden="true">→</span></Link></div>
    <section className="stats-grid" aria-label="Claim summary">
      <div className="stat-card"><span>Total claims</span><strong>{counts.total}</strong><small>{counts.total ? 'Claims in SQLite' : 'No data yet'}</small></div>
      <div className="stat-card accent-valid"><span>Valid claims</span><strong>{counts.valid}</strong><small>{counts.valid ? 'Final decisions' : 'No data yet'}</small></div>
      <div className="stat-card accent-invalid"><span>Invalid claims</span><strong>{counts.invalid}</strong><small>{counts.invalid ? 'Final decisions' : 'No data yet'}</small></div>
      <div className="stat-card accent-review"><span>Manual review</span><strong>{counts.review}</strong><small>{counts.review ? 'Needs attention' : 'No data yet'}</small></div>
    </section>
    <section className="content-panel"><div className="panel-heading"><div><p className="eyebrow">ACTIVITY</p><h2>Recent claims</h2></div><Link to="/claims" className="text-link">View all claims →</Link></div>{error && <p className="form-error" role="alert">{error}</p>}{loading ? <p className="loading-state">Loading claims...</p> : claims.length === 0 ? <div className="empty-state"><h3>No claims yet</h3><p>Create your first claim to start the analysis.</p><Link className="secondary-button" to="/analyze">Analyze claim</Link></div> : <div className="table-wrap"><table><thead><tr><th>Claim ID</th><th>Product</th><th>Decision</th><th>Created</th></tr></thead><tbody>{claims.slice(0, 5).map((claim) => { const analysis = claim.analyses?.at(-1); return <tr key={claim.claim_id}><td className="strong-cell">{claim.claim_id}</td><td>{[claim.product_category, claim.brand].filter(Boolean).join(' · ') || '—'}</td><td>{analysis ? <StatusBadge status={analysis.final_decision} /> : <span className="muted-cell">Not analyzed</span>}</td><td className="muted-cell">{formatDate(claim.created_at)}</td></tr> })}</tbody></table></div>}</section>
  </div>
}

export default Dashboard
