# Business Summary (Questions 8-13)

## 8. What business problem did you solve?

The application helps the hospital identify medium and high-risk patients from encounter data and prioritize follow-up interventions. It turns raw visit history into an actionable care queue so care teams can focus on patients most likely to need immediate attention.

## 9. Who is the primary user? What decision does your application improve?

Primary users:
- Care coordinators
- Case managers
- Population health teams

Decision improved:
- Which patients should be contacted first for intervention and follow-up
- How to assign intervention ownership and track status updates

## 10. What did the dataset prove?

The dataset proved that encounter-level utilization features (inpatient count, emergency visits, outpatient visits, length of stay, and medication load) can be transformed into a meaningful risk score and grouped into operational risk levels (LOW, MEDIUM, HIGH). This supports building a reliable first-pass care prioritization workflow.

## 11. What assumptions did you make?

- Historical utilization is a valid proxy for short-term risk.
- The source data is sufficiently complete and correctly typed for scoring.
- Higher utilization patterns correlate with higher likelihood of requiring intervention.
- A rules-based score is acceptable for an initial version before a predictive model is deployed.

## 12. What must the hospital validate before this could become a real product?

- Clinical validity: confirm that risk logic aligns with physician and care-pathway expectations.
- Outcome impact: verify that high-priority outreach reduces readmissions or adverse events.
- Data quality: check missingness, delayed updates, and coding consistency across systems.
- Workflow fit: ensure intervention assignment/status tracking matches real care operations.
- Governance and compliance: PHI handling, access controls, and auditability.
- Bias and fairness: confirm prioritization does not disadvantage protected or vulnerable groups.

## 13. Would you use rules, traditional ML, LLM, or another approach next — and why?

Recommended next step:
- Use a hybrid approach.

Phase 1:
- Keep rules for transparency and operational trust.

Phase 2:
- Add traditional ML (for example, gradient boosting) to predict readmission/intervention need more accurately than fixed thresholds.

Where LLM helps:
- Summarizing intervention notes, generating care-plan drafts, and assisting documentation.

Why this approach:
- Rules are explainable and fast to deploy.
- ML improves predictive performance.
- LLM is best for unstructured text workflows, not primary numeric risk scoring.
