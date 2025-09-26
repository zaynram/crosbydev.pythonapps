# Medical Records Configuration for Personal Injury Cases

This configuration is specifically tailored for analyzing medical records in the context of personal injury litigation. It focuses on extracting information relevant to establishing causation, damages, and the extent of injuries.

## Key Features

### Legal-Focused Analysis
- **Causation Evidence**: Extracts medical opinions linking injuries to the incident
- **Pre-existing Conditions**: Identifies conditions that may have been aggravated
- **Functional Limitations**: Documents impact on daily life and work capacity
- **Pain and Suffering**: Captures subjective symptom indicators
- **Economic Damages**: Identifies medical expenses and future care needs

### Enhanced Schema
The configuration extracts information into 8 key categories:

1. **Incident-Related Injuries**: Direct injuries with causation evidence
2. **Pre-existing Conditions**: Prior conditions and any aggravation
3. **Treatments Received**: Medical care with cost implications
4. **Functional Limitations**: Impact on daily activities and work
5. **Pain and Suffering Indicators**: Subjective symptoms and their severity
6. **Medical Expenses**: Costs associated with treatment
7. **Prognosis and Future Care**: Long-term outlook and anticipated needs
8. **Expert Opinions**: Professional medical assessments and disability ratings

## Usage Example

```bash
# Analyze medical records for a personal injury case
python main.py analyze medical_records/ \
  --config configs/medical_records.yaml \
  --incident-description "Motor vehicle accident on Highway 101" \
  --incident-date "2024-03-15" \
  --legal-context "Personal injury lawsuit - plaintiff vs. defendant driver" \
  --analysis-focus "Establish causation and quantify damages"
```

## Template Variables

The configuration uses these template variables in the prompt:

- `{incident_description}`: Details about the incident that caused the injury
- `{incident_date}`: Date when the incident occurred  
- `{legal_context}`: Type of case and parties involved
- `{analysis_focus}`: Specific legal questions to address
- `{document_text}`: The extracted medical record text

## Output Structure

Each extracted item includes detailed attributes:

```json
{
  "incident_related_injuries": [
    {
      "injury": "Lumbar spine strain",
      "body_part": "Lower back",
      "severity": "Moderate",
      "causation_evidence": "Patient reports onset immediately after collision"
    }
  ],
  "functional_limitations": [
    {
      "limitation": "Difficulty lifting over 10 pounds",
      "duration": "6 months post-incident",
      "impact_on_daily_life": "Cannot perform household chores",
      "work_related_impact": "Unable to return to construction work"
    }
  ]
}
```

This structured approach provides attorneys with the detailed information needed to build a strong personal injury case.