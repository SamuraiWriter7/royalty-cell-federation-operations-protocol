# Royalty Cell Federation Operations Protocol

A protocol for activating, assigning, forming, routing, isolating, recovering,
reconfiguring, exercising, and evaluating federated Royalty Cells during live
value-return operations.

## Status

Current protocol version: `v0.5.0`

The initial `v0.1`–`v0.5` operations cycle is complete.

```text
Activation Request
    ↓
Readiness Assessment
    ↓
Activation Receipt
    ↓
Operational Role Assignment
    ↓
Authority Scope Binding
    ↓
Federation Formation
    ↓
Route Decision
    ↓
Value Flow Route
    ↓
Operational Incident
    ↓
Cell Isolation / Route Suspension
    ↓
Recovery Assessment
    ↓
Reactivation Receipt
    ↓
Reconfiguration Plan
    ↓
Cell Replacement / Capacity Rebalancing
    ↓
Federation Drill
    ↓
Operational Conformance Report
```

The protocol defines twenty-two operational record types across five versions.

---

## Core idea

Royalty Cell Protocol defines what an autonomous value-return Cell records.

Royalty Cell Federation Operations Protocol defines how those Cells are placed
into live operation.

```text
royalty-cell-protocol
= the internal structure of each economic Cell

royalty-cell-federation-operations-protocol
= the operational nervous system connecting and moving those Cells
```

A Royalty Cell may contain valid Origin, Usage, Derivative, Contribution,
Allocation, Royalty Receipt, Interoperability, Dispute, and Holdback records.

That does not automatically mean the Cell is ready to perform a live federation
duty.

The operations protocol therefore separates:

```text
Cell existence
≠ operational readiness

Readiness
≠ activation

Activation
≠ live duty assignment

Role Assignment
≠ unlimited authority

Authority Binding
≠ new authority

Formation membership
≠ authority expansion

Route Decision
≠ Route execution

Incident observation
≠ proof of misconduct

Isolation
≠ Cell deletion

Recovery readiness
≠ reactivation authority

Reactivation
≠ authority expansion

Reconfiguration Plan
≠ live mutation

Capacity Rebalancing
≠ economic Allocation

Federation Drill
≠ live Incident

Operational Conformance Report
≠ legal certification
```

The protocol makes each transition explicit, auditable, and independently
reviewable.

---

## Why an operations protocol is necessary

A collection of interoperable Royalty Cells does not automatically become a
working federation.

A live federation must still determine:

* which Cells may enter operation;
* which roles each Cell may perform;
* which capabilities each role may exercise;
* where each Cell is positioned;
* which Route a record or value event should follow;
* which fallback Route should be used;
* how duty is handed over;
* how overloaded or damaged Cells are isolated;
* how suspended Routes are restored;
* how replacement Cells enter the Formation;
* how capacity is redistributed;
* how the federation tests its own resilience;
* how operational conformance is reported.

Without these records, federation behavior would depend on invisible,
unreviewable coordination.

This repository converts that coordination into explicit protocol evidence.

---

## Design objective

The protocol is designed to produce a federation that can:

```text
activate cautiously,
assign authority narrowly,
form deliberately,
route reproducibly,
fail partially,
recover safely,
reconfigure reversibly,
test itself,
and report what happened.
```

The goal is not maximum automation.

The goal is controlled operational autonomy.

---

## Authority containment

Authority flows downward from an explicit Activation Receipt.

```text
Activation Receipt capabilities
    ⊇ Operational Role Assignment capabilities
        ⊇ Authority Scope Binding capabilities
            ⊇ Formation node authority
                ⊇ Value Flow Route stage capabilities
                    ⊇ Isolation and Recovery targets
                        ⊇ Reactivated capabilities
                            ⊇ Replacement capabilities
```

Every downstream record may preserve or narrow upstream authority.

It must not expand it.

Examples:

