# Operational Roles and Handoffs

Version: 0.2.0

## 1. Purpose

Version 0.2 assigns bounded operating duties to activated Royalty Cells and
records the safe transfer of those duties.

```text
Activation Receipt
    ↓
Operational Role Assignment
    ↓
Authority Scope Binding
    ↓
Duty Rotation
    ↓
Cell Handoff

2. Required separation

Activation authority
is not a live duty assignment.

A Role Assignment
is not unlimited authority.

An Authority Binding
cannot expand the Activation Receipt.

A Handoff
is not a new grant of authority.

A Duty Rotation
changes who is on duty, not what the role may do.

3. Operational Role Assignment

An Assignment selects one role from an activated Cell and places it into aprimary, fallback, temporary, relief, or emergency duty mode. Assignedcapabilities MUST be a subset of the Activation Receipt role capabilities.The authority-scope reference MUST match the activated role.

Every Assignment declares:

assignment_effect: operational_role_assignment_only

4. Authority Scope Binding

A Binding limits an Assignment by capability, resource, record, route, value,time, delegation, and explicit constraints. It MUST NOT introduce a capabilitythat was absent from the Assignment.

Every Binding declares:

binding_effect: authority_scope_binding_only

5. Cell Handoff

A Handoff transfers bounded responsibility and state between two distinct,compatible Assignments. Completed Handoffs require source, target, andcoordinator acceptance. Every mandatory pending item must be accepted.Emergency takeovers require an incident reference and emergency Authorization.

Every Handoff declares:

handoff_effect: handoff_record_only

6. Duty Rotation

A Duty Rotation orders compatible Assignments into time-bounded shifts. Allparticipants MUST belong to the same federation and role type. An activerotation has exactly one current Assignment.

Every Rotation declares:

rotation_effect: duty_rotation_record_only

7. Conformance

A v0.2 record conforms when it validates against its JSON Schema, all locallyresolved references exist, authority never expands upstream grants, lifecycleand time requirements are satisfied, and pass/fail examples behave asexpected.
