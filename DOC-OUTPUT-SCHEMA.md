# Output Schema

The CLI returns one JSON object.

Required top-level keys:

- `skill`
- `version`
- `evaluated_at`
- `data_timestamp`
- `data_quality`
- `factor_scores`
- `confidence`
- `regime`
- `risk_mode`
- `maximum_invested_exposure`
- `allocation`
- `action`
- `evidence`
- `invalidation_conditions`
- `warnings`
- `risk_notice`

Allocation values are whole percentages and must total 100.
