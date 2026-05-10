# Phantom Tools Reference

This document specifies the input schemas, output schemas, example invocations, and usage guidance for the three MCP tools exposed by the Phantom server.

All tools are registered through FastMCP and exposed over the Streamable HTTP MCP transport. SHARP-on-MCP context (FHIR server URL, SMART JWT) is propagated via HTTP headers and extracted by middleware before tool execution — clients do not pass patient identifiers as tool arguments.

---

## Tool 1: `build_patient_model`

### Purpose

Constructs a structured computational patient model from the patient's FHIR R4 record. This is the foundation tool — every subsequent simulation or comparison operates on the model produced here. The model captures not just current state, but trajectory: where the patient's labs, vitals, and risk scores are headed.

### When to Use

Call this tool first in any clinical reasoning workflow. The output is intended to be passed (or referenced) into `simulate_scenario` and `compare_interventions`. Cache the result within a single agent reasoning loop to avoid redundant FHIR fetches.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "include_trajectories": {
      "type": "boolean",
      "default": true,
      "description": "Whether to compute longitudinal trajectories for labs and vitals using linear regression with 95% prediction intervals."
    },
    "include_care_gaps": {
      "type": "boolean",
      "default": true,
      "description": "Whether to evaluate the patient against the guideline-based care gap rule set."
    },
    "include_diagnostic_gaps": {
      "type": "boolean",
      "default": true,
      "description": "Whether to detect potential undiagnosed conditions from longitudinal lab patterns."
    },
    "lookback_months": {
      "type": "integer",
      "default": 24,
      "minimum": 6,
      "maximum": 60,
      "description": "How far back to fetch observations for trajectory computation."
    }
  },
  "required": []
}
```

The patient ID is **not** an input — it is extracted from the SMART JWT in the `Authorization` header (SHARP-on-MCP).

### Output Schema (abbreviated)

```json
{
  "patient": {
    "id": "string",
    "age_years": "integer",
    "sex": "male | female",
    "race": "string",
    "ethnicity": "string"
  },
  "active_conditions": [
    {
      "code": "string (ICD-10 or SNOMED)",
      "display": "string",
      "onset_date": "ISO 8601 date",
      "severity": "mild | moderate | severe | unknown"
    }
  ],
  "active_medications": [
    {
      "rxcui": "string",
      "name": "string",
      "drug_class": "string",
      "dose": "string",
      "frequency": "string"
    }
  ],
  "labs": {
    "<lab_name>": {
      "current_value": "number",
      "current_unit": "string",
      "current_date": "ISO 8601 date",
      "trajectory": {
        "slope_per_year": "number",
        "direction": "rising | falling | stable",
        "rate_classification": "normal | moderate | rapid",
        "projections": {
          "6_months": { "value": "number", "ci_lower": "number", "ci_upper": "number" },
          "12_months": { "value": "number", "ci_lower": "number", "ci_upper": "number" },
          "24_months": { "value": "number", "ci_lower": "number", "ci_upper": "number" }
        },
        "data_point_count": "integer"
      }
    }
  },
  "risk_scores": {
    "egfr_ckd_epi_2021": { "value": "number", "ckd_stage": "string", "interpretation": "string" },
    "ascvd_10yr": { "value_percent": "number", "risk_category": "string" },
    "fib4": { "value": "number", "fibrosis_category": "string" },
    "kdigo_2024": { "stage": "string", "albuminuria_category": "string", "risk_band": "string" }
  },
  "care_gaps": [
    {
      "rule_id": "string",
      "guideline": "string",
      "description": "string",
      "recommendation": "string",
      "evidence_grade": "string",
      "priority": "high | medium | low",
      "citation": "string"
    }
  ],
  "diagnostic_gaps": [
    {
      "rule_id": "string",
      "likely_diagnosis": "string",
      "explanation": "string",
      "recommended_workup": "string",
      "urgency": "urgent | soon | routine",
      "citation": "string"
    }
  ],
  "confidence": {
    "overall": "high | medium | low",
    "by_system": {
      "renal": "high | medium | low",
      "cardiovascular": "high | medium | low",
      "metabolic": "high | medium | low",
      "hepatic": "high | medium | low"
    },
    "data_gaps": ["string"]
  }
}
```

### Example Invocation

```json
{
  "tool": "build_patient_model",
  "arguments": {
    "include_trajectories": true,
    "include_care_gaps": true,
    "include_diagnostic_gaps": true,
    "lookback_months": 24
  }
}
```

### Example Response (excerpt)

```json
{
  "patient": {
    "id": "maria-santos-001",
    "age_years": 58,
    "sex": "female",
    "race": "Black or African American",
    "ethnicity": "Not Hispanic or Latino"
  },
  "active_conditions": [
    { "code": "E11.9", "display": "Type 2 diabetes mellitus", "onset_date": "2017-03-15", "severity": "moderate" },
    { "code": "N18.31", "display": "Chronic kidney disease, stage 3a", "onset_date": "2023-06-22", "severity": "moderate" }
  ],
  "labs": {
    "egfr": {
      "current_value": 49,
      "current_unit": "mL/min/1.73m2",
      "current_date": "2025-11-12",
      "trajectory": {
        "slope_per_year": -6.5,
        "direction": "falling",
        "rate_classification": "rapid",
        "projections": {
          "12_months": { "value": 42.5, "ci_lower": 38.1, "ci_upper": 46.9 }
        },
        "data_point_count": 8
      }
    }
  },
  "risk_scores": {
    "egfr_ckd_epi_2021": { "value": 49, "ckd_stage": "G3a", "interpretation": "Mildly to moderately decreased" },
    "kdigo_2024": { "stage": "G3a", "albuminuria_category": "A2", "risk_band": "high" }
  },
  "care_gaps": [
    {
      "rule_id": "diabetes_sglt2i_ckd",
      "guideline": "ADA 2024 Standards of Care + KDIGO 2024",
      "description": "Patient with T2DM and CKD Stage 3a is not on an SGLT2 inhibitor",
      "recommendation": "Initiate empagliflozin 10mg daily for renoprotection and CV risk reduction",
      "evidence_grade": "A",
      "priority": "high",
      "citation": "DAPA-CKD (PMID 32970396), EMPA-KIDNEY (PMID 36331190)"
    }
  ]
}
```

### Common Errors

| Error | Cause | Resolution |
|-------|-------|-----------|
| `MissingPatientContextError` | SHARP context not propagated; no patient ID in JWT | Verify Po MCP server config has FHIR Context extension enabled |
| `FHIRConnectionError` | FHIR server unreachable or credentials invalid | Check `X-FHIR-Server-URL` header and JWT validity |
| `InsufficientDataError` | Patient has fewer than 3 lab data points for trajectory regression | Set `include_trajectories: false` or extend `lookback_months` |
| `FHIRPaginationTimeout` | Patient has thousands of observations across many pages | Reduce `lookback_months` |

---

## Tool 2: `simulate_scenario`

### Purpose

Runs a forward simulation of a clinical scenario against the patient model. Supports four scenario types: medication change, treatment inaction, diagnostic workup, or guideline action. Projects outcomes across renal, cardiovascular, metabolic, and hepatic systems simultaneously. Every projection cites the trial(s) and effect modifiers used.

### When to Use

After `build_patient_model`, call this tool to answer "what if" questions. Typical agent workflows call it twice: once for inaction (baseline trajectory) and once for the most clinically urgent intervention.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "scenario_type": {
      "type": "string",
      "enum": ["medication_change", "inaction", "diagnostic_workup", "guideline_action"],
      "description": "The type of scenario to simulate."
    },
    "intervention": {
      "type": "object",
      "description": "Required for medication_change and guideline_action scenarios.",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["add", "remove", "switch", "dose_change"]
        },
        "drug_name": { "type": "string", "description": "Generic drug name (e.g., 'empagliflozin')" },
        "dose": { "type": "string" },
        "frequency": { "type": "string" }
      }
    },
    "horizon_months": {
      "type": "integer",
      "default": 12,
      "enum": [6, 12, 24],
      "description": "Time horizon for the simulation."
    },
    "include_cascades": {
      "type": "boolean",
      "default": true,
      "description": "Whether to apply comorbidity cascade modifiers."
    }
  },
  "required": ["scenario_type"]
}
```

