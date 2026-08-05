# Agent Integration

An AI Agent may:

1. obtain data from approved providers;
2. calculate indicators;
3. populate the input schema;
4. call the QMI evaluator;
5. explain the returned evidence and warnings;
6. ask for human approval or pass the target to a separately controlled execution adapter;
7. preserve an audit log.

The Agent must not:

- invent missing values;
- override a hard risk state;
- claim certainty or guaranteed profit;
- expose credentials in logs;
- describe illustrative examples as live recommendations.