```text
A Role Assignment cannot add a capability
that was not granted by the Activation Receipt.

An Authority Scope Binding cannot add a capability
that was not assigned to the Role.

A Formation node cannot exercise a capability
that its Assignment does not hold.

A Route stage cannot invoke a capability
that its Formation node lacks.

An Isolation Order cannot invent a capability
merely to name it as suspended.

A Reactivation Receipt cannot restore more authority
than the original Assignment held.

A Cell Replacement cannot transfer a capability
that the replacement Assignment does not possess.
```

This containment chain is one of the protocol's primary safety properties.

---

## Protocol versions

### v0.1 — Cell Activation and Readiness

Defines:

* Cell Activation Request;
* Cell Readiness Assessment;
* Cell Activation Receipt;
* Cell Suspension Receipt.

Version 0.1 answers:

> Is this Royalty Cell ready to enter federation operation, and who authorized
> it?

### v0.2 — Operational Roles and Handoffs

Defines:

* Operational Role Assignment;
* Authority Scope Binding;
* Cell Handoff Record;
* Duty Rotation Record.

Version 0.2 answers:

> What duty does the activated Cell perform, within which authority boundary,
> and how is that duty transferred?

### v0.3 — Federation Formation and Routing

Defines:

* Federation Formation Record;
* Cell Route Decision Receipt;
* Value Flow Route;
* Formation Change Record.

Version 0.3 answers:

> Where is each Cell positioned, and which operational path should a record or
> value event follow?

### v0.4 — Operational Incident Isolation and Recovery

Defines:

* Operational Incident Record;
* Cell Isolation Order;
* Route Suspension Receipt;
* Cell Recovery Assessment;
* Cell Reactivation Receipt.

Version 0.4 answers:

> How can a federation contain a partial failure, continue through a fallback,
> and restore the affected Cell safely?

### v0.5 — Federation Reconfiguration and Operational Exercises

Defines:

* Federation Reconfiguration Plan;
* Cell Replacement Record;
* Capacity Rebalancing Receipt;
* Federation Drill Record;
* Operational Conformance Report.

Version 0.5 answers:

> How can the federation reorganize itself, test its resilience, and evaluate
> whether its operating records remain conformant?

---

## Record catalog

| Version | Record                          | Purpose                                                                   | Effect declaration                                    |
| ------- | ------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------- |
| v0.1    | Cell Activation Request         | Requests activation of a Cell for declared roles and capabilities         | `request_effect: activation_request_only`             |
| v0.1    | Cell Readiness Assessment       | Evaluates whether the requested Cell is ready                             | `assessment_effect: readiness_assessment_only`        |
| v0.1    | Cell Activation Receipt         | Records an explicit activation decision and granted authority             | `receipt_effect: activation_record_only`              |
| v0.1    | Cell Suspension Receipt         | Suspends all or part of an activated Cell's operational authority         | `suspension_effect: operational_suspension_only`      |
| v0.2    | Operational Role Assignment     | Assigns a bounded live duty to an activated Cell                          | `assignment_effect: operational_role_assignment_only` |
| v0.2    | Authority Scope Binding         | Narrows a Role Assignment by resource, Route, operation, value, or time   | `binding_effect: authority_scope_binding_only`        |
| v0.2    | Cell Handoff Record             | Transfers responsibility and pending state between compatible Assignments | `handoff_effect: handoff_record_only`                 |
| v0.2    | Duty Rotation Record            | Defines which Assignment is currently on duty                             | `rotation_effect: duty_rotation_record_only`          |
| v0.3    | Federation Formation Record     | Places Role Assignments into an operational topology                      | `formation_effect: formation_record_only`             |
| v0.3    | Cell Route Decision Receipt     | Evaluates candidate paths and records the selected Route                  | `decision_effect: route_decision_only`                |
| v0.3    | Value Flow Route                | Materializes the selected path as ordered operational stages              | `route_effect: value_flow_route_only`                 |
| v0.3    | Formation Change Record         | Records append-only Formation changes                                     | `change_effect: formation_change_record_only`         |
| v0.4    | Operational Incident Record     | Records an observed operational abnormality                               | `incident_effect: incident_record_only`               |
| v0.4    | Cell Isolation Order            | Temporarily isolates a Node, capability, connection, or Route             | `isolation_effect: node_isolation_only`               |
| v0.4    | Route Suspension Receipt        | Suspends a full Route, stage, or connection                               | `route_suspension_effect: route_suspension_only`      |
| v0.4    | Cell Recovery Assessment        | Evaluates whether an isolated Cell is ready to return                     | `assessment_effect: recovery_assessment_only`         |
| v0.4    | Cell Reactivation Receipt       | Records the independent decision to restore duty                          | `receipt_effect: reactivation_record_only`            |
| v0.5    | Federation Reconfiguration Plan | Proposes topology and routing changes with rollback operations            | `plan_effect: reconfiguration_plan_only`              |
| v0.5    | Cell Replacement Record         | Replaces a Formation Assignment without expanding authority               | `replacement_effect: cell_replacement_only`           |
| v0.5    | Capacity Rebalancing Receipt    | Redistributes operational workload among Formation Nodes                  | `rebalance_effect: capacity_rebalancing_only`         |
| v0.5    | Federation Drill Record         | Records a controlled resilience exercise                                  | `drill_effect: drill_record_only`                     |
| v0.5    | Operational Conformance Report  | Aggregates operational evidence and reports protocol consistency          | `report_effect: operational_conformance_report_only`  |

