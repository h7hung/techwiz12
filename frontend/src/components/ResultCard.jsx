import StatusBadge from './StatusBadge'

function ResultCard({ result }) {
  if (!result) {
    return (
      <section className="result-card empty-result">
        <div className="empty-icon">✓</div>
        <h2>Decision will appear here</h2>
        <p>Complete the claim form to see the ML prediction and policy checks.</p>
      </section>
    )
  }

  return (
    <section className="result-card">
      <div className="result-heading">
        <div>
          <p className="eyebrow">ANALYSIS RESULT</p>
          <h2>Claim decision</h2>
        </div>
        <StatusBadge status={result.finalDecision} />
      </div>
      <div className="decision-panel">
        <span className="decision-label">Final decision</span>
        <strong>{result.finalDecision}</strong>
        <span>Based on model prediction and policy checks</span>
      </div>
      <div className="result-grid">
        <div><span>ML prediction</span><strong>{result.mlPrediction}</strong></div>
        <div><span>ML confidence</span><strong>{Math.round(result.confidence * 100)}%</strong></div>
        <div><span>Rule triggered</span><strong>{result.ruleTriggered ? 'Yes' : 'No'}</strong></div>
      </div>
      <div className="reason-block">
        <span>Decision reasons</span>
        {result.reasons.length ? <ul>{result.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul> : <p>No additional policy concerns.</p>}
      </div>
    </section>
  )
}

export default ResultCard
