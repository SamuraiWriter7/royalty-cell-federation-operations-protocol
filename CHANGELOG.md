# Changelog

All notable changes to the Royalty Cell Federation Operations Protocol are
documented in this file.

The project follows semantic versioning while the protocol remains in active
development.

---

## [Unreleased]

### Planned

* Cross-Federation operational coordination profiles.
* Long-duration resilience and chaos-testing profiles.
* Multi-Formation dependency validation.
* Cross-Federation Handoff and Route examples.
* Split-brain detection profiles.
* Stable compatibility-profile preparation.
* Preparation for a future `v1.0` conformance baseline.

---

## [0.5.0] - 2026-07-25

### Added

* Federation Reconfiguration Plan JSON Schema.
* Federation Cell Replacement Record JSON Schema.
* Federation Capacity Rebalancing Receipt JSON Schema.
* Federation Drill Record JSON Schema.
* Federation Operational Conformance Report JSON Schema.
* Federation Reconfiguration and Operational Exercises normative
  specification.
* Reconfiguration identifiers.
* Source-Formation references.
* Reconfiguration objectives.
* Reconfiguration trigger types.
* Proposed Formation operations:

  * add Node;
  * remove Node;
  * replace Assignment;
  * update Node status;
  * update Node position;
  * add connection;
  * remove connection;
  * activate Route;
  * suspend Route;
  * rebalance capacity.
* Rollback Formation operations.
* Reconfiguration risk assessments.
* Risk severity declarations.
* Risk likelihood declarations.
* Mitigation references.
* Mandatory-Role preservation.
* Reconfiguration decisions.
* Reconfiguration Authorization references.
* Reconfiguration execution references.
* Reconfiguration lifecycle states.
* Cell Replacement identifiers.
* Source-Node references.
* Source-Assignment references.
* Replacement-Assignment references.
* Shared-capability declarations.
* Replacement authority-preservation modes.
* Source, target, and coordinator acknowledgements.
* Replacement execution records.
* Capacity Rebalancing identifiers.
* Before-and-after capacity distributions.
* Normalized workload shares.
* Capacity-unit declarations.
* Rebalancing reason classifications.
* Rebalancing decisions.
* Rebalancing execution timestamps.
* Federation Drill identifiers.
* Drill types:

  * failover;
  * recovery;
  * Route switch;
  * capacity spike;
  * authority violation;
  * data integrity;
  * dispute Holdback;
  * full cycle.
* Drill environments:

  * tabletop;
  * simulation;
  * staging;
  * controlled production.
* Drill objectives.
* Mandatory and optional objective classifications.
* Drill steps.
* Expected results.
* Actual results.
* Drill execution references.
* Drill findings.
* Drill recommendations.
* Drill outcomes.
* Operational Conformance Report identifiers.
* Evaluated-record sets.
* Required conformance checks.
* Conformance conditions.
* Nonconformance findings.
* Missing-Evidence declarations.
* Report decisions.
* Report Evidence.
* Conformance states:

  * conformant;
  * conditionally conformant;
  * nonconformant;
  * incomplete.
* Passing Federation Reconfiguration Plan example.
* Passing Cell Replacement Record example.
* Passing Capacity Rebalancing Receipt example.
* Passing Federation Drill Record example.
* Passing Operational Conformance Report example.
* Expected-failure example for an approved Reconfiguration Plan without
  rollback operations.
* Expected-failure example for Cell Replacement capability expansion.
* Expected-failure example for invalid capacity-share totals.
* Expected-failure example for a passed Drill with a failed mandatory
  objective.
* Expected-failure example for a conformant Report with a failed required
  check.
* Complete `v0.1`–`v0.5` operational conformance validation.

### Validation