These effect declarations prevent one record from silently producing a broader
operational, legal, economic, or settlement effect.

---

## v0.1 — Cell Activation and Readiness

### Activation Request

An Activation Request identifies:

* the target Cell;
* the requesting federation;
* the requesting authority;
* the requested operational roles;
* the requested capabilities;
* the operation context;
* the requested activation mode;
* the readiness policy;
* the requested time window;
* supporting Evidence.

Supported activation modes include:

* `primary`;
* `fallback`;
* `temporary`;
* `emergency`.

Emergency activation requires an explicit justification.

Temporary activation requires a bounded end time.

An Activation Request does not activate the Cell.

### Readiness Assessment

A Readiness Assessment may evaluate:

* Manifest validity;
* governance authority;
* role coverage;
* requested capabilities;
* Audit coverage;
* emergency controls;
* dispute state;
* settlement controls;
* interoperability state;
* capacity;
* security;
* other policy-defined checks.

Supported readiness states are:

* `ready`;
* `ready_with_conditions`;
* `not_ready`;
* `unknown`.

A `ready` assessment requires every required check to pass.

A `ready_with_conditions` assessment must identify the conditions that remain.

A `not_ready` assessment must identify one or more blockers.

A Readiness Assessment is evidence.

It is not permission to begin operation.

### Activation Receipt

An Activation Receipt records:

* the resolved Activation Request;
* the resolved Readiness Assessment;
* the activation outcome;
* assigned operational roles;
* granted capabilities;
* the Activation window;
* fallback Cell references;
* emergency suspension authorities;
* conditions;
* the federation decision;
* the Authorization reference.

Supported outcomes include:

* `activated`;
* `activated_with_conditions`;
* `denied`.

An activated outcome must preserve the requested roles and capabilities unless
a documented condition or denial explains otherwise.

A denied outcome must not grant operational authority.

### Suspension Receipt

A Suspension Receipt may apply to:

* the full activated Cell;
* selected roles;
* selected capabilities;
* selected Routes.

Partial suspension must identify at least one explicit target.

Suspension does not:

* delete the Cell;
* retire the Cell;
* erase historical records;
* revoke Origin or Contribution records;
* confiscate allocated value.

---

## v0.2 — Operational Roles and Handoffs

### Operational Role Assignment

