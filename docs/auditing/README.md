# MaterialGraph Audit Documentation

This directory is the canonical navigation point for MaterialGraph audit work.

## Current status

| Metric | Count |
|---|---:|
| Total findings | 94 |
| Remediated | 46 |
| Accepted behavior / no defect confirmed | 2 |
| Open | 46 |
| Closed total | 48 |

See [AUDIT_REGISTER.md](AUDIT_REGISTER.md) for the authoritative status of every finding.

## Structure

- `AUDIT_REGISTER.md` — sole authoritative status register and totals.
- `findings/` — complete finding descriptions grouped by permanent ID range.
- `resolutions/` — append-only remediation and verification evidence by month.
- `change-impact/` — append-only behavioral change history by month.
- `supporting/` — frozen supporting audits and investigations.
- `archive/pre-reorganization/` — unchanged source documents retained for traceability.

## Maintenance workflow

1. Add each newly confirmed finding to `AUDIT_REGISTER.md` and the appropriate range file.
2. Keep the permanent `MG-AUD-NNN` identifier unchanged.
3. During remediation, append evidence to the current monthly resolution file.
4. Add user-visible or system-level effects to the current monthly change-impact file.
5. Update status and totals only in `AUDIT_REGISTER.md`; mirror totals here for navigation.
6. Do not edit archived or frozen supporting documents.

## Status definitions

- **Open:** Confirmed defect, risk, or decision item that has not been closed.
- **Remediated:** Implementation or documentation change is recorded in the remediation ledger with regression evidence.
- **Accepted behavior:** Investigation found no defect requiring remediation; closure rationale is documented in the finding record.

`Remediated` applies only to the documented implementation scope. It does not imply independent scientific validation by researchers, literature, domain computation, or experiment.