### Output Schema (abbreviated)

```json
{
  "scenario_summary": "string",
  "horizon_months": "integer",
  "projections": {
    "renal": {
      "egfr_at_horizon": { "value": "number", "ci_lower": "number", "ci_upper": "number" },
      "stage_progression_probability": "number (0-1)",
      "time_to_dialysis_years": "number | null",
      "modifiers_applied": ["string"]
    },
    "cardiovascular": {
      "ascvd_10yr_at_horizon_percent": "number",
      "bp_systolic_projected": "number",
      "modifiers_applied": ["string"]
    },
    "metabolic": {
      "hba1c_at_horizon_percent": "number",
      "weight_change_kg": "number",
      "modifiers_applied": ["string"]
    },
    "hepatic": {
      "fib4_at_horizon": "number",
      "fibrosis_progression_risk": "string",
      "modifiers_applied": ["string"]
    }
  },
  "evidence_citations": [
    {
      "trial_name": "string",
      "pmid": "string",
      "modifier_used": "string",
      "applicability_to_patient": "high | medium | low"
    }
  ],
  "caveats": ["string"]
}
```

### Example Invocation

```json
{
  "tool": "simulate_scenario",
  "arguments": {
    "scenario_type": "medication_change",
    "intervention": {
      "action": "add",
      "drug_name": "empagliflozin",
      "dose": "10mg",
      "frequency": "daily"
    },
    "horizon_months": 12,
    "include_cascades": true
  }
}
```