An Operational Role Assignment places an activated Cell on duty.

Supported Assignment modes include:

* `primary`;
* `fallback`;
* `temporary`;
* `relief`;
* `emergency`.

Examples of operational roles include:

* Origin authority;
* Usage router;
* Derivative processor;
* Contribution reviewer;
* independent auditor;
* allocator;
* settlement executor;
* dispute handler;
* reserve operator;
* federation coordinator.

The assigned Role and capabilities must exist in the referenced Activation
Receipt.

### Authority Scope Binding

An Authority Scope Binding may restrict an Assignment by:

* capability;
* record type;
* operation;
* resource;
* Route;
* value limit;
* time window;
* delegation policy;
* Human Review;
* dual control.

The Binding may narrow authority.

It may not enlarge it.

```text
Activation Receipt
    ⊇ Role Assignment
        ⊇ Authority Scope Binding
```

### Cell Handoff Record

A Handoff transfers responsibility between two compatible Role Assignments.

It may transfer:

* capabilities;
* Routes;
* resources;
* state snapshots;
* pending tasks;
* unresolved references;
* Audit tasks;
* settlement holds;
* dispute tasks.

A completed Handoff requires acknowledgement from:

* the source Assignment;
* the target Assignment;
* the federation coordinator.

Mandatory pending items must be accepted by the target before completion.

A Handoff transfers existing responsibility.

It does not create new authority.

### Duty Rotation Record

A Duty Rotation defines the order in which compatible Assignments perform the
same Role.

Supported rotation modes include:

* `scheduled`;
* `load_based`;
* `incident_based`;
* `manual`.

An active Rotation must identify exactly one current Assignment.

Rotation changes who is on duty.

It does not change what the Role is permitted to do.

---

## v0.3 — Federation Formation and Routing

### Federation Formation Record

A Formation places active or standby Role Assignments into bounded operational
Nodes.

Supported Formation types include:

* `serial`;
* `parallel`;
* `hub_spoke`;
* `layered`;
* `mesh`;
* `wagon_fort`;
* `custom`.

Supported Node positions include:

* `core`;
* `perimeter`;
* `relay`;
* `gateway`;
* `reserve`;
* `observer`.

Each Node is bound to an upstream Operational Role Assignment.

A Formation Node does not create additional authority.

The Formation also defines:

* required roles;
* Node status;
* connections;
* required connections;
* fallback Nodes;
* coordination policy;
* quorum;
* lifecycle state.

A wagon-fort Formation requires both core and perimeter functions.

### Cell Route Decision Receipt

A Route Decision evaluates candidate Node paths.

A candidate may be evaluated against:

* required roles;
* required capabilities;
* maximum Hop count;
* Audit requirements;
* fallback availability;
* policy constraints;
* candidate score.

An approved decision must select an eligible candidate.

Selecting a lower-scoring eligible candidate requires an explicit override.

A required fallback must be distinct from the selected candidate.

A Route Decision chooses a path.

It does not execute it.

### Value Flow Route

A Value Flow Route converts the selected candidate into ordered Stages.

Each Stage identifies:

* sequence number;
* Formation Node;
* Role Assignment;
* Role type;
* capability;
* input record types;
* output record types;
* lifecycle state.

The Stage path must exactly reproduce the selected candidate path.

Stage numbers must be contiguous.

An active Route must contain exactly one active Stage.

A Route Stage may not use a capability that is absent from its upstream
Assignment.

### Formation Change Record

A Formation Change records append-only changes such as:

* adding a Node;
* removing a Node;
* replacing an Assignment;
* changing Node status;
* changing Node position;
* adding a connection;
* removing a connection;
* changing connection status.

An applied Formation Change must preserve every mandatory Role.

Route impacts and required fallback behavior must remain visible.

The original Formation Record is not silently overwritten.

---

## v0.4 — Operational Incident Isolation and Recovery

### Operational Incident Record

