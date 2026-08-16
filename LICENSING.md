# AIFENCE Licensing

AIFENCE is the unified successor to three projects that each shipped under an
AGPL + commercial dual license: **SAGE** (`aifence.bus`), **AGENTDANCE**
(`aifence.guard`), and **BizIQ** (`aifence.quality`). The merged project keeps
that structure.

## Dual license

- **AGPL-3.0-or-later** — use, modify, and redistribute AIFENCE under the terms
  in [LICENSE](LICENSE).
- **Commercial license** — for proprietary products, closed-source services, or
  any deployment where AGPL terms are unsuitable. See
  [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md) or contact
  **aifence@digitalacre.org**.

## Path boundaries

| Path | License |
| --- | --- |
| `src/aifence/**` (server & control plane) | AGPL-3.0-or-later OR commercial |
| `quality/**` (BizIQ source pack & builder) | AGPL-3.0-or-later OR commercial |
| Generated SDKs / OpenAPI contract (when added) | Apache-2.0 |

## Provenance

AIFENCE incorporates code from the merged repositories. Tagged releases of the
predecessor projects retain their original licenses as recorded in their
respective changelogs; the dual-license terms here apply to the AIFENCE source
line and its releases. See [NOTICE](NOTICE) for attribution.
