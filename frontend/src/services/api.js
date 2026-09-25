import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

function toApiClaim(claim) {
  return {
    claim_id: claim.claimId,
    customer_id: claim.customerId || null,
    product_category: claim.productCategory || null,
    brand: claim.brand || null,
    model_number: claim.modelNumber || null,
    serial_number: claim.serialNumber || null,
    purchase_date: claim.purchaseDate || null,
    claim_date: claim.claimDate || null,
    warranty_status: claim.warrantyStatus || null,
    warranty_expiry_date: claim.warrantyExpiryDate || null,
    warranty_remaining_days: claim.warrantyRemainingDays ? Number(claim.warrantyRemainingDays) : null,
    warranty_duration_months: claim.warrantyDurationMonths ? Number(claim.warrantyDurationMonths) : null,
    extended_warranty: claim.extendedWarranty || null,
    fault_type: claim.faultType || null,
    fault_covered: claim.faultCovered || null,
    damage_type: claim.damageType || null,
    claim_amount: claim.claimAmount ? Number(claim.claimAmount) : null,
    claim_reporting_within_period: claim.claimReportingWithinPeriod || null,
    repair_count: claim.repairCount ? Number(claim.repairCount) : null,
    replacement_within_warranty: claim.replacementWithinWarranty || null,
    required_documents_complete: claim.requiredDocumentsComplete || null,
    purchase_proof_available: claim.purchaseProofAvailable || null,
    prior_claim_count: claim.priorClaimCount ? Number(claim.priorClaimCount) : null,
    previous_repair_cost: claim.previousRepairCost ? Number(claim.previousRepairCost) : null,
    ocr_confidence: claim.ocrConfidence ? Number(claim.ocrConfidence) : null,
    claim_submission_channel: claim.claimSubmissionChannel || null,
  }
}

function fromApiAnalysis(analysis) {
  return {
    finalDecision: analysis.final_decision,
    mlPrediction: analysis.ml_prediction,
    confidence: analysis.ml_confidence,
    ruleTriggered: analysis.rule_triggered,
    reasons: analysis.decision_reasons || [],
    analyzedAt: analysis.analyzed_at,
  }
}

export async function analyzeClaim(claim) {
  const createdClaim = await api.post('/claims', toApiClaim(claim))
  const analysis = await api.post(`/claims/${encodeURIComponent(createdClaim.data.claim_id)}/analyze`)
  return fromApiAnalysis(analysis.data)
}

export async function getClaims() {
  const response = await api.get('/claims', { params: { page: 1, page_size: 100 } })
  return response.data
}

export async function deleteClaim(claimId) {
  await api.delete(`/claims/${encodeURIComponent(claimId)}`)
}