Supported Incident types include:

* `node_failure`;
* `capability_failure`;
* `authority_violation`;
* `route_failure`;
* `reference_failure`;
* `audit_failure`;
* `settlement_risk`;
* `policy_conflict`;
* `overload`;
* `security_event`;
* `data_integrity`;
* `other`.

An Incident Record identifies:

* the affected Formation;
* affected Nodes;
* affected Routes;
* severity;
* containment requirements;
* recommended actions;
* lifecycle state;
* resolution;
* remedy references;
* Evidence.

An Incident Record states what was observed.

It does not prove misconduct and does not itself impose Isolation.

Major and critical Incidents require visible containment.

A resolved Incident requires an explicit resolution, timestamp, and remedy
references.

### Cell Isolation Order

An Isolation Order may target:

* the full Formation Node;
* selected capabilities;
* selected connections;
* selected Routes.

Partial Isolation must identify explicit targets.

Full Isolation must not masquerade as a partial target list.

Isolation may only restrict capabilities held by the target Assignment.

It cannot invent a new capability in order to suspend it.

Isolation is temporary containment.

It is not Cell deletion, Role revocation, or value confiscation.

### Route Suspension Receipt

A Route Suspension may affect:

* the complete Route;
* selected Stages;
* selected Formation connections.

Fallback behavior may:

* activate a declared fallback candidate;
* switch to another declared Route;
* place the operation on hold;
* perform no fallback.

Stage and connection identifiers must exist in the referenced Route or
Formation.

A reroute must identify the fallback target and the activation evidence.

Suspension does not erase the original Route or Route Decision.

### Cell Recovery Assessment

A Recovery Assessment may check:

* Manifest integrity;
* Activation validity;
* Assignment validity;
* Authority Scope integrity;
* capability operation;
* data integrity;
* independent Audit clearance;
* security clearance;
* Route compatibility;
* capacity.

Supported states are:

* `not_ready`;
* `conditionally_ready`;
* `ready`.

A `ready` assessment requires all required checks to pass and no blockers.

A `conditionally_ready` assessment requires explicit conditions.

A Recovery Assessment is evidence that a Cell may be ready.

It is not authority to resume duty.

### Cell Reactivation Receipt

A Reactivation Receipt records a separate federation decision.

Supported modes include:

* `limited`;
* `full`;
* `replacement`.

Full reactivation requires:

* a `ready` Recovery Assessment;
* a lifted Isolation Order;
* lifted Route suspensions for restored Routes;
* a resolved or closed Incident;
* exact restoration of the original Assignment capabilities.

Limited reactivation may rely on a `ready` or `conditionally_ready`
assessment, but it must identify explicit conditions.

Reactivation must remain inside the original authority boundary.

---

## v0.5 — Federation Reconfiguration and Operational Exercises

### Federation Reconfiguration Plan

A Reconfiguration Plan may propose:

* adding a Node;
* removing a Node;
* replacing an Assignment;
* changing Node status;
* changing Node position;
* adding a connection;
* removing a connection;
* activating a Route;
* suspending a Route;
* rebalancing capacity.

Approved, executing, and completed Plans require:

* an explicit decision;
* risk assessments;
* mitigation references;
* rollback operations;
* a rollback policy;
* preservation of mandatory Roles.

```text
Reconfiguration Plan
≠ live Formation mutation
```

The Plan records what should change.

Separate execution records prove what did change.

### Cell Replacement Record

A Cell Replacement Record replaces the Assignment serving one Formation Node.

It verifies:

* source Node existence;
* source Assignment matching;
* replacement Assignment existence;
* Role compatibility;
* capability compatibility;
* authority-preservation mode;
* source acknowledgement;
* target acknowledgement;
* coordinator acknowledgement;
* execution evidence.

Replacement may preserve or narrow shared authority.

It may not expand it.

### Capacity Rebalancing Receipt