* Added local Formation resolution from Reconfiguration Plans.
* Added local Assignment resolution from Reconfiguration Plans.
* Added proposed-operation Node validation.
* Added proposed-operation Assignment validation.
* Added proposed-operation connection validation.
* Added proposed-operation Route validation.
* Added duplicate Reconfiguration operation-ID detection.
* Added mandatory-Role preservation after proposed changes.
* Added decision requirements for approved, executing, completed, rejected,
  and cancelled Plans.
* Added rollback-operation requirements for approved, executing, and completed
  Plans.
* Added rollback-policy requirements.
* Added risk-assessment requirements.
* Added Reconfiguration execution-reference requirements.
* Added source-Node resolution from Cell Replacement Records.
* Added source-Assignment matching.
* Added replacement-Assignment resolution.
* Added replacement Role-type compatibility validation.
* Added shared-capability intersection validation.
* Added rejection of authority expansion through Cell Replacement.
* Added exact and narrowed authority-preservation validation.
* Added source, target, and coordinator acknowledgement requirements.
* Added completed-Replacement execution requirements.
* Added Decimal-based before-share normalization.
* Added Decimal-based after-share normalization.
* Added Formation Node and Assignment matching for Capacity Rebalancing.
* Added duplicate capacity-participant detection.
* Added rejection of unchanged before-and-after distributions.
* Added decision and execution requirements for applied Rebalancing.
* Added mandatory Drill objective/result coverage.
* Added duplicate Drill objective-ID detection.
* Added duplicate Drill step-ID detection.
* Added local execution-reference resolution from Drills.
* Added rejection of passed Drills with failed mandatory objectives.
* Added required findings for failed Drills.
* Added v0.5 minimum-record coverage for conformant reports.
* Added evaluated-record resolution.
* Added duplicate evaluated-record detection.
* Added required-check consistency for each conformance state.
* Added required conditions for conditionally conformant reports.
* Added required findings for nonconformant reports.
* Added required missing-Evidence declarations for incomplete reports.

### Protocol decisions

* A Reconfiguration Plan proposes change; it does not mutate live state.
* Historical Formation records remain append-only.
* Approved Reconfiguration Plans require explicit rollback paths.
* Reconfiguration must preserve mandatory Roles.
* Reconfiguration risks and mitigations must remain visible.
* Cell Replacement cannot create new authority.
* Replacement may only preserve or narrow capabilities shared by source and
  target Assignments.
* Completed Cell Replacement requires source, target, and coordinator
  acknowledgement.
* Capacity Rebalancing changes operational workload, not economic Allocation.
* Capacity shares must remain normalized before and after Rebalancing.
* A Federation Drill is a controlled exercise, not a live Incident declaration.
* A passed Drill requires every mandatory objective to pass.
* Failed Drills must expose findings.
* An Operational Conformance Report demonstrates protocol consistency.
* Operational conformance does not prove factual truth.
* Operational conformance does not establish legal or regulatory
  certification.
* Every Reconfiguration Plan declares:

```yaml
plan_effect: reconfiguration_plan_only
```

* Every Cell Replacement Record declares:

```yaml
replacement_effect: cell_replacement_only
```

* Every Capacity Rebalancing Receipt declares:

```yaml
rebalance_effect: capacity_rebalancing_only
```

* Every Federation Drill Record declares:

```yaml
drill_effect: drill_record_only
```

* Every Operational Conformance Report declares:

```yaml
report_effect: operational_conformance_report_only
```

### Completed lifecycle

Version 0.5 completes the initial federation-operations cycle:

```text
Activation and Readiness
    ↓
Roles and Authority
    ↓
Formation and Routing
    ↓
Incident Isolation and Recovery
    ↓
Reconfiguration and Replacement
    ↓
Capacity Rebalancing
    ↓
Federation Drill
    ↓
Operational Conformance Report
```

---

## [0.4.0] - 2026-07-25

### Added

