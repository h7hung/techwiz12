import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import StatusBadge from '../components/StatusBadge'
import { deleteClaim, getClaims } from '../services/api'

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

function Claims() {
  const [claims, setClaims] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadClaims = () => {
    setLoading(true)
    getClaims()
      .then((response) => setClaims(response.items || []))
      .catch(() => setError('Claims could not be loaded right now.'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { loadClaims() }, [])

  const handleDelete = async (claimId) => {
    if (!window.confirm(`Delete claim ${claimId}?`)) return
    try {
      await deleteClaim(claimId)
      loadClaims()
    } catch {
      setError('The claim could not be deleted.')
    }
  }

  return <div className="page-stack"><div className="page-intro"><div><p className="eyebrow">CLAIM REGISTER</p><h2>Claims</h2><p className="page-copy">Review claims stored in the current workspace.</p></div><Link className="primary-button" to="/analyze">Analyze claim <span aria-hidden="true">→</span></Link></div><section className="content-panel"><div className="panel-heading"><div><h2>All claims</h2><p className="panel-subtitle">{claims.length} {claims.length === 1 ? 'claim' : 'claims'} in SQLite</p></div></div>{error && <p className="form-error" role="alert">{error}</p>}{loading ? <p className="loading-state">Loading claims...</p> : claims.length === 0 ? <div className="empty-state"><h3>No claims found</h3><p>Create your first claim to start the analysis.</p><Link className="secondary-button" to="/analyze">Analyze claim</Link></div> : <div className="table-wrap"><table><thead><tr><th>Claim ID</th><th>Customer</th><th>Product</th><th>Warranty</th><th>Decision</th><th>Created</th><th>Action</th></tr></thead><tbody>{claims.map((claim) => { const analysis = claim.analyses?.at(-1); return <tr key={claim.claim_id}><td className="strong-cell">{claim.claim_id}</td><td>{claim.customer_id || '—'}</td><td>{[claim.product_category, claim.brand].filter(Boolean).join(' · ') || '—'}</td><td>{claim.warranty_status || '—'}</td><td>{analysis ? <StatusBadge status={analysis.final_decision} /> : <span className="muted-cell">Not analyzed</span>}</td><td className="muted-cell">{formatDate(claim.created_at)}</td><td><button className="table-button danger-button" onClick={() => handleDelete(claim.claim_id)}>Delete</button></td></tr> })}</tbody></table></div>}</section></div>
}

export default Claims
