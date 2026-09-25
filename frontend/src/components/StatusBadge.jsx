function StatusBadge({ status }) {
  const tone = status === 'Valid Claim' ? 'valid' : status === 'Invalid Claim' ? 'invalid' : 'review'
  return <span className={`status-badge ${tone}`}><span className="status-dot" />{status}</span>
}

export default StatusBadge