* Federation Operational Incident Record JSON Schema.
* Federation Cell Isolation Order JSON Schema.
* Federation Route Suspension Receipt JSON Schema.
* Federation Cell Recovery Assessment JSON Schema.
* Federation Cell Reactivation Receipt JSON Schema.
* Operational Incident Isolation and Recovery normative specification.
* Incident identifiers.
* Incident types:

  * Node failure;
  * capability failure;
  * authority violation;
  * Route failure;
  * reference failure;
  * Audit failure;
  * settlement risk;
  * policy conflict;
  * overload;
  * security event;
  * data integrity;
  * other.
* Incident-severity classifications.
* Incident lifecycle states.
* Affected Formation references.
* Affected Node declarations.
* Affected Assignment declarations.
* Affected Value Flow Route declarations.
* Containment requirements.
* Recommended containment actions.
* Incident resolutions.
* Remedy references.
* Incident Evidence.
* Cell Isolation identifiers.
* Incident references from Isolation Orders.
* Formation references from Isolation Orders.
* Target-Node references.
* Full and partial Isolation modes.
* Capability Isolation targets.
* Formation-connection Isolation targets.
* Route Isolation targets.
* Isolation decisions.
* Isolation Authorization references.
* Active, lifted, and cancelled Isolation states.
* Isolation lift decisions.
* Route Suspension identifiers.
* Full, Stage-level, and connection-level Route suspension.
* Fallback-candidate activation.
* Route switching.
* Hold behavior.
* Route-suspension decisions.
* Route-suspension execution references.
* Route-suspension lift decisions.
* Cell Recovery Assessment identifiers.
* Recovery requirements.
* Recovery-check categories.
* Capability-test requirements.
* independent Audit clearance.
* security clearance.
* Route compatibility checks.
* capacity checks.
* Recovery blockers.
* Recovery conditions.
* Recovery states:

  * not ready;
  * conditionally ready;
  * ready.
* Cell Reactivation Receipt identifiers.
* Limited, full, and replacement Reactivation modes.
* Restored capabilities.
* Restored Routes.
* Reactivation conditions.
* Reactivation decisions.
* Reactivation Authorization references.
* Passing Operational Incident example.
* Passing Cell Isolation example.
* Passing Route Suspension example.
* Passing Cell Recovery Assessment example.
* Passing Cell Reactivation example.
* Expected-failure example for a resolved Incident without resolution.
* Expected-failure example for capability expansion through Isolation.
* Expected-failure example for Stage suspension without a Stage target.
* Expected-failure example for a ready Recovery Assessment containing a failed
  required check.
* Expected-failure example for capability expansion through Reactivation.

### Validation

* Added local Formation resolution from Incident Records.
* Added Incident federation matching.
* Added Incident affected-Node resolution.
* Added Incident Node-to-Assignment matching.
* Added Incident affected-Route resolution.
* Added Incident Route-to-Formation matching.
* Added major and critical containment requirements.
* Added Incident resolution requirements.
* Added Incident resolution-time validation.
* Added Incident remedy-reference requirements.
* Added local Incident resolution from Isolation Orders.
* Added local Formation resolution from Isolation Orders.
* Added Isolation target-Node matching.
* Added rejection of capability expansion through Isolation.
* Added Formation connection-target validation.
* Added Route-target validation.
* Added partial-Isolation target requirements.
* Added full-Isolation scope constraints.
* Added active-Isolation requirements.
* Added lifted-Isolation requirements.
* Added cancelled-Isolation requirements.
* Added local Incident resolution from Route Suspension Receipts.
* Added local Formation resolution from Route Suspension Receipts.
* Added local Value Flow Route resolution.
* Added Stage-target validation.
* Added connection-target validation.
* Added eligible fallback-candidate validation.
* Added Route-switch target validation.
* Added Route suspension, reroute, hold, lift, and cancellation requirements.
* Added local Isolation resolution from Recovery Assessments.
* Added local Route Suspension resolution from Recovery Assessments.
* Added Recovery target-Node consistency.
* Added required capability-test coverage.
* Added Audit-clearance requirements.
* Added security-clearance requirements.
* Added Route-compatibility requirements.
* Added ready-state consistency validation.
* Added conditionally-ready consistency validation.
* Added not-ready blocker validation.
* Added local Recovery Assessment resolution from Reactivation Receipts.
* Added exact target-Node matching across Incident, Isolation, Recovery, and
  Reactivation records.