Capacity Rebalancing redistributes operational workload shares.

It does not allocate Royalty or economic value.

The following relations must hold:

```text
sum(before.share) = 1
sum(after.share)  = 1
```

Each participant must resolve to a Formation Node and matching Role Assignment.

The before and after distributions must differ.

An applied Rebalancing requires an explicit decision and execution time.

### Federation Drill Record

Supported Drill types include:

* `failover`;
* `recovery`;
* `route_switch`;
* `capacity_spike`;
* `authority_violation`;
* `data_integrity`;
* `dispute_holdback`;
* `full_cycle`.

Supported environments include:

* `tabletop`;
* `simulation`;
* `staging`;
* `controlled_production`.

A Drill defines mandatory and optional objectives.

A `passed` Drill requires every mandatory objective to pass.

A Drill may reference Reconfiguration, Replacement, Rebalancing, Isolation,
Recovery, or Route records.

A Drill is a controlled exercise.

It is not automatically a live Incident declaration.

### Operational Conformance Report

An Operational Conformance Report aggregates evaluated records and required
checks.

Supported states include:

* `conformant`;
* `conditionally_conformant`;
* `nonconformant`;
* `incomplete`.

A v0.5 `conformant` report must include minimum evidence covering:

* a Reconfiguration Plan;
* a Cell Replacement Record;
* a Capacity Rebalancing Receipt;
* a Federation Drill Record.

Every required check must pass.

A conditionally conformant report must identify its conditions.

A nonconformant report must expose failed checks.

An incomplete report must identify missing evidence.

The Report demonstrates protocol consistency.

It does not prove:

* factual truth;
* cybersecurity;
* legal compliance;
* economic fairness;
* regulatory certification.

---

## Normal operations loop

```text
Activation Request
    ↓
Readiness Assessment
    ↓
Activation Receipt
    ↓
Role Assignment
    ↓
Authority Binding
    ↓
Formation
    ↓
Route Decision
    ↓
Value Flow Route
    ↓
Handoff or Rotation
```

This is the ordinary path for placing Cells into controlled operation.

---

## Incident-response loop

```text
Operational Incident
    ↓
Containment decision
    ↓
Cell Isolation
    ↓
Route Suspension or fallback activation
    ↓
Recovery Assessment
    ↓
Reactivation Receipt
```

The loop separates observation, containment, readiness, and permission.

---

## Continuous-improvement loop

```text
Weakness observed
    ↓
Reconfiguration Plan
    ↓
Risk and rollback assessment
    ↓
Cell Replacement
    ↓
Capacity Rebalancing
    ↓
Federation Drill
    ↓
Operational Conformance Report
    ↓
Next improvement
```

This allows the federation to test and improve its own operational structure.

---

## Repository structure

```text
royalty-cell-federation-operations-protocol/
├── .github/
│   └── workflows/
│       └── validate.yml
├── schemas/
│   ├── cell-activation-request.schema.json
│   ├── cell-readiness-assessment.schema.json
│   ├── cell-activation-receipt.schema.json
│   ├── cell-suspension-receipt.schema.json
│   ├── operational-role-assignment.schema.json
│   ├── authority-scope-binding.schema.json
│   ├── cell-handoff-record.schema.json
│   ├── duty-rotation-record.schema.json
│   ├── federation-formation-record.schema.json
│   ├── cell-route-decision-receipt.schema.json
│   ├── value-flow-route.schema.json
│   ├── formation-change-record.schema.json
│   ├── operational-incident-record.schema.json
│   ├── cell-isolation-order.schema.json
│   ├── route-suspension-receipt.schema.json
│   ├── cell-recovery-assessment.schema.json
│   ├── cell-reactivation-receipt.schema.json
│   ├── federation-reconfiguration-plan.schema.json
│   ├── cell-replacement-record.schema.json
│   ├── capacity-rebalancing-receipt.schema.json
│   ├── federation-drill-record.schema.json
│   └── operational-conformance-report.schema.json
├── specs/
│   ├── cell-activation-and-readiness.md
│   ├── operational-roles-and-handoffs.md
│   ├── federation-formation-and-routing.md
│   ├── operational-incident-isolation-and-recovery.md
│   └── federation-reconfiguration-and-exercises.md
├── examples/
│   ├── pass/
│   └── fail/
├── scripts/
│   └── validate_examples.py
├── requirements.txt
├── README.md
└── CHANGELOG.md
```

