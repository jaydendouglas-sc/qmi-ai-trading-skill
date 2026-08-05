# Architecture

```mermaid
flowchart TD
    A[Timestamped market and portfolio data] --> B[Schema and freshness validation]
    B -->|Invalid| Z[Data Stop: 100% cash target]
    B -->|Valid| C[Six factor scorers]
    C --> D[Weighted confidence]
    D --> E[Regime classifier]
    E --> F[Hard risk-control overlay]
    F --> G[Rotation adjustment]
    G --> H[Exposure cap and asset restrictions]
    H --> I[Decision packet: JSON]
    I --> J[Agent explanation, audit log and optional execution adapter]
```

The reference package ends at the decision packet. Exchange execution is intentionally separated so that credentials, venue rules and operational controls are not mixed with strategy logic.
