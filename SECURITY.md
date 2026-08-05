# Security Policy

QMI does not require exchange credentials and should not be modified to commit keys to source control.

## Reporting

Report security concerns privately to the repository owner before public disclosure.

## Safe deployment principles

- Keep exchange credentials outside the repository.
- Use read-only keys for data retrieval where possible.
- Use withdrawal-disabled keys for any future execution adapter.
- Enforce allowlists, position limits and independent kill switches.
- Treat third-party data and model output as untrusted input.