### Example Response (excerpt)

```json
{
  "scenario_summary": "Add empagliflozin 10mg daily to current regimen for 12 months",
  "horizon_months": 12,
  "projections": {
    "renal": {
      "egfr_at_horizon": { "value": 47, "ci_lower": 43, "ci_upper": 51 },
      "stage_progression_probability": 0.18,
      "time_to_dialysis_years": 14.2,
      "modifiers_applied": ["sglt2i_renoprotection_-1.78_slope", "diabetes_acceleration_+0.4"]
    },
    "metabolic": {
      "hba1c_at_horizon_percent": 7.6,
      "weight_change_kg": -2.3,
      "modifiers_applied": ["sglt2i_hba1c_-0.6", "sglt2i_weight_-2_to_-3"]
    }
  },
  "evidence_citations": [
    {
      "trial_name": "DAPA-CKD",
      "pmid": "32970396",
      "modifier_used": "drug-vs-placebo eGFR slope difference +1.78 mL/min/1.73m²/year",
      "applicability_to_patient": "high"
    },
    {
      "trial_name": "EMPA-KIDNEY",
      "pmid": "36331190",
      "modifier_used": "kidney disease progression hazard ratio 0.72",
      "applicability_to_patient": "high"
    }
  ],
  "caveats": [
    "Projections assume medication adherence at 80%+",
    "Genitourinary side effect risk elevated in female patients with diabetes"
  ]
}
```

### Common Errors

| Error | Cause | Resolution |
|-------|-------|-----------|
| `UnknownDrugError` | `drug_name` not in evidence base | Use `get_all_drug_names()` to list supported drugs; consider adding the drug |
| `ContraindicatedInterventionError` | The proposed drug has a hard contraindication for this patient | Surface the contraindication; do not simulate |
| `MissingInterventionError` | `scenario_type` is `medication_change` but `intervention` is null | Provide a complete intervention object |
| `InvalidHorizonError` | `horizon_months` not in [6, 12, 24] | Use one of the supported horizons |

---

## Tool 3: `compare_interventions`

### Purpose

Runs multiple intervention simulations head-to-head and returns a personalized ranked comparison. Designed for shared decision-making moments where a clinician (or patient) is choosing among 2-4 candidate treatments. Ranking is patient-specific based on the patient's actual labs, comorbidities, and contraindications — not population averages.

### When to Use