---

## Validation

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run the complete conformance suite

```bash
python scripts/validate_examples.py
```

The validator performs:

1. YAML loading;
2. record-type-specific JSON Schema validation;
3. record-type-specific semantic validation;
4. local cross-record resolution;
5. upstream authority-boundary validation;
6. Role, capability, Cell, Formation, and Route matching;
7. lifecycle and timestamp-order validation;
8. fallback and recovery validation;
9. Decimal-based capacity-share validation;
10. Drill objective validation;
11. Operational Conformance Report validation;
12. passing-example verification;
13. expected-failure verification.

Files under `examples/pass` must pass every applicable validation stage.

Files under `examples/fail` must fail at least one validation stage.

A successful run ends with:

```text
All Royalty Cell Federation Operations Protocol examples behaved as expected.
```

Any passing example that fails causes a non-zero process exit.

Any expected-failure example that unexpectedly passes also causes a non-zero
process exit.

---

## Conformance model

Protocol conformance has two principal layers.

### Schema conformance

The document validates against the JSON Schema associated with its
`record_type`.

### Semantic conformance

The document satisfies cross-field and cross-record protocol rules.

```text
Schema-valid
≠ semantically valid

Semantically valid
≠ factually true

Factually supported
≠ legally certified
```

The conformance suite validates protocol structure.

External Audit remains necessary to verify underlying Evidence.

---

## Expected-failure coverage

The repository includes intentionally invalid examples covering conditions such
as:

### v0.1

* emergency activation without justification;
* a ready assessment containing a failed required check;
* activation without a resolvable Readiness Assessment;
* activation omitting requested roles or capabilities;
* partial suspension without explicit targets.

### v0.2

* Role Assignment capability expansion;
* Authority Binding capability expansion;
* completed Handoff without target acceptance;
* Handoff from an Assignment to itself;
* active Rotation with multiple current Assignments.

### v0.3

* active Formation missing a required Role;
* Formation connection referencing an unknown Node;
* approved decision selecting a rejected candidate;
* Value Flow Route path differing from the selected candidate;
* applied Formation Change removing mandatory Audit coverage.

### v0.4

* resolved Incident without a resolution record;
* Isolation targeting a capability absent from the Assignment;
* Stage suspension without a Stage target;
* ready Recovery Assessment containing a failed required check;
* Reactivation expanding Assignment capabilities.

### v0.5

* approved Reconfiguration Plan without rollback operations;
* Cell Replacement expanding capabilities;
* Capacity Rebalancing shares not summing to one;
* passed Drill containing a failed mandatory objective;
* conformant Report containing a failed required check.

These are conformance tests, not broken examples.

They demonstrate that invalid operational states are rejected intentionally.

---

## Security considerations

Implementations should account for:

* forged Activation Receipts;
* stale Readiness Assessments;
* role impersonation;
* authority drift;
* privilege expansion through downstream records;
* duplicate active duty;
* Handoff omission;
* unaccepted mandatory pending tasks;
* Formation Node substitution;
* malicious Route scoring;
* hidden Route overrides;
* fallback loops;
* split-brain routing;
* Incident suppression;
* fabricated Incident severity;
* indefinite Isolation;
* unauthorized Route suspension;
* false Recovery Evidence;
* premature Reactivation;
* replacement-Cell impersonation;
* capacity manipulation;
* rollback omission;
* Drill results presented as live Evidence;
* false Operational Conformance Reports;
* replayed execution references;
* collusive federation decisions.