* Added rejection of capability expansion during Reactivation.
* Added exact capability restoration for full Reactivation.
* Added restored-Route recovery coverage.
* Added lifted-Isolation requirements.
* Added lifted Route-suspension requirements.
* Added resolved or closed Incident requirements.
* Added limited-Reactivation condition requirements.

### Protocol decisions

* An Incident Record records observation; it does not prove misconduct.
* Incident declaration does not itself impose Isolation.
* Incident declaration does not itself suspend a Route.
* Major and critical Incidents require visible containment.
* Isolation is temporary operational containment.
* Isolation does not delete a Cell.
* Isolation does not revoke historical records.
* Partial Isolation must identify explicit bounded targets.
* Isolation cannot expand the target's authority in order to suspend it.
* Route suspension does not erase the original Route.
* Route suspension does not erase the Route Decision.
* Rerouting requires a declared fallback and activation Evidence.
* Recovery readiness is not reactivation authority.
* A ready assessment does not automatically restore duty.
* Full Reactivation requires a ready Recovery Assessment.
* Limited Reactivation requires explicit conditions.
* Reactivation capabilities cannot exceed the original Role Assignment.
* Reactivation requires lifted Isolation.
* Restored Routes require lifted Route suspensions.
* Full Reactivation requires a resolved or closed Incident.
* Every Operational Incident Record declares:

```yaml
incident_effect: incident_record_only
```

* Every Cell Isolation Order declares:

```yaml
isolation_effect: node_isolation_only
```

* Every Route Suspension Receipt declares:

```yaml
route_suspension_effect: route_suspension_only
```

* Every Cell Recovery Assessment declares:

```yaml
assessment_effect: recovery_assessment_only
```

* Every Cell Reactivation Receipt declares:

```yaml
receipt_effect: reactivation_record_only
```

### Incident lifecycle

```text
Operational Incident
    ↓
Cell Isolation
    ↓
Route Suspension or fallback
    ↓
Recovery Assessment
    ↓
Cell Reactivation
```

---

## [0.3.0] - 2026-07-25

### Added

* Federation Formation Record JSON Schema.
* Cell Route Decision Receipt JSON Schema.
* Federation Value Flow Route JSON Schema.
* Federation Formation Change Record JSON Schema.
* Federation Formation and Routing normative specification.
* Origin-authority Operational Role Assignment example.
* Usage-router Operational Role Assignment example.
* Wagon-fort Formation example.
* Formation identifiers.
* Formation types:

  * serial;
  * parallel;
  * hub and spoke;
  * layered;
  * mesh;
  * wagon fort;
  * custom.
* Formation lifecycle states.
* Formation Node identifiers.
* Formation Node positions:

  * core;
  * perimeter;
  * relay;
  * gateway;
  * reserve;
  * observer.
* Formation Node Role Assignment references.
* Formation Node lifecycle states.
* Formation required-Role declarations.
* Formation connections.
* Required and optional connection declarations.
* Connection lifecycle states.
* Fallback-Node references.
* Formation coordination policies.
* Formation quorum declarations.
* Route Decision identifiers.
* Route requirements.
* Required-Role declarations.
* Required-capability declarations.
* maximum-Hop limits.
* Audit-presence requirements.
* fallback requirements.
* Route-candidate records.
* Candidate Node paths.
* Candidate scores.
* Candidate eligibility states.
* Candidate rejection reasons.
* Selected-candidate references.
* Fallback-candidate references.
* Route-decision overrides.
* Value Flow Route identifiers.
* Ordered Route Stages.
* Stage Node references.
* Stage Assignment references.
* Stage Role declarations.
* Stage capability declarations.
* Input record types.
* Output record types.
* Stage lifecycle states.
* Route failure policies.
* unresolved-reference policies.
* Formation Change identifiers.
* Formation Change operations:

  * add Node;
  * remove Node;
  * replace Assignment;
  * update Node status;
  * update Node position;
  * add connection;
  * remove connection;
  * update connection status.