When the patient model surfaces a clear decision point (e.g., "needs second-line glycemic agent" or "needs antihypertensive intensification") and there are multiple guideline-supported options. Do not use for single-option decisions.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "interventions": {
      "type": "array",
      "minItems": 2,
      "maxItems": 4,
      "items": {
        "type": "object",
        "properties": {
          "drug_name": { "type": "string" },
          "dose": { "type": "string" },
          "frequency": { "type": "string" }
        },
        "required": ["drug_name"]
      }
    },
    "comparison_dimensions": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "hba1c_reduction",
          "weight_change",
          "egfr_protection",
          "cardiovascular_benefit",
          "hepatic_safety",
          "contraindications",
          "cost_tier",
          "adherence_burden"
        ]
      },
      "description": "If omitted, all relevant dimensions are included."
    },
    "horizon_months": {
      "type": "integer",
      "default": 12,
      "enum": [6, 12, 24]
    }
  },
  "required": ["interventions"]
}
```

### Output Schema (abbreviated)

```json
{
  "comparison_table": [
    {
      "drug_name": "string",
      "dimensions": {
        "<dimension_name>": {
          "value": "string | number",
          "rank": "integer (1 = best)",
          "evidence": "string"
        }
      },
      "overall_rank": "integer",
      "patient_specific_factors": ["string"],
      "contraindications_for_this_patient": ["string"]
    }
  ],
  "recommendation": {
    "top_choice": "string",
    "rationale": "string",
    "shared_decision_talking_points": ["string"]
  },
  "evidence_citations": [
    {
      "trial_name": "string",
      "pmid": "string",
      "supports": "string"
    }
  ]
}
```

### Example Invocation

```json
{
  "tool": "compare_interventions",
  "arguments": {
    "interventions": [
      { "drug_name": "empagliflozin", "dose": "10mg", "frequency": "daily" },
      { "drug_name": "semaglutide", "dose": "1mg", "frequency": "weekly" },
      { "drug_name": "tirzepatide", "dose": "5mg", "frequency": "weekly" }
    ],
    "horizon_months": 12
  }
}
```

### Example Response (excerpt)

```json
{
  "comparison_table": [
    {
      "drug_name": "empagliflozin",
      "dimensions": {
        "egfr_protection": { "value": "+1.78 mL/min/year vs placebo", "rank": 1, "evidence": "DAPA-CKD" },
        "hba1c_reduction": { "value": "-0.6%", "rank": 3, "evidence": "EMPA-REG" },
        "weight_change": { "value": "-2.3 kg", "rank": 3, "evidence": "EMPA-REG" },
        "cardiovascular_benefit": { "value": "HR 0.86 MACE", "rank": 2, "evidence": "EMPA-REG" },
        "cost_tier": { "value": "high", "rank": 2, "evidence": "AWP retail" }
      },
      "overall_rank": 1,
      "patient_specific_factors": [
        "CKD Stage 3a — renoprotection is highest priority",
        "Albuminuria A2 — SGLT2i strongly indicated"
      ]
    },
    {
      "drug_name": "semaglutide",
      "dimensions": {
        "egfr_protection": { "value": "modest", "rank": 2, "evidence": "FLOW trial" },
        "hba1c_reduction": { "value": "-1.4%", "rank": 2, "evidence": "SUSTAIN-6" },
        "weight_change": { "value": "-4.5 kg", "rank": 2, "evidence": "SUSTAIN-6" },
        "cardiovascular_benefit": { "value": "HR 0.74 MACE", "rank": 1, "evidence": "SUSTAIN-6" },
        "cost_tier": { "value": "high", "rank": 2, "evidence": "AWP retail" }
      },
      "overall_rank": 2
    }
  ],
  "recommendation": {
    "top_choice": "empagliflozin",
    "rationale": "For this patient — T2DM with CKD Stage 3a, A2 albuminuria, and rising eGFR slope — renoprotection is the dominant consideration. Empagliflozin has the strongest renoprotective evidence in this exact population (DAPA-CKD inclusion criteria match closely).",
    "shared_decision_talking_points": [
      "Empagliflozin protects kidneys and lowers cardiovascular risk",
      "Daily oral pill, not injection",
      "Modest weight loss (~2-3 kg) and HbA1c reduction (~0.6%)",
      "Watch for genitourinary infections, especially in first 3 months"
    ]
  }
}
```

### Common Errors

| Error | Cause | Resolution |
|-------|-------|-----------|
| `TooFewInterventionsError` | Fewer than 2 interventions provided | Supply at least 2 |
| `TooManyInterventionsError` | More than 4 interventions provided | Reduce to ≤4 (cognitive load principle) |
| `AllInterventionsContraindicatedError` | Every supplied drug has a contraindication for this patient | Re-evaluate the differential |
| `MixedClassWarning` | Comparing drugs from very different classes (e.g., insulin vs aspirin) | Returns warning but proceeds |

---

## Tool Composition Patterns

### Pattern 1: Pre-Visit Briefing (Standard)
```
build_patient_model
  → simulate_scenario (inaction, 12 months)
  → simulate_scenario (top intervention, 12 months)
  → compare_interventions (top 3 candidates)
  → compose briefing
```

### Pattern 2: Single Question Answer
```
build_patient_model
  → simulate_scenario (specific intervention requested)
  → return narrative
```

### Pattern 3: Risk Stratification Only
```
build_patient_model (include_trajectories=true)
  → return risk_scores + trajectories
```

### Pattern 4: Care Gap Audit
```
build_patient_model (include_care_gaps=true, include_diagnostic_gaps=true)
  → return care_gaps + diagnostic_gaps sorted by priority
```