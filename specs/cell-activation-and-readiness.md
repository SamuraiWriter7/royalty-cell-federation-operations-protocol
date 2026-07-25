# Cell Activation and Readiness Specification

Version: 0.1.0

## 1. Purpose

Version 0.1 defines the minimum records required to move a Royalty Cell from
registered existence into controlled federation operation.

It defines:

1. Federation Cell Activation Request
2. Federation Cell Readiness Assessment
3. Federation Cell Activation Receipt
4. Federation Cell Suspension Receipt

The operational sequence is:

```text
Activation Request
    ↓
Readiness Assessment
    ↓
Activation Decision
    ↓
Activation Receipt
    ↓
Operation
    ↓
Partial or Full Suspension when required

2. Required separation

Implementations MUST preserve these distinctions:

A Cell Manifest
is not proof that the Cell is operationally ready.

A Readiness Assessment
is not an Activation decision.

An Activation Receipt
is not proof that every later action was valid.

A Suspension Receipt
is not deletion, retirement, or confiscation.

3. Activation Request

3.1 Definition

An Activation Request states that a participant or federation authority wantsone Royalty Cell to receive operational roles and capabilities.

The request MUST identify:

the federation;

the Cell;

the requester;

the activation mode;

the requested roles;

the requested capabilities;

the readiness policy;

supporting Evidence.

3.2 Activation modes

Supported modes are:

primary

fallback

temporary

emergency

A temporary request MUST identify an intended end time.

An emergency request MUST include an emergency justification.

3.3 Role and capability consistency

Every capability required by a requested role MUST also appear in the globalrequested_capabilities list.

Role identifiers MUST be unique within one request.

3.4 Request lifecycle

Supported states are:

submitted

under_review

withdrawn

superseded

A withdrawn request MUST provide a reason.

A superseded request MUST identify its successor.

3.5 Request effect

Every Activation Request MUST declare:

request_effect: activation_request_only

The request does not activate the Cell.

4. Readiness Assessment

4.1 Definition

A Readiness Assessment evaluates whether the requested Cell is capable ofsafely receiving the requested operational authority.

It does not itself grant that authority.

4.2 Readiness checks

Checks may cover:

Manifest validity;

governance authority;

role coverage;

requested capabilities;

Allocation policy;

unresolved disputes;

interoperability;

audit coverage;

emergency controls;

operational capacity;

security.

Every requested capability MUST have a correspondingrequested_capability check.

4.3 Check states

Supported check states are:

pass

warn

fail

not_applicable

Required and optional checks remain distinguishable.

4.4 Readiness states

Supported readiness states are:

ready

ready_with_conditions

not_ready

unknown

A ready assessment:

MUST NOT contain required warning or failed checks;

MUST have no blockers;

MUST have no conditions;

MUST show every requested capability as passed.

A ready_with_conditions assessment:

MUST NOT contain a required failed check;

MUST contain at least one required warning;

MUST identify at least one condition;

MUST show requested capabilities as passed or warned.

A not_ready assessment:

MUST contain at least one required failed check;

MUST identify at least one blocker.

4.5 Assessment validity

An assessment MAY identify valid_until.

An Activation Receipt MUST NOT rely on a locally resolved assessment afterthat validity time.

4.6 Assessment effect

Every Readiness Assessment MUST declare:

assessment_effect: readiness_assessment_only

Readiness does not compel activation.

5. Activation Receipt

5.1 Definition

An Activation Receipt records the federation decision to:

activate the Cell;

activate it with conditions; or

deny activation.

5.2 Activation outcomes

Supported outcomes are:

activated

activated_with_conditions

denied

An activated outcome requires a ready assessment.

An activated_with_conditions outcome requires aready_with_conditions assessment and MUST preserve all assessmentconditions.

A denied outcome assigns no operational roles or capabilities.

5.3 Operational roles

Activated Cells MUST identify at least one operational role.

Every requested role MUST be represented in the Activation Receipt unless anew request or explicit policy exception replaces the original request.

Every capability granted through an operational role MUST appear in theglobal granted_capabilities list.

Every requested capability MUST be granted for an activated outcome.

5.4 Activation window

An activated Cell MUST identify an activation start time.

An optional end time MUST NOT be earlier than the start time.

5.5 Emergency controls

An activated Cell MUST identify:

one or more suspension authorities;

an emergency policy.

Emergency control is a prerequisite for operational freedom rather than areplacement for it.

5.6 Decision

Every Activation Receipt MUST identify:

the deciding authorities;

the decision time;

the governing policy;

the Authorization reference;

the rationale.

5.7 Receipt effect

Every Activation Receipt MUST declare:

receipt_effect: activation_record_only

The Receipt authorizes federation operation within the declared scope. It doesnot prove that every later action conforms to that authority.

6. Suspension Receipt

6.1 Definition

A Suspension Receipt records a temporary full or partial restriction placedon an activated Cell.

Suspension may respond to:

an incident;

a policy violation;

expired readiness;

capacity failure;

security risk;

a dispute;

manual intervention;

an emergency.

6.2 Scope

A suspension may be:

full; or

partial.

A partial suspension MUST identify at least one target:

role;

capability;

route.

A full suspension MUST NOT masquerade as a partial target list.

Locally targeted roles and capabilities MUST exist in the referencedActivation Receipt.

6.3 Settlement and new-operation policy

A Suspension Receipt MUST state what happens to settlement and new work.

Settlement actions include:

no special action;

holding pending settlements;

holding all settlements;

continuing already authorized settlements.

New operations may be:

blocked;

restricted;

allowed.

6.4 Suspension states

Supported states are:

active

lifted

cancelled

An active suspension MUST identify its effective time.

A lifted suspension MUST identify:

its original effective time;

the lift time;

a lift decision.

A cancelled suspension MUST identify:

the cancellation time;

the cancellation reason.

6.5 Dispute-related suspension

A suspension using reason_code: dispute MUST identify at least one disputereference.

6.6 Suspension effect

Every Suspension Receipt MUST declare:

suspension_effect: operational_suspension_only

Suspension does not delete the Cell, revoke its historical records, or settlethe underlying dispute.

7. Local and external resolution

Protocol references use:

resolved

externally_resolved

unresolved

A locally resolved reference MUST exist among the local passing records knownto the conformance validator.

An externally resolved reference MUST include record_ref.

An unresolved reference remains visible but MUST NOT silently receive thesame trust as a resolved reference.

8. Evidence

Every record MUST include at least one Evidence item.

Evidence identifiers MUST be unique inside each record.

Evidence may include:

Manifest snapshots;

policy records;

Authorization records;

capability tests;

capacity reports;

security assessments;

role assignments;

incident records;

signed statements;

external references.

Protocol conformance does not prove that the Evidence is authentic. ExternalAudit remains necessary.

9. Security considerations

Implementations SHOULD account for:

activation without a current readiness assessment;

fabricated readiness results;

omitted failed checks;

capability escalation;

role substitution;

expired readiness evidence;

unauthorized activation decisions;

missing emergency controls;

suspension of nonexistent roles;

indefinite emergency suspension;

false security incidents;

concealed settlement holds;

forged lift decisions.

10. Version 0.1 conformance

An Activation Request conforms when:

it validates against its JSON Schema;

role identifiers are unique;

role capability requirements are included in the request;

temporary and emergency requirements are satisfied;

lifecycle requirements are satisfied;

Evidence identifiers are unique.

A Readiness Assessment conforms when:

it validates against its JSON Schema;

its local request resolves;

Cell and federation identifiers match the request;

every requested capability is assessed;

readiness state and check results are consistent;

assessment times are ordered correctly;

Evidence identifiers are unique.

An Activation Receipt conforms when:

it validates against its JSON Schema;

its local Request and Assessment resolve;

the Assessment belongs to the Request;

its outcome matches the readiness state;

requested roles and capabilities are granted for activated outcomes;

activation windows and decision times are valid;

emergency controls are present;

Evidence identifiers are unique.

A Suspension Receipt conforms when:

it validates against its JSON Schema;

its local Activation Receipt resolves;

the referenced Cell was activated;

partial targets are explicit;

local role and capability targets were actually granted;

status-dependent timestamps and decisions are present;

dispute-related requirements are satisfied;

Evidence identifiers are unique.