* Route-impact declarations.
* Passing Formation example.
* Passing Route Decision example.
* Passing Value Flow Route example.
* Passing Formation Change example.
* Expected-failure example for an active Formation missing a mandatory Role.
* Expected-failure example for a connection referencing an unknown Node.
* Expected-failure example for approval of a rejected Route candidate.
* Expected-failure example for a Value Flow Route path mismatch.
* Expected-failure example for an applied Formation Change removing Audit
  coverage.

### Validation

* Added local Operational Role Assignment resolution from Formation Nodes.
* Added Formation federation matching.
* Added Formation Cell matching.
* Added duplicate Node-ID detection.
* Added duplicate Assignment-use detection.
* Added duplicate connection-ID detection.
* Added connection endpoint validation.
* Added self-connection rejection.
* Added mandatory-Role coverage for active Formations.
* Added required-connection activation validation.
* Added fallback-Node resolution.
* Added coordination-quorum validation.
* Added wagon-fort core and perimeter requirements.
* Added active-Formation lifecycle requirements.
* Added suspended-Formation lifecycle requirements.
* Added retired-Formation lifecycle requirements.
* Added local Formation resolution from Route Decisions.
* Added candidate Node-path resolution.
* Added candidate required-Role coverage.
* Added candidate required-capability coverage.
* Added maximum-Hop validation.
* Added Audit-presence validation.
* Added candidate eligibility validation.
* Added selected-candidate validation.
* Added fallback-candidate validation.
* Added highest-score selection validation.
* Added explicit override support for lower-scoring candidates.
* Added local Route Decision resolution from Value Flow Routes.
* Added exact selected-path-to-Stage-path validation.
* Added Stage Assignment matching.
* Added Stage Role matching.
* Added Stage capability matching.
* Added contiguous Stage sequence validation.
* Added exactly-one-active-Stage validation.
* Added completed-Route Stage requirements.
* Added local Formation resolution from Formation Changes.
* Added local Route resolution from Formation Changes.
* Added Change-operation target validation.
* Added duplicate Change-operation detection.
* Added mandatory-Role preservation after applied Formation Changes.
* Added Route-impact requirements.
* Added fallback-candidate requirements for affected Routes.

### Protocol decisions

* Formation membership does not create new authority.
* A Formation Node must be bound to an upstream Operational Role Assignment.
* A Formation Node may only exercise upstream capabilities.
* A Route Decision selects a candidate path but does not execute it.
* An eligible candidate must satisfy every declared Role and capability
  requirement.
* A lower-scoring candidate requires an explicit override.
* A required fallback must differ from the selected candidate.
* A Value Flow Route must reproduce the selected candidate path exactly.
* Route Stages may only invoke capabilities granted upstream.
* An active Route has exactly one active Stage.
* Formation Changes are append-only operational records.
* Formation Changes must not silently rewrite historical Formation records.
* Applied Formation Changes must preserve every mandatory Role.
* Route impacts must remain visible during live Formation changes.
* Every Federation Formation Record declares:

```yaml
formation_effect: formation_record_only
```

* Every Cell Route Decision Receipt declares:

```yaml
decision_effect: route_decision_only
```

* Every Value Flow Route declares:

```yaml
route_effect: value_flow_route_only
```

* Every Formation Change Record declares:

```yaml
change_effect: formation_change_record_only
```

### Formation lifecycle

```text
Operational Role Assignments
    ↓
Federation Formation
    ↓
Route Decision
    ↓
Value Flow Route
    ↓
Formation Change
```

---

## [0.2.0] - 2026-07-25

### Added

