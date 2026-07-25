# Federation Formation and Routing

Version: 0.3.0

## 1. Purpose

Version 0.3 converts activated and role-bound Royalty Cells into an operational
formation and defines how value-related records are routed through that
formation.

```text
Operational Role Assignments
    ↓
Federation Formation
    ↓
Route Candidate Evaluation
    ↓
Route Decision
    ↓
Value Flow Route
    ↓
Formation Change
```

## 2. Required separation

```text
Formation membership
is not unrestricted authority.

Route selection
is not route execution.

A Value Flow Route
is not proof that every stage completed.

Formation Change
is not silent mutation of the original Formation Record.
```

## 3. Federation Formation Record

A Formation Record places Operational Role Assignments into named nodes and
connects those nodes through explicit operational edges.

An active Formation must:

- reference locally available Assignments when marked resolved;
- cover every required role type;
- identify an activation time;
- contain at least one active node;
- keep every required connection active;
- keep fallback nodes inside the declared node set.

A `wagon_fort` Formation must contain at least one `core` node and at least one
`perimeter` node.

## 4. Cell Route Decision Receipt

A Route Decision compares candidate node paths inside one Formation.

An approved decision must:

- reference an active Formation;
- select an eligible candidate;
- satisfy required roles and capabilities;
- remain within the declared maximum hop count;
- include an auditor when audit is required;
- define a distinct eligible fallback when fallback is required;
- select the highest-scoring eligible candidate unless an override is recorded.

Every decision declares:

```yaml
 decision_effect: route_decision_only
```

## 5. Value Flow Route

A Value Flow Route materializes the selected candidate as ordered stages.

The stage path must exactly match the selected candidate path. Stage sequence
numbers must be contiguous and begin at one. Every stage Assignment, role, and
capability set must match the Formation and its upstream Role Assignment.

An active route must have exactly one active stage. A completed route must have
all stages completed and identify `completed_at`.

Every route declares:

```yaml
route_effect: value_flow_route_only
```

## 6. Formation Change Record

A Formation Change records bounded operations against an existing Formation.
It does not rewrite the original Formation Record.

Applied changes must preserve all required role coverage. Changes affecting an
active route must declare their route impact and required action.

Every change declares:

```yaml
change_effect: formation_change_record_only
```

## 7. Conformance

A v0.3 record conforms when it validates against its JSON Schema, all local
references resolve, formation roles and connections remain valid, selected
routes satisfy declared requirements, route stages match the selected path,
and applied Formation Changes preserve mandatory operational coverage.
