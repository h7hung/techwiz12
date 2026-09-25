import { useState } from 'react'

const initialClaim = {
  claimId: '', customerId: '', claimDate: '', productCategory: '', brand: '', modelNumber: '', serialNumber: '', purchaseDate: '', warrantyExpiryDate: '', warrantyStatus: '', faultType: '', faultCovered: '', damageType: '', claimAmount: '', requiredDocumentsComplete: '', purchaseProofAvailable: '', ocrConfidence: '', claimSubmissionChannel: '',
}

const sections = [
  { title: 'Claim Information', fields: [['claimId', 'Claim ID', 'text'], ['customerId', 'Customer ID', 'text'], ['claimDate', 'Claim Date', 'date']] },
  { title: 'Product Information', fields: [['productCategory', 'Product Category', 'text'], ['brand', 'Brand', 'text'], ['modelNumber', 'Model Number', 'text'], ['serialNumber', 'Serial Number', 'text']] },
  { title: 'Warranty', fields: [['purchaseDate', 'Purchase Date', 'date'], ['warrantyExpiryDate', 'Warranty End Date', 'date'], ['warrantyStatus', 'Warranty Status', 'select'], ['faultCovered', 'Fault Covered', 'select']] },
  { title: 'Claim Details', fields: [['faultType', 'Fault / Damage', 'text'], ['damageType', 'Damage Type', 'text'], ['claimAmount', 'Claim Amount', 'number']] },
  { title: 'Evidence', fields: [['requiredDocumentsComplete', 'Required Documents', 'select'], ['purchaseProofAvailable', 'Purchase Proof', 'select'], ['ocrConfidence', 'OCR Confidence', 'number'], ['claimSubmissionChannel', 'Submission Channel', 'text']] },
]

const selectOptions = {
  warrantyStatus: ['Active', 'Expired'],
  faultCovered: ['Yes', 'No'],
  requiredDocumentsComplete: ['Yes', 'No'],
  purchaseProofAvailable: ['Yes', 'No'],
}

function ClaimForm({ onSubmit, loading }) {
  const [claim, setClaim] = useState(initialClaim)
  const update = (key, value) => setClaim((current) => ({ ...current, [key]: value }))

  return (
    <form className="claim-form" onSubmit={(event) => { event.preventDefault(); onSubmit(claim) }}>
      {sections.map((section) => (
        <fieldset key={section.title} className="form-section">
          <legend>{section.title}</legend>
          <div className="field-grid">
            {section.fields.map(([key, label, type]) => (
              <label key={key} className="field">
                <span>{label}</span>
                {type === 'select' ? <select value={claim[key]} onChange={(event) => update(key, event.target.value)}><option value="">Select</option>{selectOptions[key].map((option) => <option key={option}>{option}</option>)}</select> : <input type={type} value={claim[key]} onChange={(event) => update(key, event.target.value)} />}
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <div className="form-actions"><span>Required fields are saved before analysis.</span><button className="primary-button" disabled={loading || !claim.claimId}>{loading ? 'Analyzing...' : 'Analyze Claim'} <span aria-hidden="true">→</span></button></div>
    </form>
  )
}

export default ClaimForm