Protocol conformance does not prove that the supplied Evidence is authentic.

Signed Evidence, trusted timestamps, independent Audit, and protected storage may
be required in real deployments.

---

## Privacy considerations

Federation operations records may expose:

* Cell identities;
* human or agent operator identities;
* Role Assignments;
* Authority Scopes;
* internal Routes;
* fallback topology;
* security weaknesses;
* Incident details;
* capacity constraints;
* recovery tests;
* Audit results;
* dispute information;
* operational schedules.

Implementations should apply data minimization.

Public records may expose:

* a digest;
* a timestamp;
* a redacted state;
* a protected Evidence reference;
* a non-sensitive summary;

instead of publishing confidential operational details.

Visibility and export controls should remain consistent with the policies of the
underlying Royalty Cells.

---

## Non-goals

Royalty Cell Federation Operations Protocol v0.5 does not:

* define Origin, Usage, Derivative, Contribution, Allocation, or Royalty
  records;
* replace Royalty Cell Protocol;
* execute financial settlement;
* allocate Royalty value;
* establish final legal authority;
* certify regulatory compliance;
* prove that an Incident involved misconduct;
* replace cybersecurity Incident-response procedures;
* replace human emergency command;
* automatically activate a ready Cell;
* automatically reactivate a recovered Cell;
* create one global federation controller;
* require one universal Formation;
* require one universal Route-scoring method;
* guarantee availability;
* guarantee Evidence authenticity;
* guarantee economic fairness;
* require blockchain infrastructure;
* require cryptocurrency;
* silently mutate historical records.

---

## Adoption model

The protocol supports gradual adoption.

A small federation may begin with:

* YAML records;
* JSON Schema;
* Git history;
* manual readiness reviews;
* human-issued Activation Receipts;
* manually selected Routes;
* tabletop Drills;
* local CI validation.

A more advanced implementation may later add:

* cryptographic signatures;
* policy engines;
* automated Route evaluation;
* live monitoring;
* machine-issued Incident Records;
* controlled failover;
* external Audit;
* cross-Federation coordination.

The protocol does not require the advanced implementation before the records
become useful.

---

## Relationship to the wider Royalty OS

```text
Royalty Cell Protocol
    ↓
defines autonomous value-return Cells

Royalty Cell Federation Operations Protocol
    ↓
places those Cells into live bounded operation

Civilization OS Interoperability Profile
    ↓
connects the wider protocol families

Operational conformance and exercises
    ↓
test whether the connected structure can survive real conditions
```

Royalty Cell Protocol provides the economic Cells.

Federation Operations Protocol provides their movement, coordination, reflexes,
and recovery.

---

## Versioning

The repository uses semantic versioning during active protocol development.

```text
v0.1 — Activation and readiness
v0.2 — Roles, authority, handoffs, and rotation
v0.3 — Formation, routing, and live Formation changes
v0.4 — Incidents, Isolation, suspension, recovery, and Reactivation
v0.5 — Reconfiguration, replacement, capacity, Drills, and conformance
```

The `v0.1`–`v0.5` cycle defines the first complete federation-operations
lifecycle.

Mature components may later be extracted into dedicated profiles or protocols
without turning the repository into one indivisible system.

---

## Summary

Royalty Cell Federation Operations Protocol allows a federation to record:

```text
which Cells may operate,
which duties they hold,
which authority they inherit,
where they are positioned,
which Routes they use,
how they hand off responsibility,
how they respond to partial failure,
how they recover,
how the Formation is reorganized,
how workload is redistributed,
how resilience is tested,
and how operational conformance is reported.
```

The protocol does not seek one all-powerful central controller.

It creates a common operational language through which independently governed
Royalty Cells can coordinate without surrendering their local autonomy.

The result is a federation that can move, fail, recover, reorganize, and learn.
