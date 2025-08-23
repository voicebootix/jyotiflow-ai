# ADR: Downgrade `email-validator` to v2.1.1

**Date**: 2025-08-23

**Status**: Accepted

## Context

During a deployment on Render, the dependency installation failed due to a conflict between `fastapi-users` and `email-validator`.

- `fastapi-users==13.0.0` requires `email-validator<2.2`
- Our `requirements.txt` had pinned `email-validator==2.2.0`

This caused a `ResolutionImpossible` error in `pip`, blocking all deployments.

## Decision

We have downgraded `email-validator` from version `2.2.0` to `2.1.1`.

This version satisfies the constraint imposed by `fastapi-users` (`<2.2`) and resolves the immediate dependency conflict.

## Consequences

- **Positive**:
  - Unblocks deployments.
  - Stabilizes the dependency tree.

- **Negative**:
  - We are not on the latest version of `email-validator`. This is an acceptable trade-off for system stability.

- **Action Required**:
  - The CI pipeline should be verified to include comprehensive email validation tests (e.g., Unicode characters, plus-tagging, Pydantic model integration) to catch any future regressions if we decide to upgrade this package again.
