# Stale-Data Scenario

Set `evaluated_at` more than 90 minutes after `data_timestamp`.

The evaluator fails closed:

- data quality becomes `Stale`;
- risk mode becomes `Data Stop`;
- regime becomes `High Risk`;
- cash target becomes 100%.