* Federation Operational Role Assignment JSON Schema.
* Federation Authority Scope Binding JSON Schema.
* Federation Cell Handoff Record JSON Schema.
* Federation Duty Rotation Record JSON Schema.
* Operational Roles and Handoffs normative specification.
* Operational Role Assignment identifiers.
* Activation Receipt references from Role Assignments.
* Role identifiers.
* Role types.
* Assignment modes:

  * primary;
  * fallback;
  * temporary;
  * relief;
  * emergency.
* Assignment lifecycle states.
* Assigned-capability declarations.
* Authority Scope references.
* Duty windows.
* Assignment decisions.
* Assignment Authorization references.
* Authority Scope Binding identifiers.
* Capability restrictions.
* Record-type restrictions.
* Operation restrictions.
* Resource restrictions.
* Route restrictions.
* Value limits.
* Time limits.
* Delegation policies.
* Human Review requirements.
* Dual-control requirements.
* Cell Handoff identifiers.
* Source-Assignment references.
* Target-Assignment references.
* Handoff capability declarations.
* Handoff Route declarations.
* Handoff resource declarations.
* State snapshots.
* Pending tasks.
* unresolved-reference items.
* Audit tasks.
* settlement-hold items.
* dispute tasks.
* Mandatory pending-item declarations.
* Source acknowledgement.
* Target acknowledgement.
* Coordinator acknowledgement.
* Duty Rotation identifiers.
* Rotation modes:

  * scheduled;
  * load based;
  * Incident based;
  * manual.
* Rotation participant Assignments.
* Rotation sequence entries.
* current-Assignment declarations.
* Primary and fallback auditor Assignment examples.
* Primary and reserve auditor Authority Binding examples.
* Reserve Cell Activation Request.
* Reserve Cell Readiness Assessment.
* Reserve Cell Activation Receipt.
* Passing Cell Handoff example.
* Passing Duty Rotation example.
* Expected-failure example for Role Assignment capability expansion.
* Expected-failure example for Authority Binding capability expansion.
* Expected-failure example for completed Handoff without target acceptance.
* Expected-failure example for self-Handoff.
* Expected-failure example for an active Rotation with two current
  Assignments.

### Validation

* Added local Activation Receipt resolution from Role Assignments.
* Added Role matching against the Activation Receipt.
* Added capability matching against the activated Role.
* Added global granted-capability matching.
* Added Authority Scope reference matching.
* Added rejection of downstream capability expansion.
* Added Assignment lifecycle validation.
* Added duty-window ordering validation.
* Added local Assignment resolution from Authority Bindings.
* Added capability-boundary validation.
* Added record-type boundary validation.
* Added operation boundary validation.
* Added resource boundary validation.
* Added Route boundary validation.
* Added delegation validation.
* Added value-limit validation.
* Added time-window validation.
* Added Human Review validation.
* Added dual-control validation.
* Added local Assignment and Binding resolution from Handoffs.
* Added Handoff source/target Role compatibility validation.
* Added Handoff capability-intersection validation.
* Added self-Handoff rejection.
* Added mandatory pending-item acceptance.
* Added completed-Handoff three-party acknowledgement requirements.
* Added local Assignment resolution from Duty Rotations.
* Added participant uniqueness validation.
* Added sequence coverage validation.
* Added duty-window overlap validation.
* Added exactly-one-current-Assignment rule for active Rotations.

### Protocol decisions

* Activation does not automatically place a Cell on live duty.
* A Role Assignment cannot exceed its Activation Receipt.
* An Authority Scope Binding may only narrow assigned authority.
* A Handoff transfers responsibility; it does not create authority.
* A completed Handoff requires source, target, and coordinator acceptance.
* Mandatory pending state must be accepted before Handoff completion.
* A Duty Rotation changes current duty.
* A Duty Rotation does not change Role permissions.
* An active Rotation has exactly one current Assignment.
* Every Operational Role Assignment declares:

