# Routing reference

Preferred: call `aifence_quality_plan` with the full request, then follow its retrieval actions. The plan is advisory routing derived from AIFENCE Core; model judgment still resolves ambiguous business context.

Fallback without MCP: run `aifence plan "<request>" --json`. If no runtime is installed, find AIFENCE Core, read `README.md` first, then `CONTROL_INDEX.md`, `PROFILE_MATRIX.md`, and `MANIFEST.md` only as the README requires. Never load all controls/registries preemptively.

Hybrid artifacts use the union of only the necessary creation routes. Explicit prototype/MVP/mockup/wireframe/demo intent may reduce deliverable scope but never disables truth, safety, authority, or evidence boundaries.
