# Risk Management

Risk rules override opportunity scores.

## Control hierarchy

1. Data-quality stop
2. Daily-loss circuit breaker
3. Maximum-drawdown protection
4. BTC long-term trend cap
5. Volatility shock
6. Sentiment/funding crowding caps
7. Normal regime allocation

## Portfolio heat

The reference implementation expresses portfolio heat as total invested exposure. A production adapter should also measure:

- correlated exposure;
- open stop-loss risk;
- exchange concentration;
- stablecoin issuer concentration;
- liquidity under stressed spreads.

## No hidden recovery logic

After a circuit breaker, the Agent must not immediately re-enter because a lower timeframe appears bullish. Normal operation resumes only after the configured daily reset and fresh validation.