```yaml
assignment_effect: operational_role_assignment_only
```

* Every Authority Scope Binding declares:

```yaml
binding_effect: authority_scope_binding_only
```

* Every Cell Handoff Record declares:

```yaml
handoff_effect: handoff_record_only
```

* Every Duty Rotation Record declares:

```yaml
rotation_effect: duty_rotation_record_only
```

### Authority lifecycle

```text
Activation Receipt
    ⊇ Operational Role Assignment
        ⊇ Authority Scope Binding
            ⊇ Handoff Scope
```

---

## [0.1.0] - 2026-07-25

### Added

* Initial repository structure.
* Federation Cell Activation Request JSON Schema.
* Federation Cell Readiness Assessment JSON Schema.
* Federation Cell Activation Receipt JSON Schema.
* Federation Cell Suspension Receipt JSON Schema.
* Cell Activation and Readiness normative specification.
* Federation identifiers.
* Royalty Cell references.
* Activation Request identifiers.
* Readiness Assessment identifiers.
* Activation Receipt identifiers.
* Suspension Receipt identifiers.
* Activation modes:

  * primary;
  * fallback;
  * temporary;
  * emergency.
* Requested operational roles.
* Requested capability declarations.
* Authority Scope references.
* Operation-context declarations.
* Operation objectives.
* Operation priorities.
* Requested start times.
* Temporary Activation windows.
* Emergency Activation justification.
* Activation Request lifecycle states.
* Activation Request Evidence.
* Readiness-policy references.
* Readiness-check identifiers.
* Readiness-check categories.
* Required and optional Readiness checks.
* Readiness-check states:

  * pass;
  * warn;
  * fail;
  * not applicable.
* Readiness states:

  * ready;
  * ready with conditions;
  * not ready;
  * unknown.
* Readiness blockers.
* Activation conditions.
* Assessment validity times.
* Assessment Evidence.
* Activation outcomes:

  * activated;
  * activated with conditions;
  * denied.
* Operational Role assignments inside Activation Receipts.
* Granted-capability declarations.
* Activation windows.
* Fallback Cell references.
* Emergency suspension authorities.
* Emergency-policy references.
* Activation decisions.
* Activation decision-policy references.
* Activation Authorization references.
* Activation Receipt Evidence.
* Full and partial suspension scopes.
* Role-level suspension targets.
* Capability-level suspension targets.
* Route-level suspension targets.
* Suspension reason codes.
* dispute-related suspension references.
* settlement-hold policy.
* new-operation policy during suspension.
* Suspension decisions.
* Active, lifted, and cancelled Suspension states.
* Suspension lift decisions.
* Suspension Evidence.
* Passing examples for all four v0.1 record types.
* Expected-failure example for emergency Activation without justification.
* Expected-failure example for a ready state containing a failed required
  check.
* Expected-failure example for Activation without a resolvable Readiness
  Assessment.
* Expected-failure example for Activation omitting requested Roles.
* Expected-failure example for partial Suspension without targets.
* Initial Python conformance validator.
* Initial GitHub Actions validation workflow.
* Initial README.
* Initial CHANGELOG.

### Validation

