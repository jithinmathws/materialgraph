# MaterialGraph Scientific Change History

---

## v1.9.7

Summary

Composition weighting remediation.

Reason

Resolved MG-AUD-001.

Affected Components

Material import

Criticality

Quality

Discovery

Changes

LiFePO4 Criticality

36.5 → 32.0

Scientific Usefulness

94.95 → 95.65

Reason

Correct stoichiometric weighting.

Breaking API

No

Database Backfill

Yes

Regression Status

Passed

---

## v1.9.8

Summary

Criticality evidence remediation.

Reason

Resolved MG-AUD-002.

Affected Components

Criticality

Quality

Scientific Pathway

Similarity

Recommendation

Changes

Unknown Criticality

null remains unknown

Quality Contribution

Unknown criticality receives no favorable quality bonus.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

Scientific Usefulness

No change (95.65)

Reason

Only incomplete criticality evidence behavior changed.

Breaking API

No

Database Backfill

No

Regression Status

Passed

---

## v1.9.9

Summary

Risk evidence remediation for candidate screening.

Reason

Resolved MG-AUD-003.

Affected Components

Candidate Screening

Candidate Comparison

Material Risk

Changes

Unknown Risk

null remains unknown throughout screening and comparison.

Risk Evidence

Evidence metadata exposed in candidate screening responses.

Performance

Bulk risk loading replaces per-material legacy risk lookups.

Scientific Changes

LiFePO4 Risk

No change (2.833)

LiFePO4 Criticality

No change (32.0)

Scientific Usefulness

No change (95.65)

Reason

Only unknown risk evidence handling changed.

Breaking API

No

Database Backfill

No

Regression Status

Passed

---

## v1.9.10

Summary

Exact element membership remediation.

Reason

Resolved MG-AUD-004.

Affected Components

Discovery Candidate Scoring

Discovery Chain Search

Discovery Warning Generation

Research Objective Exploration

Chemical Formula Membership

Changes

Element Membership

Exact chemical element membership replaces raw formula substring matching.

Candidate Scoring

Preferred and avoided element scoring now uses structured element
membership instead of string matching.

Discovery Chains

Candidate expansion now uses exact element membership during preferred
element filtering.

Research Objective Exploration

Scoring, researcher reasons, and warnings now use exact element
membership.

Warnings

Researcher-facing warnings no longer rely on substring matching.

Scientific Changes

LiFePO4 Criticality

No change (32.0)

LiFePO4 Risk

No change (2.833)

Scientific Usefulness

No change (95.65)

Reason

The Li/Na phosphate reference workflow already used unambiguous element
symbols. The remediation corrects ambiguous element symbol handling
(e.g. N vs Na, S vs Si, C vs Ca) without changing valid scientific
results.

Performance

Structured MaterialElement membership reused where already available.

Formula parsing only used where structured membership is unavailable.

Breaking API

No

Database Backfill

No

Regression Status

Passed

Reference Workflow

Verified

LiFePO4 → Na phosphate objective unchanged.