* Added JSON Schema validation for all v0.1 record types.
* Added unique Evidence identifier validation.
* Added duplicate requested-Role detection.
* Added requested-Role capability coverage validation.
* Added temporary Activation end-time requirements.
* Added emergency Activation justification requirements.
* Added Activation Request lifecycle validation.
* Added operation-window ordering validation.
* Added local Activation Request resolution.
* Added externally resolved Request reference requirements.
* Added Readiness Assessment federation matching.
* Added Readiness Assessment Cell matching.
* Added assessment time-order validation.
* Added assessment-expiration validation.
* Added duplicate Readiness-check detection.
* Added requested-capability check coverage.
* Added duplicate capability-check detection.
* Added ready-state consistency validation.
* Added ready-with-conditions consistency validation.
* Added not-ready blocker validation.
* Added local Readiness Assessment resolution.
* Added Request-to-Assessment relationship validation.
* Added Activation Receipt federation matching.
* Added Activation Receipt Cell matching.
* Added Activation decision time-order validation.
* Added Activation-window validation.
* Added duplicate assigned-Role detection.
* Added Role capability and globally granted-capability consistency.
* Added requested-Role Assignment coverage.
* Added requested-capability grant coverage.
* Added Readiness-to-outcome consistency.
* Added condition-propagation requirements.
* Added denied-outcome empty-authority requirements.
* Added local Activation Receipt resolution from Suspension Receipts.
* Added rejection of Suspension against a denied Cell.
* Added partial-Suspension target requirements.
* Added full-Suspension scope constraints.
* Added Suspension target-Role validation.
* Added Suspension target-capability validation.
* Added dispute-reference requirements.
* Added Suspension decision time-order validation.
* Added active-Suspension requirements.
* Added lifted-Suspension requirements.
* Added cancelled-Suspension requirements.
* Added pass-example and expected-failure behavior validation.

### Protocol decisions

* A Royalty Cell Manifest does not establish operational readiness.
* A Readiness Assessment does not grant operational authority.
* An Activation Request does not activate a Cell.
* Activation requires an explicit Receipt.
* Activation requires an Authorization reference.
* A ready Cell may still require a separate federation decision.
* Requested Roles and capabilities cannot silently disappear from an activated
  outcome.
* An activated Cell must include emergency suspension controls.
* A denied Activation grants no Roles or capabilities.
* Partial Suspension must identify explicit targets.
* A Suspension Receipt does not delete or retire a Cell.
* Suspension does not invalidate historical Royalty Cell records.
* Operational authority remains bounded by Role, capability, scope, and time.
* Every Cell Activation Request declares:

```yaml
request_effect: activation_request_only
```

* Every Cell Readiness Assessment declares:

```yaml
assessment_effect: readiness_assessment_only
```

* Every Cell Activation Receipt declares:

```yaml
receipt_effect: activation_record_only
```

* Every Cell Suspension Receipt declares:

```yaml
suspension_effect: operational_suspension_only
```

### Initial lifecycle

Version 0.1 establishes:

```text
Activation Request
    ↓
Readiness Assessment
    ↓
Activation Receipt
    ↓
Controlled Operation
    ↓
Partial or Full Suspension
```

This was the first step from static Royalty Cell records toward a living,
reconfigurable Royalty Cell federation.

---

## Initial `v0.1`–`v0.5` milestone

The first development cycle establishes the following operational structure:

```text
Cell Activation Request
    ↓
Cell Readiness Assessment
    ↓
Cell Activation Receipt
    ↓
Operational Role Assignment
    ↓
Authority Scope Binding
    ↓
Cell Handoff / Duty Rotation
    ↓
Federation Formation
    ↓
Cell Route Decision
    ↓
Value Flow Route
    ↓
Formation Change
    ↓
Operational Incident
    ↓
Cell Isolation / Route Suspension
    ↓
Cell Recovery Assessment
    ↓
Cell Reactivation Receipt
    ↓
Federation Reconfiguration Plan
    ↓
Cell Replacement
    ↓
Capacity Rebalancing
    ↓
Federation Drill
    ↓
Operational Conformance Report
```

The protocol now supports a federation that can:

* determine whether a Cell is ready;
* activate it explicitly;
* bind its authority;
* assign live duties;
* rotate or hand off those duties;
* place Cells into an operational Formation;
* choose and execute bounded Routes;
* record partial failures;
* isolate damaged or unsafe Nodes;
* activate fallbacks;
* assess recovery;
* restore authority without expanding it;
* plan reversible reconfiguration;
* replace Cells safely;
* redistribute operational capacity;
* exercise failure scenarios;
* report protocol conformance.

The result is not one centralized controller.

It is a shared operational language for many independently governed Royalty
Cells.
