#!/usr/bin/env python3
"""
Validate Royalty Cell Federation Operations Protocol examples.

Supported v0.1-v0.5 records:

- Federation Cell Activation Request
- Federation Cell Readiness Assessment
- Federation Cell Activation Receipt
- Federation Cell Suspension Receipt
- Federation Operational Role Assignment
- Federation Authority Scope Binding
- Federation Cell Handoff Record
- Federation Duty Rotation Record
- Federation Formation Record
- Federation Cell Route Decision Receipt
- Federation Value Flow Route
- Federation Formation Change Record
- Federation Operational Incident Record
- Federation Cell Isolation Order
- Federation Route Suspension Receipt
- Federation Cell Recovery Assessment
- Federation Cell Reactivation Receipt
- Federation Reconfiguration Plan
- Federation Cell Replacement Record
- Federation Capacity Rebalancing Receipt
- Federation Drill Record
- Federation Operational Conformance Report

Validation stages:

1. YAML loading
2. Record-type-specific JSON Schema validation
3. Record-type-specific semantic validation
4. Local cross-record reference validation
5. Lifecycle, role, capability, formation, routing, and time-order validation

Files under examples/pass must pass every validation stage.
Files under examples/fail must fail at least one validation stage.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT_DIR = Path(__file__).resolve().parents[1]
PASS_DIR = ROOT_DIR / "examples" / "pass"
FAIL_DIR = ROOT_DIR / "examples" / "fail"

SCHEMA_PATHS = {
    "federation_cell_activation_request": (
        ROOT_DIR / "schemas" / "cell-activation-request.schema.json"
    ),
    "federation_cell_readiness_assessment": (
        ROOT_DIR / "schemas" / "cell-readiness-assessment.schema.json"
    ),
    "federation_cell_activation_receipt": (
        ROOT_DIR / "schemas" / "cell-activation-receipt.schema.json"
    ),
    "federation_cell_suspension_receipt": (
        ROOT_DIR / "schemas" / "cell-suspension-receipt.schema.json"
    ),
    "federation_operational_role_assignment": (
        ROOT_DIR / "schemas" / "operational-role-assignment.schema.json"
    ),
    "federation_authority_scope_binding": (
        ROOT_DIR / "schemas" / "authority-scope-binding.schema.json"
    ),
    "federation_cell_handoff_record": (
        ROOT_DIR / "schemas" / "cell-handoff-record.schema.json"
    ),
    "federation_duty_rotation_record": (
        ROOT_DIR / "schemas" / "duty-rotation-record.schema.json"
    ),
    "federation_formation_record": (
        ROOT_DIR / "schemas" / "federation-formation-record.schema.json"
    ),
    "federation_cell_route_decision_receipt": (
        ROOT_DIR / "schemas" / "cell-route-decision-receipt.schema.json"
    ),
    "federation_value_flow_route": (
        ROOT_DIR / "schemas" / "value-flow-route.schema.json"
    ),
    "federation_formation_change_record": (
        ROOT_DIR / "schemas" / "formation-change-record.schema.json"
    ),
    "federation_operational_incident_record": (
        ROOT_DIR / "schemas" / "operational-incident-record.schema.json"
    ),
    "federation_cell_isolation_order": (
        ROOT_DIR / "schemas" / "cell-isolation-order.schema.json"
    ),
    "federation_route_suspension_receipt": (
        ROOT_DIR / "schemas" / "route-suspension-receipt.schema.json"
    ),
    "federation_cell_recovery_assessment": (
        ROOT_DIR / "schemas" / "cell-recovery-assessment.schema.json"
    ),
    "federation_cell_reactivation_receipt": (
        ROOT_DIR / "schemas" / "cell-reactivation-receipt.schema.json"
    ),
    "federation_reconfiguration_plan": (
        ROOT_DIR / "schemas" / "federation-reconfiguration-plan.schema.json"
    ),
    "federation_cell_replacement_record": (
        ROOT_DIR / "schemas" / "cell-replacement-record.schema.json"
    ),
    "federation_capacity_rebalancing_receipt": (
        ROOT_DIR / "schemas" / "capacity-rebalancing-receipt.schema.json"
    ),
    "federation_drill_record": (
        ROOT_DIR / "schemas" / "federation-drill-record.schema.json"
    ),
    "federation_operational_conformance_report": (
        ROOT_DIR / "schemas" / "operational-conformance-report.schema.json"
    ),
}

ID_FIELDS = {
    "federation_cell_activation_request": "request_id",
    "federation_cell_readiness_assessment": "assessment_id",
    "federation_cell_activation_receipt": "receipt_id",
    "federation_cell_suspension_receipt": "suspension_id",
    "federation_operational_role_assignment": "assignment_id",
    "federation_authority_scope_binding": "binding_id",
    "federation_cell_handoff_record": "handoff_id",
    "federation_duty_rotation_record": "rotation_id",
    "federation_formation_record": "formation_id",
    "federation_cell_route_decision_receipt": "route_decision_id",
    "federation_value_flow_route": "route_id",
    "federation_formation_change_record": "change_id",
    "federation_operational_incident_record": "incident_id",
    "federation_cell_isolation_order": "isolation_id",
    "federation_route_suspension_receipt": "route_suspension_id",
    "federation_cell_recovery_assessment": "recovery_assessment_id",
    "federation_cell_reactivation_receipt": "reactivation_id",
    "federation_reconfiguration_plan": "plan_id",
    "federation_cell_replacement_record": "replacement_id",
    "federation_capacity_rebalancing_receipt": "rebalance_id",
    "federation_drill_record": "drill_id",
    "federation_operational_conformance_report": "report_id",
}


KnownRecords = dict[str, dict[str, dict[str, Any]]]


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a JSON object")

    return data


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root value must be a YAML mapping")

    return data


def collect_yaml_files(directory: Path) -> list[Path]:
    """Collect YAML files in stable order."""
    files = list(directory.glob("*.yaml"))
    files.extend(directory.glob("*.yml"))
    return sorted(set(files))


def format_error_path(parts: list[Any]) -> str:
    """Convert a jsonschema path into readable dotted notation."""
    if not parts:
        return "<root>"

    result = ""

    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            if result:
                result += "."
            result += str(part)

    return result


def parse_datetime(value: Any) -> datetime | None:
    """Parse ISO-8601 timestamps, including a trailing Z."""
    if not isinstance(value, str):
        return None

    normalized = value

    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def to_decimal(value: Any) -> Decimal | None:
    """Convert numeric values to Decimal without float arithmetic."""
    if isinstance(value, bool):
        return None
    if not isinstance(value, (int, float, str, Decimal)):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def decimal_equal(left: Decimal, right: Decimal, tolerance: Decimal) -> bool:
    """Compare Decimal values with a declared tolerance."""
    return abs(left - right) <= tolerance


def duplicate_values(values: list[str]) -> list[str]:
    """Return duplicated values in stable order."""
    return sorted(
        {
            value
            for value in values
            if values.count(value) > 1
        }
    )


def load_validators() -> dict[str, Draft202012Validator]:
    """Load and compile every JSON Schema."""
    validators: dict[str, Draft202012Validator] = {}

    for record_type, schema_path in SCHEMA_PATHS.items():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        validators[record_type] = Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        )

    return validators


def schema_errors(
    document: dict[str, Any],
    validators: dict[str, Draft202012Validator],
) -> list[str]:
    """Return JSON Schema errors for one document."""
    record_type = document.get("record_type")

    if not isinstance(record_type, str):
        return ["record_type: missing or not a string"]

    validator = validators.get(record_type)

    if validator is None:
        return [f"record_type: unsupported record type '{record_type}'"]

    errors: list[str] = []

    sorted_errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.absolute_path),
    )

    for error in sorted_errors:
        path = format_error_path(list(error.absolute_path))
        errors.append(f"{path}: {error.message}")

    return errors


def collect_known_records(
    pass_files: list[Path],
    validators: dict[str, Draft202012Validator],
) -> KnownRecords:
    """Collect schema-valid passing records by type and identifier."""
    known: KnownRecords = {
        record_type: {}
        for record_type in ID_FIELDS
    }

    for path in pass_files:
        try:
            document = load_yaml(path)
        except (OSError, ValueError, yaml.YAMLError):
            continue

        record_type = document.get("record_type")

        if record_type not in ID_FIELDS:
            continue

        if schema_errors(document, validators):
            continue

        id_field = ID_FIELDS[record_type]
        record_id = document.get(id_field)

        if isinstance(record_id, str):
            known[record_type][record_id] = document

    return known


def evidence_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Validate Evidence identifier uniqueness."""
    errors: list[str] = []
    evidence = document.get("evidence", [])

    if not isinstance(evidence, list):
        return errors

    evidence_ids: list[str] = []

    for item in evidence:
        if not isinstance(item, dict):
            continue

        evidence_id = item.get("evidence_id")

        if isinstance(evidence_id, str):
            evidence_ids.append(evidence_id)

    for evidence_id in duplicate_values(evidence_ids):
        errors.append(
            f"evidence: duplicate evidence_id '{evidence_id}'"
        )

    return errors


def external_reference_errors(
    value: Any,
    path: str,
) -> list[str]:
    """Require record_ref for externally resolved references."""
    if not isinstance(value, dict):
        return []

    if (
        value.get("resolution_status") == "externally_resolved"
        and not value.get("record_ref")
    ):
        return [
            f"{path}.record_ref: required when resolution_status "
            "is 'externally_resolved'"
        ]

    return []


def activation_request_semantic_errors(
    document: dict[str, Any],
) -> list[str]:
    """Validate Cell Activation Request semantics."""
    errors: list[str] = []

    requested_capabilities = document.get("requested_capabilities", [])
    capability_set = {
        capability
        for capability in requested_capabilities
        if isinstance(capability, str)
    } if isinstance(requested_capabilities, list) else set()

    requested_roles = document.get("requested_roles", [])
    role_ids: list[str] = []

    if isinstance(requested_roles, list):
        for index, role in enumerate(requested_roles):
            if not isinstance(role, dict):
                continue

            role_id = role.get("role_id")

            if isinstance(role_id, str):
                role_ids.append(role_id)

            required_capabilities = role.get(
                "required_capabilities",
                [],
            )

            if isinstance(required_capabilities, list):
                for capability in required_capabilities:
                    if (
                        isinstance(capability, str)
                        and capability not in capability_set
                    ):
                        errors.append(
                            f"requested_roles[{index}]."
                            "required_capabilities: capability "
                            f"'{capability}' is not declared in "
                            "requested_capabilities"
                        )

    for role_id in duplicate_values(role_ids):
        errors.append(
            f"requested_roles: duplicate role_id '{role_id}'"
        )

    activation_mode = document.get("activation_mode")
    operation_context = document.get("operation_context")

    if activation_mode == "temporary":
        if not isinstance(operation_context, dict):
            errors.append(
                "operation_context: required for temporary activation"
            )
        elif not operation_context.get("requested_end_at"):
            errors.append(
                "operation_context.requested_end_at: required for "
                "temporary activation"
            )

    if (
        activation_mode == "emergency"
        and not document.get("emergency_justification")
    ):
        errors.append(
            "emergency_justification: required for emergency activation"
        )

    if isinstance(operation_context, dict):
        start_at = parse_datetime(
            operation_context.get("requested_start_at")
        )
        end_at = parse_datetime(
            operation_context.get("requested_end_at")
        )

        if start_at is not None and end_at is not None:
            if end_at < start_at:
                errors.append(
                    "operation_context.requested_end_at: must be equal "
                    "to or later than requested_start_at"
                )

    request_status = document.get("request_status")

    if (
        request_status == "withdrawn"
        and not document.get("status_reason")
    ):
        errors.append(
            "status_reason: required when request_status is 'withdrawn'"
        )

    if (
        request_status == "superseded"
        and not document.get("superseded_by_ref")
    ):
        errors.append(
            "superseded_by_ref: required when request_status is "
            "'superseded'"
        )

    errors.extend(evidence_semantic_errors(document))
    return errors


def readiness_assessment_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Readiness Assessment semantics."""
    errors: list[str] = []

    request_ref = document.get("request", {})
    errors.extend(external_reference_errors(request_ref, "request"))

    request_document: dict[str, Any] | None = None

    if isinstance(request_ref, dict):
        request_id = request_ref.get("request_id")

        if (
            request_ref.get("resolution_status") == "resolved"
            and request_ref.get("source_cell_id")
            == document.get("cell_id")
        ):
            request_document = known[
                "federation_cell_activation_request"
            ].get(request_id)

            if request_document is None:
                errors.append(
                    "request.request_id: locally resolved Activation "
                    f"Request '{request_id}' was not found"
                )

    if request_document is not None:
        if request_document.get("cell_id") != document.get("cell_id"):
            errors.append(
                "cell_id: does not match the referenced Activation Request"
            )

        if (
            request_document.get("federation_id")
            != document.get("federation_id")
        ):
            errors.append(
                "federation_id: does not match the referenced "
                "Activation Request"
            )

        requested_at = parse_datetime(
            request_document.get("requested_at")
        )
        assessed_at = parse_datetime(document.get("assessed_at"))

        if (
            requested_at is not None
            and assessed_at is not None
            and assessed_at < requested_at
        ):
            errors.append(
                "assessed_at: must not be earlier than the request time"
            )

    assessed_at = parse_datetime(document.get("assessed_at"))
    valid_until = parse_datetime(document.get("valid_until"))

    if (
        assessed_at is not None
        and valid_until is not None
        and valid_until < assessed_at
    ):
        errors.append(
            "valid_until: must be equal to or later than assessed_at"
        )

    checks = document.get("checks", [])
    check_ids: list[str] = []
    required_statuses: list[str] = []
    capability_checks: dict[str, list[str]] = {}

    if isinstance(checks, list):
        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                continue

            check_id = check.get("check_id")

            if isinstance(check_id, str):
                check_ids.append(check_id)

            status = check.get("status")

            if check.get("required") is True and isinstance(status, str):
                required_statuses.append(status)

            if check.get("category") == "requested_capability":
                capability = check.get("capability")

                if not isinstance(capability, str):
                    errors.append(
                        f"checks[{index}].capability: required for "
                        "requested_capability checks"
                    )
                else:
                    capability_checks.setdefault(capability, []).append(
                        status if isinstance(status, str) else "unknown"
                    )

    for check_id in duplicate_values(check_ids):
        errors.append(
            f"checks: duplicate check_id '{check_id}'"
        )

    for capability, statuses in capability_checks.items():
        if len(statuses) > 1:
            errors.append(
                "checks: duplicate requested_capability assessment for "
                f"'{capability}'"
            )

    readiness_status = document.get("readiness_status")
    blockers = document.get("blockers", [])
    conditions = document.get("conditions", [])

    if request_document is not None:
        requested_capabilities = request_document.get(
            "requested_capabilities",
            [],
        )

        if isinstance(requested_capabilities, list):
            for capability in requested_capabilities:
                if not isinstance(capability, str):
                    continue

                statuses = capability_checks.get(capability)

                if not statuses:
                    errors.append(
                        "checks: missing requested_capability check for "
                        f"'{capability}'"
                    )
                    continue

                status = statuses[0]

                if readiness_status == "ready" and status != "pass":
                    errors.append(
                        "checks: readiness_status 'ready' requires "
                        f"capability '{capability}' to pass"
                    )

                if (
                    readiness_status == "ready_with_conditions"
                    and status not in {"pass", "warn"}
                ):
                    errors.append(
                        "checks: conditionally ready assessment requires "
                        f"capability '{capability}' to pass or warn"
                    )

    if readiness_status == "ready":
        invalid_required = [
            status
            for status in required_statuses
            if status not in {"pass", "not_applicable"}
        ]

        if invalid_required:
            errors.append(
                "checks: readiness_status 'ready' cannot contain "
                "required warn or fail checks"
            )

        if blockers:
            errors.append(
                "blockers: must be empty when readiness_status is 'ready'"
            )

        if conditions:
            errors.append(
                "conditions: must be empty when readiness_status is 'ready'"
            )

    if readiness_status == "ready_with_conditions":
        if "fail" in required_statuses:
            errors.append(
                "checks: conditionally ready assessment cannot contain "
                "a required failed check"
            )

        if "warn" not in required_statuses:
            errors.append(
                "checks: readiness_status 'ready_with_conditions' "
                "requires at least one required warning"
            )

        if not conditions:
            errors.append(
                "conditions: required when readiness_status is "
                "'ready_with_conditions'"
            )

    if readiness_status == "not_ready":
        if "fail" not in required_statuses:
            errors.append(
                "checks: readiness_status 'not_ready' requires at least "
                "one required failed check"
            )

        if not blockers:
            errors.append(
                "blockers: required when readiness_status is 'not_ready'"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors


def activation_receipt_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Activation Receipt semantics."""
    errors: list[str] = []

    request_ref = document.get("request", {})
    assessment_ref = document.get("assessment", {})

    errors.extend(external_reference_errors(request_ref, "request"))
    errors.extend(external_reference_errors(assessment_ref, "assessment"))

    request_document: dict[str, Any] | None = None
    assessment_document: dict[str, Any] | None = None

    if isinstance(request_ref, dict):
        request_id = request_ref.get("request_id")

        if (
            request_ref.get("resolution_status") == "resolved"
            and request_ref.get("source_cell_id")
            == document.get("cell_id")
        ):
            request_document = known[
                "federation_cell_activation_request"
            ].get(request_id)

            if request_document is None:
                errors.append(
                    "request.request_id: locally resolved Activation "
                    f"Request '{request_id}' was not found"
                )

    if isinstance(assessment_ref, dict):
        assessment_id = assessment_ref.get("assessment_id")

        if (
            assessment_ref.get("resolution_status") == "resolved"
            and assessment_ref.get("source_cell_id")
            == document.get("cell_id")
        ):
            assessment_document = known[
                "federation_cell_readiness_assessment"
            ].get(assessment_id)

            if assessment_document is None:
                errors.append(
                    "assessment.assessment_id: locally resolved "
                    f"Readiness Assessment '{assessment_id}' was not found"
                )

    for label, linked_document in [
        ("Activation Request", request_document),
        ("Readiness Assessment", assessment_document),
    ]:
        if linked_document is None:
            continue

        if linked_document.get("cell_id") != document.get("cell_id"):
            errors.append(
                f"cell_id: does not match the referenced {label}"
            )

        if (
            linked_document.get("federation_id")
            != document.get("federation_id")
        ):
            errors.append(
                f"federation_id: does not match the referenced {label}"
            )

    if (
        assessment_document is not None
        and request_document is not None
    ):
        linked_assessment_request = assessment_document.get("request", {})

        if isinstance(linked_assessment_request, dict):
            if (
                linked_assessment_request.get("request_id")
                != request_document.get("request_id")
            ):
                errors.append(
                    "assessment: does not assess the referenced "
                    "Activation Request"
                )

    issued_at = parse_datetime(document.get("issued_at"))
    decision = document.get("decision", {})

    if isinstance(decision, dict):
        decided_at = parse_datetime(decision.get("decided_at"))

        if (
            decided_at is not None
            and issued_at is not None
            and issued_at < decided_at
        ):
            errors.append(
                "issued_at: must be equal to or later than "
                "decision.decided_at"
            )

    if assessment_document is not None and issued_at is not None:
        assessed_at = parse_datetime(
            assessment_document.get("assessed_at")
        )
        valid_until = parse_datetime(
            assessment_document.get("valid_until")
        )

        if assessed_at is not None and issued_at < assessed_at:
            errors.append(
                "issued_at: must not be earlier than assessed_at"
            )

        if valid_until is not None and issued_at > valid_until:
            errors.append(
                "assessment: readiness assessment expired before "
                "the Activation Receipt was issued"
            )

    activation_window = document.get("activation_window")

    if isinstance(activation_window, dict):
        start_at = parse_datetime(activation_window.get("start_at"))
        end_at = parse_datetime(activation_window.get("end_at"))

        if start_at is not None and end_at is not None:
            if end_at < start_at:
                errors.append(
                    "activation_window.end_at: must be equal to or later "
                    "than start_at"
                )

    operational_roles = document.get("operational_roles", [])
    granted_capabilities = document.get("granted_capabilities", [])

    global_capabilities = {
        capability
        for capability in granted_capabilities
        if isinstance(capability, str)
    } if isinstance(granted_capabilities, list) else set()

    assigned_role_ids: list[str] = []
    assigned_role_types: dict[str, str] = {}

    if isinstance(operational_roles, list):
        for index, role in enumerate(operational_roles):
            if not isinstance(role, dict):
                continue

            role_id = role.get("role_id")
            role_type = role.get("role_type")

            if isinstance(role_id, str):
                assigned_role_ids.append(role_id)

                if isinstance(role_type, str):
                    assigned_role_types[role_id] = role_type

            role_capabilities = role.get("granted_capabilities", [])

            if isinstance(role_capabilities, list):
                for capability in role_capabilities:
                    if (
                        isinstance(capability, str)
                        and capability not in global_capabilities
                    ):
                        errors.append(
                            f"operational_roles[{index}]."
                            "granted_capabilities: capability "
                            f"'{capability}' is not declared in "
                            "granted_capabilities"
                        )

    for role_id in duplicate_values(assigned_role_ids):
        errors.append(
            f"operational_roles: duplicate role_id '{role_id}'"
        )

    outcome = document.get("activation_outcome")
    conditions = document.get("conditions", [])

    if outcome in {"activated", "activated_with_conditions"}:
        if not operational_roles:
            errors.append(
                "operational_roles: required for an activated Cell"
            )

        if not granted_capabilities:
            errors.append(
                "granted_capabilities: required for an activated Cell"
            )

        if not isinstance(activation_window, dict):
            errors.append(
                "activation_window: required for an activated Cell"
            )

        if not isinstance(document.get("emergency_controls"), dict):
            errors.append(
                "emergency_controls: required for an activated Cell"
            )

        if request_document is not None:
            request_status = request_document.get("request_status")

            if request_status in {"withdrawn", "superseded"}:
                errors.append(
                    "request: withdrawn or superseded Activation Request "
                    "cannot produce an activated outcome"
                )

            requested_roles = request_document.get(
                "requested_roles",
                [],
            )

            if isinstance(requested_roles, list):
                for requested_role in requested_roles:
                    if not isinstance(requested_role, dict):
                        continue

                    requested_role_id = requested_role.get("role_id")
                    requested_role_type = requested_role.get("role_type")

                    if requested_role_id not in assigned_role_types:
                        errors.append(
                            "operational_roles: requested role "
                            f"'{requested_role_id}' was not assigned"
                        )
                    elif (
                        assigned_role_types.get(requested_role_id)
                        != requested_role_type
                    ):
                        errors.append(
                            "operational_roles: assigned role type for "
                            f"'{requested_role_id}' does not match the "
                            "Activation Request"
                        )

            requested_capabilities = request_document.get(
                "requested_capabilities",
                [],
            )

            if isinstance(requested_capabilities, list):
                for capability in requested_capabilities:
                    if (
                        isinstance(capability, str)
                        and capability not in global_capabilities
                    ):
                        errors.append(
                            "granted_capabilities: requested capability "
                            f"'{capability}' was not granted"
                        )

    if outcome == "activated":
        if (
            assessment_document is not None
            and assessment_document.get("readiness_status") != "ready"
        ):
            errors.append(
                "activation_outcome: 'activated' requires a 'ready' "
                "Readiness Assessment"
            )

        if conditions:
            errors.append(
                "conditions: must be empty when activation_outcome is "
                "'activated'"
            )

    if outcome == "activated_with_conditions":
        if (
            assessment_document is not None
            and assessment_document.get("readiness_status")
            != "ready_with_conditions"
        ):
            errors.append(
                "activation_outcome: 'activated_with_conditions' "
                "requires a conditionally ready assessment"
            )

        if not conditions:
            errors.append(
                "conditions: required for activated_with_conditions"
            )

        if assessment_document is not None:
            assessment_conditions = assessment_document.get(
                "conditions",
                [],
            )

            if isinstance(assessment_conditions, list):
                missing_conditions = sorted(
                    {
                        condition
                        for condition in assessment_conditions
                        if isinstance(condition, str)
                    }
                    - {
                        condition
                        for condition in conditions
                        if isinstance(condition, str)
                    }
                )

                for condition in missing_conditions:
                    errors.append(
                        "conditions: assessment condition was not carried "
                        f"into the Activation Receipt: '{condition}'"
                    )

    if outcome == "denied":
        if operational_roles:
            errors.append(
                "operational_roles: must be empty for a denied activation"
            )

        if granted_capabilities:
            errors.append(
                "granted_capabilities: must be empty for a denied activation"
            )

        if activation_window is not None:
            errors.append(
                "activation_window: must be omitted for a denied activation"
            )

        if document.get("emergency_controls") is not None:
            errors.append(
                "emergency_controls: must be omitted for a denied activation"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors


def suspension_receipt_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Suspension Receipt semantics."""
    errors: list[str] = []

    activation_ref = document.get("activation_receipt", {})
    errors.extend(
        external_reference_errors(
            activation_ref,
            "activation_receipt",
        )
    )

    activation_document: dict[str, Any] | None = None

    if isinstance(activation_ref, dict):
        receipt_id = activation_ref.get("receipt_id")

        if (
            activation_ref.get("resolution_status") == "resolved"
            and activation_ref.get("source_cell_id")
            == document.get("cell_id")
        ):
            activation_document = known[
                "federation_cell_activation_receipt"
            ].get(receipt_id)

            if activation_document is None:
                errors.append(
                    "activation_receipt.receipt_id: locally resolved "
                    f"Activation Receipt '{receipt_id}' was not found"
                )

    if activation_document is not None:
        if activation_document.get("cell_id") != document.get("cell_id"):
            errors.append(
                "cell_id: does not match the Activation Receipt"
            )

        if (
            activation_document.get("federation_id")
            != document.get("federation_id")
        ):
            errors.append(
                "federation_id: does not match the Activation Receipt"
            )

        if activation_document.get("activation_outcome") not in {
            "activated",
            "activated_with_conditions",
        }:
            errors.append(
                "activation_receipt: only an activated Cell may be suspended"
            )

    scope = document.get("suspension_scope", {})

    if isinstance(scope, dict):
        role_ids = scope.get("role_ids", [])
        capabilities = scope.get("capabilities", [])
        route_refs = scope.get("route_refs", [])
        mode = scope.get("mode")

        has_target = any(
            isinstance(value, list) and bool(value)
            for value in [role_ids, capabilities, route_refs]
        )

        if mode == "partial" and not has_target:
            errors.append(
                "suspension_scope: partial suspension requires at least "
                "one role, capability, or route target"
            )

        if mode == "full" and has_target:
            errors.append(
                "suspension_scope: full suspension must not enumerate "
                "partial targets"
            )

        if activation_document is not None:
            assigned_roles = activation_document.get(
                "operational_roles",
                [],
            )
            assigned_role_ids = {
                role.get("role_id")
                for role in assigned_roles
                if isinstance(role, dict)
                and isinstance(role.get("role_id"), str)
            } if isinstance(assigned_roles, list) else set()

            granted_capabilities = {
                capability
                for capability in activation_document.get(
                    "granted_capabilities",
                    [],
                )
                if isinstance(capability, str)
            }

            if isinstance(role_ids, list):
                for role_id in role_ids:
                    if (
                        isinstance(role_id, str)
                        and role_id not in assigned_role_ids
                    ):
                        errors.append(
                            "suspension_scope.role_ids: role "
                            f"'{role_id}' was not assigned by the "
                            "Activation Receipt"
                        )

            if isinstance(capabilities, list):
                for capability in capabilities:
                    if (
                        isinstance(capability, str)
                        and capability not in granted_capabilities
                    ):
                        errors.append(
                            "suspension_scope.capabilities: capability "
                            f"'{capability}' was not granted by the "
                            "Activation Receipt"
                        )

    if (
        document.get("reason_code") == "dispute"
        and not document.get("dispute_refs")
    ):
        errors.append(
            "dispute_refs: required when reason_code is 'dispute'"
        )

    issued_at = parse_datetime(document.get("issued_at"))
    decision = document.get("decision", {})

    if isinstance(decision, dict):
        decided_at = parse_datetime(decision.get("decided_at"))

        if (
            decided_at is not None
            and issued_at is not None
            and issued_at < decided_at
        ):
            errors.append(
                "issued_at: must be equal to or later than "
                "decision.decided_at"
            )

    effective_at = parse_datetime(document.get("effective_at"))
    status = document.get("suspension_status")

    if status == "active":
        if effective_at is None:
            errors.append(
                "effective_at: required for an active suspension"
            )

        if document.get("lifted_at") is not None:
            errors.append(
                "lifted_at: must be omitted for an active suspension"
            )

        if document.get("lift_decision") is not None:
            errors.append(
                "lift_decision: must be omitted for an active suspension"
            )

        if document.get("cancelled_at") is not None:
            errors.append(
                "cancelled_at: must be omitted for an active suspension"
            )

    if status == "lifted":
        lifted_at = parse_datetime(document.get("lifted_at"))
        lift_decision = document.get("lift_decision")

        if effective_at is None:
            errors.append(
                "effective_at: required for a lifted suspension"
            )

        if lifted_at is None:
            errors.append(
                "lifted_at: required when suspension_status is 'lifted'"
            )

        if not isinstance(lift_decision, dict):
            errors.append(
                "lift_decision: required when suspension_status is 'lifted'"
            )

        if (
            effective_at is not None
            and lifted_at is not None
            and lifted_at < effective_at
        ):
            errors.append(
                "lifted_at: must be equal to or later than effective_at"
            )

        if isinstance(lift_decision, dict) and lifted_at is not None:
            lift_decided_at = parse_datetime(
                lift_decision.get("decided_at")
            )

            if (
                lift_decided_at is not None
                and lift_decided_at > lifted_at
            ):
                errors.append(
                    "lift_decision.decided_at: must not be later than "
                    "lifted_at"
                )

    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append(
                "cancelled_at: required when suspension_status is "
                "'cancelled'"
            )

        if not document.get("cancellation_reason"):
            errors.append(
                "cancellation_reason: required when suspension_status is "
                "'cancelled'"
            )

    errors.extend(evidence_semantic_errors(document))
    return errors



def decision_time_errors(document: dict[str, Any]) -> list[str]:
    """Require the decision to precede record issuance."""
    decision = document.get("decision", {})
    issued_at = parse_datetime(document.get("issued_at"))

    if not isinstance(decision, dict):
        return []

    decided_at = parse_datetime(decision.get("decided_at"))

    if decided_at and issued_at and issued_at < decided_at:
        return ["issued_at: must not be earlier than decision.decided_at"]

    return []


def resolved_record(
    reference: Any,
    id_field: str,
    internal_type: str,
    known: KnownRecords,
    path: str,
    errors: list[str],
) -> dict[str, Any] | None:
    """Resolve a local reference or validate an external reference."""
    errors.extend(external_reference_errors(reference, path))

    if not isinstance(reference, dict):
        return None

    if reference.get("resolution_status") != "resolved":
        return None

    record_id = reference.get(id_field)
    record = known[internal_type].get(record_id)

    if record is None:
        errors.append(
            f"{path}.{id_field}: locally resolved record "
            f"'{record_id}' was not found"
        )

    return record


def operational_role_assignment_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Operational Role Assignment semantics."""
    errors: list[str] = []
    activation_ref = document.get("activation_receipt", {})
    activation = resolved_record(
        activation_ref,
        "receipt_id",
        "federation_cell_activation_receipt",
        known,
        "activation_receipt",
        errors,
    )

    if activation is not None:
        if activation.get("activation_outcome") not in {
            "activated",
            "activated_with_conditions",
        }:
            errors.append(
                "activation_receipt: role assignment requires an activated Cell"
            )

        if activation.get("federation_id") != document.get("federation_id"):
            errors.append(
                "federation_id: does not match the Activation Receipt"
            )

        if activation.get("cell_id") != document.get("cell_id"):
            errors.append("cell_id: does not match the Activation Receipt")

        role_id = document.get("role_id")
        matching_role = None

        for role in activation.get("operational_roles", []):
            if isinstance(role, dict) and role.get("role_id") == role_id:
                matching_role = role
                break

        if matching_role is None:
            errors.append(
                f"role_id: activated role '{role_id}' was not found"
            )
        else:
            if matching_role.get("role_type") != document.get("role_type"):
                errors.append(
                    "role_type: does not match the activated operational role"
                )

            if (
                matching_role.get("authority_scope_ref")
                != document.get("authority_scope_ref")
            ):
                errors.append(
                    "authority_scope_ref: does not match the activated role"
                )

            role_caps = {
                item
                for item in matching_role.get("granted_capabilities", [])
                if isinstance(item, str)
            }
            assigned_caps = {
                item
                for item in document.get("assigned_capabilities", [])
                if isinstance(item, str)
            }

            for capability in sorted(assigned_caps - role_caps):
                errors.append(
                    "assigned_capabilities: capability "
                    f"'{capability}' was not granted to the activated role"
                )

        global_caps = {
            item
            for item in activation.get("granted_capabilities", [])
            if isinstance(item, str)
        }
        assigned_caps = {
            item
            for item in document.get("assigned_capabilities", [])
            if isinstance(item, str)
        }

        for capability in sorted(assigned_caps - global_caps):
            errors.append(
                "assigned_capabilities: capability "
                f"'{capability}' was not granted by the Activation Receipt"
            )

    duty_window = document.get("duty_window", {})
    duty_start = duty_end = None

    if isinstance(duty_window, dict):
        duty_start = parse_datetime(duty_window.get("start_at"))
        duty_end = parse_datetime(duty_window.get("end_at"))

        if duty_start and duty_end and duty_end < duty_start:
            errors.append(
                "duty_window.end_at: must not be earlier than start_at"
            )

    if activation is not None:
        activation_window = activation.get("activation_window", {})

        if isinstance(activation_window, dict):
            activation_start = parse_datetime(
                activation_window.get("start_at")
            )
            activation_end = parse_datetime(activation_window.get("end_at"))

            if duty_start and activation_start and duty_start < activation_start:
                errors.append(
                    "duty_window.start_at: must not precede activation start"
                )

            if duty_end and activation_end and duty_end > activation_end:
                errors.append(
                    "duty_window.end_at: must not exceed activation end"
                )

    status = document.get("assignment_status")
    mode = document.get("assignment_mode")
    effective_at = parse_datetime(document.get("effective_at"))

    if status == "active":
        if effective_at is None:
            errors.append("effective_at: required for active assignment")
        elif duty_start and effective_at < duty_start:
            errors.append("effective_at: must not precede duty_window.start_at")

    if mode in {"temporary", "relief"} and duty_end is None:
        errors.append(
            "duty_window.end_at: required for temporary or relief assignment"
        )

    status_fields = {
        "suspended": "suspended_at",
        "completed": "completed_at",
        "revoked": "revoked_at",
    }

    required_field = status_fields.get(status)
    if required_field and not document.get(required_field):
        errors.append(f"{required_field}: required for {status} assignment")

    if status in {"suspended", "revoked"} and not document.get(
        "status_reason"
    ):
        errors.append(f"status_reason: required for {status} assignment")

    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def authority_scope_binding_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Authority Scope Binding semantics."""
    errors: list[str] = []
    assignment_ref = document.get("assignment", {})
    assignment = resolved_record(
        assignment_ref,
        "assignment_id",
        "federation_operational_role_assignment",
        known,
        "assignment",
        errors,
    )

    permitted = {
        item
        for item in document.get("permitted_capabilities", [])
        if isinstance(item, str)
    }
    prohibited = {
        item
        for item in document.get("prohibited_capabilities", [])
        if isinstance(item, str)
    }

    for capability in sorted(permitted & prohibited):
        errors.append(
            "prohibited_capabilities: capability "
            f"'{capability}' is also permitted"
        )

    if assignment is not None:
        if assignment.get("federation_id") != document.get("federation_id"):
            errors.append("federation_id: does not match the Role Assignment")

        if assignment.get("cell_id") != document.get("cell_id"):
            errors.append("cell_id: does not match the Role Assignment")

        if assignment.get("role_id") != document.get("role_id"):
            errors.append("role_id: does not match the Role Assignment")

        assigned = {
            item
            for item in assignment.get("assigned_capabilities", [])
            if isinstance(item, str)
        }

        for capability in sorted(permitted - assigned):
            errors.append(
                "permitted_capabilities: capability "
                f"'{capability}' was not assigned upstream"
            )

        status = document.get("binding_status")
        assignment_status = assignment.get("assignment_status")

        if status == "active" and assignment_status != "active":
            errors.append(
                "binding_status: active binding requires active assignment"
            )

        if status == "prepared" and assignment_status not in {
            "pending",
            "standby",
            "active",
        }:
            errors.append(
                "binding_status: prepared binding requires pending, standby, "
                "or active assignment"
            )

        binding_window = document.get("time_window", {})
        assignment_window = assignment.get("duty_window", {})

        if isinstance(binding_window, dict) and isinstance(
            assignment_window,
            dict,
        ):
            binding_start = parse_datetime(binding_window.get("start_at"))
            binding_end = parse_datetime(binding_window.get("end_at"))
            assignment_start = parse_datetime(
                assignment_window.get("start_at")
            )
            assignment_end = parse_datetime(assignment_window.get("end_at"))

            if binding_start and assignment_start and binding_start < assignment_start:
                errors.append(
                    "time_window.start_at: must not precede assignment duty"
                )

            if binding_end and assignment_end and binding_end > assignment_end:
                errors.append(
                    "time_window.end_at: must not exceed assignment duty"
                )

    resource_scope = document.get("resource_scope", {})
    if isinstance(resource_scope, dict):
        allowed = set(resource_scope.get("allowed_refs", []))
        denied = set(resource_scope.get("denied_refs", []))
        mode = resource_scope.get("mode")

        if mode == "listed_only" and not allowed:
            errors.append(
                "resource_scope.allowed_refs: required for listed_only mode"
            )

        if mode == "none" and allowed:
            errors.append(
                "resource_scope.allowed_refs: must be empty for none mode"
            )

        for ref in sorted(allowed & denied):
            errors.append(
                f"resource_scope: reference '{ref}' is both allowed and denied"
            )

    route_scope = document.get("route_scope", {})
    if isinstance(route_scope, dict):
        allowed_routes = set(route_scope.get("allowed_route_refs", []))
        denied_routes = set(route_scope.get("denied_route_refs", []))

        for ref in sorted(allowed_routes & denied_routes):
            errors.append(
                f"route_scope: route '{ref}' is both allowed and denied"
            )

    delegation = document.get("delegation_policy", {})
    if isinstance(delegation, dict):
        mode = delegation.get("mode")
        delegates = delegation.get("delegate_refs")
        policy_ref = delegation.get("policy_ref")

        if mode == "prohibited" and (delegates or policy_ref):
            errors.append(
                "delegation_policy: prohibited mode must not define delegates "
                "or policy_ref"
            )

        if mode == "explicit" and not delegates:
            errors.append(
                "delegation_policy.delegate_refs: required for explicit mode"
            )

        if mode == "policy_based" and not policy_ref:
            errors.append(
                "delegation_policy.policy_ref: required for policy_based mode"
            )

    value_limits = document.get("value_limits")
    if isinstance(value_limits, dict):
        per_event = value_limits.get("per_event_max")
        cumulative = value_limits.get("cumulative_max")

        if cumulative is not None and cumulative < per_event:
            errors.append(
                "value_limits.cumulative_max: must be equal to or greater "
                "than per_event_max"
            )

        if cumulative is not None and not value_limits.get("period"):
            errors.append(
                "value_limits.period: required when cumulative_max is set"
            )

    time_window = document.get("time_window", {})
    if isinstance(time_window, dict):
        start_at = parse_datetime(time_window.get("start_at"))
        end_at = parse_datetime(time_window.get("end_at"))

        if start_at and end_at and end_at < start_at:
            errors.append(
                "time_window.end_at: must not be earlier than start_at"
            )

    status = document.get("binding_status")
    if status == "active" and not document.get("effective_at"):
        errors.append("effective_at: required for active binding")

    for state, field in {
        "suspended": "suspended_at",
        "revoked": "revoked_at",
        "expired": "expired_at",
    }.items():
        if status == state and not document.get(field):
            errors.append(f"{field}: required for {state} binding")

    if status in {"suspended", "revoked"} and not document.get(
        "status_reason"
    ):
        errors.append(f"status_reason: required for {status} binding")

    constraint_ids = [
        item.get("constraint_id")
        for item in document.get("constraints", [])
        if isinstance(item, dict) and isinstance(item.get("constraint_id"), str)
    ]
    for constraint_id in duplicate_values(constraint_ids):
        errors.append(
            f"constraints: duplicate constraint_id '{constraint_id}'"
        )

    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def cell_handoff_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Handoff Record semantics."""
    errors: list[str] = []
    source_ref = document.get("source_assignment", {})
    target_ref = document.get("target_assignment", {})
    source = resolved_record(
        source_ref,
        "assignment_id",
        "federation_operational_role_assignment",
        known,
        "source_assignment",
        errors,
    )
    target = resolved_record(
        target_ref,
        "assignment_id",
        "federation_operational_role_assignment",
        known,
        "target_assignment",
        errors,
    )

    source_id = source_ref.get("assignment_id") if isinstance(source_ref, dict) else None
    target_id = target_ref.get("assignment_id") if isinstance(target_ref, dict) else None

    if source_id == target_id:
        errors.append(
            "target_assignment.assignment_id: must differ from source assignment"
        )

    for label, assignment in [("source", source), ("target", target)]:
        if assignment is None:
            continue

        if assignment.get("federation_id") != document.get("federation_id"):
            errors.append(
                f"{label}_assignment: federation_id does not match handoff"
            )

    if source is not None and target is not None:
        if source.get("role_type") != target.get("role_type"):
            errors.append(
                "target_assignment: role_type must match source assignment"
            )

    source_binding = resolved_record(
        document.get("source_authority_binding", {}),
        "binding_id",
        "federation_authority_scope_binding",
        known,
        "source_authority_binding",
        errors,
    )
    target_binding = resolved_record(
        document.get("target_authority_binding", {}),
        "binding_id",
        "federation_authority_scope_binding",
        known,
        "target_authority_binding",
        errors,
    )

    if source_binding is not None and source_id is not None:
        binding_assignment = source_binding.get("assignment", {})
        if isinstance(binding_assignment, dict) and binding_assignment.get(
            "assignment_id"
        ) != source_id:
            errors.append(
                "source_authority_binding: does not bind source assignment"
            )

    if target_binding is not None and target_id is not None:
        binding_assignment = target_binding.get("assignment", {})
        if isinstance(binding_assignment, dict) and binding_assignment.get(
            "assignment_id"
        ) != target_id:
            errors.append(
                "target_authority_binding: does not bind target assignment"
            )

    scope = document.get("handoff_scope", {})
    capabilities = set(scope.get("capabilities", [])) if isinstance(scope, dict) else set()

    for label, assignment in [("source", source), ("target", target)]:
        if assignment is None:
            continue
        assigned = set(assignment.get("assigned_capabilities", []))
        for capability in sorted(capabilities - assigned):
            errors.append(
                f"handoff_scope.capabilities: '{capability}' is not assigned "
                f"to the {label} assignment"
            )

    for label, binding in [("source", source_binding), ("target", target_binding)]:
        if binding is None:
            continue
        permitted = set(binding.get("permitted_capabilities", []))
        for capability in sorted(capabilities - permitted):
            errors.append(
                f"handoff_scope.capabilities: '{capability}' is not permitted "
                f"by the {label} authority binding"
            )

    pending_items = []
    state_transfer = document.get("state_transfer", {})
    if isinstance(state_transfer, dict):
        pending_items = state_transfer.get("pending_items", [])

    item_ids = [
        item.get("item_id")
        for item in pending_items
        if isinstance(item, dict) and isinstance(item.get("item_id"), str)
    ] if isinstance(pending_items, list) else []

    for item_id in duplicate_values(item_ids):
        errors.append(f"state_transfer.pending_items: duplicate item_id '{item_id}'")

    status = document.get("handoff_status")
    acknowledgements = document.get("acknowledgements", {})

    if status == "completed":
        if not document.get("effective_at"):
            errors.append("effective_at: required for completed handoff")
        if not document.get("completed_at"):
            errors.append("completed_at: required for completed handoff")

        if isinstance(acknowledgements, dict):
            for party in ["source", "target", "coordinator"]:
                value = acknowledgements.get(party, {})
                if not isinstance(value, dict) or value.get("status") != "accepted":
                    errors.append(
                        f"acknowledgements.{party}.status: must be accepted "
                        "for completed handoff"
                    )

        if isinstance(pending_items, list):
            for index, item in enumerate(pending_items):
                if not isinstance(item, dict):
                    continue
                if item.get("mandatory") and item.get("transfer_status") != "accepted":
                    errors.append(
                        f"state_transfer.pending_items[{index}]: mandatory "
                        "item must be accepted before completion"
                    )

    if status == "failed":
        if not document.get("failed_at"):
            errors.append("failed_at: required for failed handoff")
        if not document.get("status_reason"):
            errors.append("status_reason: required for failed handoff")

    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append("cancelled_at: required for cancelled handoff")
        if not document.get("status_reason"):
            errors.append("status_reason: required for cancelled handoff")

    if document.get("handoff_mode") == "emergency_takeover":
        if not document.get("incident_ref"):
            errors.append("incident_ref: required for emergency takeover")
        if not document.get("emergency_authorization_ref"):
            errors.append(
                "emergency_authorization_ref: required for emergency takeover"
            )

    effective_at = parse_datetime(document.get("effective_at"))
    completed_at = parse_datetime(document.get("completed_at"))
    if effective_at and completed_at and completed_at < effective_at:
        errors.append("completed_at: must not be earlier than effective_at")

    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def duty_rotation_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Duty Rotation Record semantics."""
    errors: list[str] = []
    participants = document.get("participant_assignments", [])
    participant_ids: list[str] = []
    participant_docs: dict[str, dict[str, Any]] = {}

    if isinstance(participants, list):
        for index, reference in enumerate(participants):
            assignment = resolved_record(
                reference,
                "assignment_id",
                "federation_operational_role_assignment",
                known,
                f"participant_assignments[{index}]",
                errors,
            )
            assignment_id = reference.get("assignment_id") if isinstance(reference, dict) else None

            if isinstance(assignment_id, str):
                participant_ids.append(assignment_id)

            if assignment is not None and isinstance(assignment_id, str):
                participant_docs[assignment_id] = assignment

                if assignment.get("federation_id") != document.get("federation_id"):
                    errors.append(
                        f"participant_assignments[{index}]: federation mismatch"
                    )

                if assignment.get("role_type") != document.get("role_type"):
                    errors.append(
                        f"participant_assignments[{index}]: role_type mismatch"
                    )

    for assignment_id in duplicate_values(participant_ids):
        errors.append(
            f"participant_assignments: duplicate assignment '{assignment_id}'"
        )

    sequence = document.get("sequence", [])
    sequence_numbers: list[str] = []
    sequence_assignment_ids: list[str] = []
    current_entries: list[dict[str, Any]] = []
    parsed_entries: list[tuple[datetime, datetime, dict[str, Any]]] = []

    if isinstance(sequence, list):
        for index, entry in enumerate(sequence):
            if not isinstance(entry, dict):
                continue

            sequence_numbers.append(str(entry.get("sequence_no")))
            assignment_id = entry.get("assignment_id")

            if isinstance(assignment_id, str):
                sequence_assignment_ids.append(assignment_id)
                if assignment_id not in participant_ids:
                    errors.append(
                        f"sequence[{index}].assignment_id: not declared as participant"
                    )

            if entry.get("duty_status") == "current":
                current_entries.append(entry)

            start_at = parse_datetime(entry.get("start_at"))
            end_at = parse_datetime(entry.get("end_at"))

            if start_at and end_at:
                if end_at < start_at:
                    errors.append(
                        f"sequence[{index}].end_at: must not precede start_at"
                    )
                parsed_entries.append((start_at, end_at, entry))

    for number in duplicate_values(sequence_numbers):
        errors.append(f"sequence: duplicate sequence_no '{number}'")

    for assignment_id in duplicate_values(sequence_assignment_ids):
        errors.append(
            f"sequence: assignment '{assignment_id}' appears more than once"
        )

    if set(sequence_assignment_ids) != set(participant_ids):
        errors.append(
            "sequence: must cover every participant assignment exactly once"
        )

    overlap_policy = document.get("overlap_policy", {})
    overlap_mode = overlap_policy.get("mode") if isinstance(overlap_policy, dict) else None
    maximum_overlap = overlap_policy.get("maximum_overlap_minutes", 0) if isinstance(overlap_policy, dict) else 0

    parsed_entries.sort(key=lambda item: item[0])
    for left, right in zip(parsed_entries, parsed_entries[1:]):
        _, left_end, _ = left
        right_start, _, _ = right
        overlap_seconds = (left_end - right_start).total_seconds()

        if overlap_seconds > 0:
            overlap_minutes = overlap_seconds / 60
            if overlap_mode == "none":
                errors.append("sequence: overlapping duty windows are prohibited")
            elif overlap_mode == "brief" and overlap_minutes > maximum_overlap:
                errors.append(
                    "sequence: overlap exceeds maximum_overlap_minutes"
                )

    status = document.get("rotation_status")
    current_ref = document.get("current_assignment_ref")
    next_ref = document.get("next_assignment_ref")

    if current_ref and next_ref and current_ref == next_ref:
        errors.append(
            "next_assignment_ref: must differ from current_assignment_ref"
        )

    if status == "active":
        if not document.get("started_at"):
            errors.append("started_at: required for active rotation")

        if len(current_entries) != 1:
            errors.append(
                "sequence: active rotation requires exactly one current entry"
            )
        elif current_entries[0].get("assignment_id") != current_ref:
            errors.append(
                "current_assignment_ref: does not match the current sequence entry"
            )

    if status == "completed":
        if not document.get("completed_at"):
            errors.append("completed_at: required for completed rotation")

        for index, entry in enumerate(sequence if isinstance(sequence, list) else []):
            if isinstance(entry, dict) and entry.get("duty_status") not in {
                "completed",
                "skipped",
            }:
                errors.append(
                    f"sequence[{index}].duty_status: completed rotation may "
                    "contain only completed or skipped entries"
                )

    if status == "suspended":
        if not document.get("suspended_at"):
            errors.append("suspended_at: required for suspended rotation")
        if not document.get("status_reason"):
            errors.append("status_reason: required for suspended rotation")

    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append("cancelled_at: required for cancelled rotation")
        if not document.get("status_reason"):
            errors.append("status_reason: required for cancelled rotation")

    if document.get("rotation_mode") == "incident_based" and not document.get(
        "incident_ref"
    ):
        errors.append("incident_ref: required for incident_based rotation")

    if document.get("rotation_mode") == "load_based" and not document.get(
        "capacity_policy_ref"
    ):
        errors.append("capacity_policy_ref: required for load_based rotation")

    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors



def formation_record_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Federation Formation Record semantics."""
    errors: list[str] = []
    federation_id = document.get("federation_id")
    status = document.get("formation_status")
    nodes = document.get("participating_nodes", [])
    node_ids: list[str] = []
    assignment_ids: list[str] = []
    node_map: dict[str, dict[str, Any]] = {}
    covered_roles: set[str] = set()

    if isinstance(nodes, list):
        for index, node in enumerate(nodes):
            if not isinstance(node, dict):
                continue
            node_id = node.get("node_id")
            if isinstance(node_id, str):
                node_ids.append(node_id)
                node_map[node_id] = node
            assignment_ref = node.get("assignment", {})
            assignment_document: dict[str, Any] | None = None
            if isinstance(assignment_ref, dict):
                assignment_id = assignment_ref.get("assignment_id")
                if isinstance(assignment_id, str):
                    assignment_ids.append(assignment_id)
                resolution_status = assignment_ref.get("resolution_status")
                if resolution_status == "externally_resolved" and not assignment_ref.get("record_ref"):
                    errors.append(
                        f"participating_nodes[{index}].assignment.record_ref: required for externally_resolved assignment"
                    )
                if resolution_status == "resolved":
                    assignment_document = known[
                        "federation_operational_role_assignment"
                    ].get(assignment_id)
                    if assignment_document is None:
                        errors.append(
                            f"participating_nodes[{index}].assignment.assignment_id: locally resolved record '{assignment_id}' was not found"
                        )
                    else:
                        if assignment_document.get("cell_id") != assignment_ref.get("source_cell_id"):
                            errors.append(
                                f"participating_nodes[{index}].assignment.source_cell_id: does not match Role Assignment"
                            )
                        if assignment_document.get("federation_id") != federation_id:
                            errors.append(
                                f"participating_nodes[{index}].assignment.assignment_id: Role Assignment belongs to another federation"
                            )
                        node_status = node.get("node_status")
                        assignment_status = assignment_document.get("assignment_status")
                        if node_status == "active" and assignment_status != "active":
                            errors.append(
                                f"participating_nodes[{index}].node_status: active node requires an active Role Assignment"
                            )
                        if node_status == "standby" and assignment_status not in {"active", "standby"}:
                            errors.append(
                                f"participating_nodes[{index}].node_status: standby node requires active or standby Role Assignment"
                            )
                        if node_status != "isolated":
                            role_type = assignment_document.get("role_type")
                            if isinstance(role_type, str):
                                covered_roles.add(role_type)

            binding_refs = node.get("authority_binding_refs", [])
            if isinstance(binding_refs, list):
                for binding_ref in binding_refs:
                    if (
                        isinstance(binding_ref, str)
                        and binding_ref
                        not in known["federation_authority_scope_binding"]
                    ):
                        errors.append(
                            f"participating_nodes[{index}].authority_binding_refs: locally referenced binding '{binding_ref}' was not found"
                        )

    for value in duplicate_values(node_ids):
        errors.append(f"participating_nodes: duplicate node_id '{value}'")
    for value in duplicate_values(assignment_ids):
        errors.append(
            f"participating_nodes: assignment '{value}' is placed more than once"
        )

    connections = document.get("connections", [])
    connection_ids: list[str] = []
    connection_keys: list[str] = []
    if isinstance(connections, list):
        for index, connection in enumerate(connections):
            if not isinstance(connection, dict):
                continue
            connection_id = connection.get("connection_id")
            if isinstance(connection_id, str):
                connection_ids.append(connection_id)
            from_node = connection.get("from_node_id")
            to_node = connection.get("to_node_id")
            if isinstance(from_node, str) and isinstance(to_node, str):
                connection_keys.append(
                    f"{from_node}|{to_node}|{connection.get('connection_type')}"
                )
            if from_node not in node_map:
                errors.append(
                    f"connections[{index}].from_node_id: node '{from_node}' was not found"
                )
            if to_node not in node_map:
                errors.append(
                    f"connections[{index}].to_node_id: node '{to_node}' was not found"
                )
            if from_node == to_node:
                errors.append(
                    f"connections[{index}]: a connection cannot target its source node"
                )
            if (
                status == "active"
                and connection.get("required") is True
                and connection.get("connection_status") != "active"
            ):
                errors.append(
                    f"connections[{index}].connection_status: required connection must be active in an active Formation"
                )

    for value in duplicate_values(connection_ids):
        errors.append(f"connections: duplicate connection_id '{value}'")
    for value in duplicate_values(connection_keys):
        errors.append(f"connections: duplicate node connection '{value}'")

    required_roles = document.get("required_role_types", [])
    if isinstance(required_roles, list) and status == "active":
        for role in required_roles:
            if isinstance(role, str) and role not in covered_roles:
                errors.append(
                    f"required_role_types: active Formation does not cover role '{role}'"
                )

    fallback = document.get("fallback_policy", {})
    if isinstance(fallback, dict):
        fallback_nodes = fallback.get("fallback_node_ids", [])
        if fallback.get("enabled") is True and not fallback_nodes:
            errors.append(
                "fallback_policy.fallback_node_ids: enabled fallback requires at least one node"
            )
        if isinstance(fallback_nodes, list):
            for node_id in fallback_nodes:
                if node_id not in node_map:
                    errors.append(
                        f"fallback_policy.fallback_node_ids: node '{node_id}' was not found"
                    )

    coordination = document.get("coordination_policy", {})
    if isinstance(coordination, dict):
        coordinator_refs = coordination.get("coordinator_refs", [])
        quorum = coordination.get("quorum")
        if (
            isinstance(coordinator_refs, list)
            and isinstance(quorum, int)
            and quorum > len(coordinator_refs)
        ):
            errors.append(
                "coordination_policy.quorum: cannot exceed the number of coordinators"
            )

    if status == "active":
        if not document.get("activated_at"):
            errors.append("activated_at: required for active Formation")
        active_nodes = [
            node for node in nodes
            if isinstance(node, dict) and node.get("node_status") == "active"
        ] if isinstance(nodes, list) else []
        if not active_nodes:
            errors.append(
                "participating_nodes: active Formation requires at least one active node"
            )

    if document.get("formation_type") == "wagon_fort":
        positions = {
            node.get("operational_position")
            for node in nodes
            if isinstance(node, dict)
        } if isinstance(nodes, list) else set()
        if "core" not in positions:
            errors.append("participating_nodes: wagon_fort requires a core node")
        if "perimeter" not in positions:
            errors.append(
                "participating_nodes: wagon_fort requires a perimeter node"
            )

    if status == "suspended":
        if not document.get("suspended_at"):
            errors.append("suspended_at: required for suspended Formation")
        if not document.get("status_reason"):
            errors.append("status_reason: required for suspended Formation")
    if status == "retired":
        if not document.get("retired_at"):
            errors.append("retired_at: required for retired Formation")
        if not document.get("status_reason"):
            errors.append("status_reason: required for retired Formation")

    created_at = parse_datetime(document.get("created_at"))
    for field in ["activated_at", "suspended_at", "retired_at"]:
        event_at = parse_datetime(document.get(field))
        if created_at and event_at and event_at < created_at:
            errors.append(f"{field}: must not be earlier than created_at")

    errors.extend(evidence_semantic_errors(document))
    return errors


def route_decision_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Route Decision Receipt semantics."""
    errors: list[str] = []
    formation_ref = document.get("formation", {})
    formation_document: dict[str, Any] | None = None
    if isinstance(formation_ref, dict):
        formation_id = formation_ref.get("formation_id")
        if formation_ref.get("resolution_status") == "externally_resolved" and not formation_ref.get("record_ref"):
            errors.append(
                "formation.record_ref: required for externally_resolved Formation"
            )
        if formation_ref.get("resolution_status") == "resolved":
            formation_document = known["federation_formation_record"].get(
                formation_id
            )
            if formation_document is None:
                errors.append(
                    f"formation.formation_id: locally resolved record '{formation_id}' was not found"
                )
            else:
                if formation_document.get("federation_id") != document.get("federation_id"):
                    errors.append(
                        "federation_id: does not match the referenced Formation"
                    )
                if document.get("decision_status") == "approved" and formation_document.get("formation_status") != "active":
                    errors.append(
                        "formation: approved Route Decision requires an active Formation"
                    )

    node_map: dict[str, dict[str, Any]] = {}
    if formation_document is not None:
        for node in formation_document.get("participating_nodes", []):
            if isinstance(node, dict) and isinstance(node.get("node_id"), str):
                node_map[node["node_id"]] = node

    requirements = document.get("route_requirements", {})
    max_hops = requirements.get("max_hops") if isinstance(requirements, dict) else None
    candidate_routes = document.get("candidate_routes", [])
    candidate_ids: list[str] = []
    candidate_map: dict[str, dict[str, Any]] = {}
    eligible_scores: list[float] = []

    if isinstance(candidate_routes, list):
        for index, candidate in enumerate(candidate_routes):
            if not isinstance(candidate, dict):
                continue
            candidate_id = candidate.get("candidate_id")
            if isinstance(candidate_id, str):
                candidate_ids.append(candidate_id)
                candidate_map[candidate_id] = candidate
            path = candidate.get("node_path", [])
            if isinstance(path, list):
                repeated = duplicate_values([x for x in path if isinstance(x, str)])
                for node_id in repeated:
                    errors.append(
                        f"candidate_routes[{index}].node_path: node '{node_id}' is repeated"
                    )
                if isinstance(max_hops, int) and len(path) > max_hops:
                    errors.append(
                        f"candidate_routes[{index}].node_path: exceeds max_hops {max_hops}"
                    )
                for node_id in path:
                    if node_id not in node_map:
                        errors.append(
                            f"candidate_routes[{index}].node_path: Formation node '{node_id}' was not found"
                        )

                roles: set[str] = set()
                caps: set[str] = set()
                for node_id in path:
                    node = node_map.get(node_id)
                    if not isinstance(node, dict):
                        continue
                    assignment_ref = node.get("assignment", {})
                    assignment = None
                    if isinstance(assignment_ref, dict):
                        assignment = known[
                            "federation_operational_role_assignment"
                        ].get(assignment_ref.get("assignment_id"))
                    if isinstance(assignment, dict):
                        role_type = assignment.get("role_type")
                        if isinstance(role_type, str):
                            roles.add(role_type)
                        assigned = assignment.get("assigned_capabilities", [])
                        if isinstance(assigned, list):
                            caps.update(x for x in assigned if isinstance(x, str))

                if candidate.get("candidate_status") == "eligible" and isinstance(requirements, dict):
                    for role in requirements.get("required_role_types", []):
                        if role not in roles:
                            errors.append(
                                f"candidate_routes[{index}]: eligible candidate does not cover required role '{role}'"
                            )
                    for capability in requirements.get("required_capabilities", []):
                        if capability not in caps:
                            errors.append(
                                f"candidate_routes[{index}]: eligible candidate does not cover required capability '{capability}'"
                            )
                    if requirements.get("audit_required") is True and "auditor" not in roles:
                        errors.append(
                            f"candidate_routes[{index}]: audit_required candidate must include an auditor"
                        )
                if candidate.get("candidate_status") == "rejected" and not candidate.get("rejection_reason"):
                    errors.append(
                        f"candidate_routes[{index}].rejection_reason: required for rejected candidate"
                    )
            if candidate.get("candidate_status") == "eligible" and isinstance(candidate.get("score"), (int, float)):
                eligible_scores.append(float(candidate["score"]))

    for value in duplicate_values(candidate_ids):
        errors.append(f"candidate_routes: duplicate candidate_id '{value}'")

    status = document.get("decision_status")
    selected_id = document.get("selected_candidate_id")
    fallback_id = document.get("fallback_candidate_id")
    if status == "approved":
        selected = candidate_map.get(selected_id)
        if selected is None:
            errors.append(
                "selected_candidate_id: approved decision must select an existing candidate"
            )
        elif selected.get("candidate_status") != "eligible":
            errors.append(
                "selected_candidate_id: approved decision must select an eligible candidate"
            )
        elif eligible_scores and float(selected.get("score", 0)) < max(eligible_scores) and not document.get("selection_override_ref"):
            errors.append(
                "selected_candidate_id: lower-scoring candidate requires selection_override_ref"
            )
        if not isinstance(document.get("decision"), dict):
            errors.append("decision: required for approved Route Decision")
        if isinstance(requirements, dict) and requirements.get("fallback_required") is True:
            fallback = candidate_map.get(fallback_id)
            if fallback is None or fallback.get("candidate_status") != "eligible":
                errors.append(
                    "fallback_candidate_id: fallback_required decision needs an eligible fallback candidate"
                )
            if fallback_id == selected_id:
                errors.append(
                    "fallback_candidate_id: must differ from selected_candidate_id"
                )

    if status == "revoked":
        if not document.get("revoked_at"):
            errors.append("revoked_at: required for revoked Route Decision")
        if not document.get("revocation_reason"):
            errors.append(
                "revocation_reason: required for revoked Route Decision"
            )

    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def value_flow_route_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Federation Value Flow Route semantics."""
    errors: list[str] = []
    formation_document: dict[str, Any] | None = None
    decision_document: dict[str, Any] | None = None

    formation_ref = document.get("formation", {})
    if isinstance(formation_ref, dict):
        if formation_ref.get("resolution_status") == "externally_resolved" and not formation_ref.get("record_ref"):
            errors.append(
                "formation.record_ref: required for externally_resolved Formation"
            )
        if formation_ref.get("resolution_status") == "resolved":
            formation_id = formation_ref.get("formation_id")
            formation_document = known["federation_formation_record"].get(
                formation_id
            )
            if formation_document is None:
                errors.append(
                    f"formation.formation_id: locally resolved record '{formation_id}' was not found"
                )

    decision_ref = document.get("route_decision", {})
    if isinstance(decision_ref, dict):
        if decision_ref.get("resolution_status") == "externally_resolved" and not decision_ref.get("record_ref"):
            errors.append(
                "route_decision.record_ref: required for externally_resolved Route Decision"
            )
        if decision_ref.get("resolution_status") == "resolved":
            route_decision_id = decision_ref.get("route_decision_id")
            decision_document = known[
                "federation_cell_route_decision_receipt"
            ].get(route_decision_id)
            if decision_document is None:
                errors.append(
                    f"route_decision.route_decision_id: locally resolved record '{route_decision_id}' was not found"
                )
            elif decision_document.get("decision_status") != "approved":
                errors.append(
                    "route_decision: Value Flow Route requires an approved Route Decision"
                )

    node_map: dict[str, dict[str, Any]] = {}
    if formation_document is not None:
        if formation_document.get("federation_id") != document.get("federation_id"):
            errors.append("federation_id: does not match Formation")
        for node in formation_document.get("participating_nodes", []):
            if isinstance(node, dict) and isinstance(node.get("node_id"), str):
                node_map[node["node_id"]] = node

    selected_candidate: dict[str, Any] | None = None
    if decision_document is not None:
        for field in ["federation_id", "operation_id", "route_type"]:
            if document.get(field) != decision_document.get(field):
                errors.append(f"{field}: does not match Route Decision")
        selected_id = document.get("selected_candidate_id")
        if selected_id != decision_document.get("selected_candidate_id"):
            errors.append(
                "selected_candidate_id: does not match Route Decision"
            )
        if document.get("fallback_candidate_id") != decision_document.get("fallback_candidate_id"):
            errors.append(
                "fallback_candidate_id: does not match Route Decision"
            )
        for candidate in decision_document.get("candidate_routes", []):
            if isinstance(candidate, dict) and candidate.get("candidate_id") == selected_id:
                selected_candidate = candidate
                break

    stages = document.get("stages", [])
    stage_ids: list[str] = []
    sequences: list[int] = []
    stage_node_path: list[str] = []
    active_count = 0
    if isinstance(stages, list):
        for index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                continue
            stage_id = stage.get("stage_id")
            sequence = stage.get("sequence")
            node_id = stage.get("node_id")
            if isinstance(stage_id, str):
                stage_ids.append(stage_id)
            if isinstance(sequence, int):
                sequences.append(sequence)
            if isinstance(node_id, str):
                stage_node_path.append(node_id)
            if stage.get("stage_status") == "active":
                active_count += 1

            node = node_map.get(node_id)
            if node is None:
                errors.append(
                    f"stages[{index}].node_id: Formation node '{node_id}' was not found"
                )
                continue
            assignment_ref = node.get("assignment", {})
            assignment_id = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
            if stage.get("assignment_id") != assignment_id:
                errors.append(
                    f"stages[{index}].assignment_id: does not match Formation node assignment"
                )
            assignment = known["federation_operational_role_assignment"].get(
                assignment_id
            )
            if isinstance(assignment, dict):
                if stage.get("role_type") != assignment.get("role_type"):
                    errors.append(
                        f"stages[{index}].role_type: does not match Role Assignment"
                    )
                assigned_caps = set(
                    x for x in assignment.get("assigned_capabilities", [])
                    if isinstance(x, str)
                )
                for capability in stage.get("required_capabilities", []):
                    if capability not in assigned_caps:
                        errors.append(
                            f"stages[{index}].required_capabilities: capability '{capability}' is not assigned upstream"
                        )

    for value in duplicate_values(stage_ids):
        errors.append(f"stages: duplicate stage_id '{value}'")
    if sequences and sorted(sequences) != list(range(1, len(sequences) + 1)):
        errors.append("stages.sequence: values must be contiguous and start at 1")
    if selected_candidate is not None and stage_node_path != selected_candidate.get("node_path"):
        errors.append(
            "stages.node_id: stage path does not match the selected Route Decision candidate"
        )

    constraints = document.get("route_constraints", {})
    if isinstance(constraints, dict):
        max_hops = constraints.get("max_hops")
        if isinstance(max_hops, int) and len(stage_node_path) > max_hops:
            errors.append("stages: route exceeds route_constraints.max_hops")
        if constraints.get("audit_required") is True:
            role_types = {
                stage.get("role_type")
                for stage in stages
                if isinstance(stage, dict)
            } if isinstance(stages, list) else set()
            if "auditor" not in role_types:
                errors.append("stages: audit_required route must include an auditor")

    status = document.get("route_status")
    if status == "active":
        if not document.get("activated_at"):
            errors.append("activated_at: required for active Value Flow Route")
        if active_count != 1:
            errors.append(
                "stages: active Value Flow Route requires exactly one active stage"
            )
    if status == "completed":
        if not document.get("completed_at"):
            errors.append("completed_at: required for completed Value Flow Route")
        incomplete = [
            stage for stage in stages
            if isinstance(stage, dict) and stage.get("stage_status") != "completed"
        ] if isinstance(stages, list) else []
        if incomplete:
            errors.append(
                "stages: completed Value Flow Route requires every stage to be completed"
            )
    lifecycle_fields = {
        "suspended": "suspended_at",
        "failed": "failed_at",
        "cancelled": "cancelled_at",
    }
    if status in lifecycle_fields:
        field = lifecycle_fields[status]
        if not document.get(field):
            errors.append(f"{field}: required for {status} Value Flow Route")
        if not document.get("status_reason"):
            errors.append(
                f"status_reason: required for {status} Value Flow Route"
            )

    created_at = parse_datetime(document.get("created_at"))
    for field in ["activated_at", "completed_at", "suspended_at", "failed_at", "cancelled_at"]:
        value = parse_datetime(document.get(field))
        if created_at and value and value < created_at:
            errors.append(f"{field}: must not be earlier than created_at")

    errors.extend(evidence_semantic_errors(document))
    return errors


def formation_change_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Federation Formation Change Record semantics."""
    errors: list[str] = []
    formation_ref = document.get("formation", {})
    formation_document: dict[str, Any] | None = None
    if isinstance(formation_ref, dict):
        if formation_ref.get("resolution_status") == "externally_resolved" and not formation_ref.get("record_ref"):
            errors.append(
                "formation.record_ref: required for externally_resolved Formation"
            )
        if formation_ref.get("resolution_status") == "resolved":
            formation_id = formation_ref.get("formation_id")
            formation_document = known["federation_formation_record"].get(
                formation_id
            )
            if formation_document is None:
                errors.append(
                    f"formation.formation_id: locally resolved record '{formation_id}' was not found"
                )
            elif formation_document.get("federation_id") != document.get("federation_id"):
                errors.append("federation_id: does not match Formation")

    node_map: dict[str, dict[str, Any]] = {}
    connection_map: dict[str, dict[str, Any]] = {}
    if formation_document is not None:
        for node in formation_document.get("participating_nodes", []):
            if isinstance(node, dict) and isinstance(node.get("node_id"), str):
                node_map[node["node_id"]] = dict(node)
        for connection in formation_document.get("connections", []):
            if isinstance(connection, dict) and isinstance(connection.get("connection_id"), str):
                connection_map[connection["connection_id"]] = dict(connection)

    operations = document.get("operations", [])
    operation_ids: list[str] = []
    operation_keys: list[str] = []
    if isinstance(operations, list):
        for index, operation in enumerate(operations):
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operation_id")
            if isinstance(operation_id, str):
                operation_ids.append(operation_id)
            op_type = operation.get("operation_type")
            target_type = operation.get("target_type")
            target_id = operation.get("target_id")
            operation_keys.append(f"{op_type}|{target_type}|{target_id}")
            if target_type == "node":
                exists = target_id in node_map
                if op_type == "add_node":
                    if exists:
                        errors.append(
                            f"operations[{index}].target_id: added node already exists"
                        )
                    if not isinstance(operation.get("new_assignment"), dict):
                        errors.append(
                            f"operations[{index}].new_assignment: required for add_node"
                        )
                elif not exists:
                    errors.append(
                        f"operations[{index}].target_id: Formation node '{target_id}' was not found"
                    )
                if op_type == "update_node_status":
                    if not operation.get("new_node_status"):
                        errors.append(
                            f"operations[{index}].new_node_status: required"
                        )
                    elif exists:
                        node_map[target_id]["node_status"] = operation["new_node_status"]
                if op_type == "update_position" and not operation.get("new_position"):
                    errors.append(
                        f"operations[{index}].new_position: required"
                    )
                if op_type == "replace_assignment":
                    new_assignment = operation.get("new_assignment")
                    if not isinstance(new_assignment, dict):
                        errors.append(
                            f"operations[{index}].new_assignment: required"
                        )
                    elif new_assignment.get("resolution_status") == "resolved":
                        assignment_id = new_assignment.get("assignment_id")
                        assignment = known[
                            "federation_operational_role_assignment"
                        ].get(assignment_id)
                        if assignment is None:
                            errors.append(
                                f"operations[{index}].new_assignment.assignment_id: locally resolved record '{assignment_id}' was not found"
                            )
                        elif exists:
                            node_map[target_id]["assignment"] = new_assignment
                if op_type == "remove_node" and exists:
                    node_map.pop(target_id, None)
            elif target_type == "connection":
                exists = target_id in connection_map
                if op_type == "add_connection":
                    if exists:
                        errors.append(
                            f"operations[{index}].target_id: added connection already exists"
                        )
                elif not exists:
                    errors.append(
                        f"operations[{index}].target_id: Formation connection '{target_id}' was not found"
                    )
                if op_type == "update_connection_status" and not operation.get("new_connection_status"):
                    errors.append(
                        f"operations[{index}].new_connection_status: required"
                    )

    for value in duplicate_values(operation_ids):
        errors.append(f"operations: duplicate operation_id '{value}'")
    for value in duplicate_values(operation_keys):
        errors.append(f"operations: duplicate operation target '{value}'")

    status = document.get("change_status")
    if status == "applied":
        if not document.get("applied_at"):
            errors.append("applied_at: required for applied Formation Change")
        if formation_document is not None:
            covered_roles: set[str] = set()
            for node in node_map.values():
                if node.get("node_status") == "isolated":
                    continue
                assignment_ref = node.get("assignment", {})
                assignment_id = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
                assignment = known[
                    "federation_operational_role_assignment"
                ].get(assignment_id)
                if isinstance(assignment, dict) and isinstance(assignment.get("role_type"), str):
                    covered_roles.add(assignment["role_type"])
            for role in formation_document.get("required_role_types", []):
                if role not in covered_roles:
                    errors.append(
                        f"operations: applied Formation Change removes required role coverage for '{role}'"
                    )

    if document.get("trigger_type") == "incident" and not document.get("incident_ref"):
        errors.append("incident_ref: required for incident-triggered Formation Change")
    if status == "rejected":
        if not document.get("rejected_at"):
            errors.append("rejected_at: required for rejected Formation Change")
        if not document.get("status_reason"):
            errors.append("status_reason: required for rejected Formation Change")
    if status == "rolled_back":
        if not document.get("rolled_back_at"):
            errors.append("rolled_back_at: required for rolled_back Formation Change")
        if not document.get("rollback_ref"):
            errors.append("rollback_ref: required for rolled_back Formation Change")
        if not document.get("status_reason"):
            errors.append("status_reason: required for rolled_back Formation Change")

    route_impacts = document.get("route_impacts", [])
    if isinstance(route_impacts, list):
        route_ids: list[str] = []
        for index, impact in enumerate(route_impacts):
            if not isinstance(impact, dict):
                continue
            route_id = impact.get("route_id")
            if isinstance(route_id, str):
                route_ids.append(route_id)
                if route_id not in known["federation_value_flow_route"]:
                    errors.append(
                        f"route_impacts[{index}].route_id: locally referenced route '{route_id}' was not found"
                    )
            if impact.get("required_action") == "activate_fallback_candidate" and not impact.get("candidate_id"):
                errors.append(
                    f"route_impacts[{index}].candidate_id: required when activating fallback candidate"
                )
        for value in duplicate_values(route_ids):
            errors.append(f"route_impacts: duplicate route_id '{value}'")

    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors



def formation_node_map(formation: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    """Build a node-id map from a Formation."""
    if not isinstance(formation, dict):
        return {}
    return {
        node["node_id"]: node
        for node in formation.get("participating_nodes", [])
        if isinstance(node, dict) and isinstance(node.get("node_id"), str)
    }


def formation_connection_map(
    formation: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """Build a connection-id map from a Formation."""
    if not isinstance(formation, dict):
        return {}
    return {
        connection["connection_id"]: connection
        for connection in formation.get("connections", [])
        if isinstance(connection, dict)
        and isinstance(connection.get("connection_id"), str)
    }


def assignment_for_node(
    formation: dict[str, Any] | None,
    node_id: Any,
    known: KnownRecords,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Resolve a Formation node and its local Role Assignment."""
    node = formation_node_map(formation).get(node_id)
    if not isinstance(node, dict):
        return None, None
    assignment_ref = node.get("assignment", {})
    assignment_id = (
        assignment_ref.get("assignment_id")
        if isinstance(assignment_ref, dict)
        else None
    )
    assignment = known["federation_operational_role_assignment"].get(
        assignment_id
    )
    return node, assignment


def operational_incident_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Operational Incident Record semantics."""
    errors: list[str] = []
    formation = resolved_record(
        document.get("formation", {}),
        "formation_id",
        "federation_formation_record",
        known,
        "formation",
        errors,
    )
    if formation is not None and formation.get("federation_id") != document.get("federation_id"):
        errors.append("federation_id: does not match the Formation")

    affected_nodes = document.get("affected_nodes", [])
    affected_routes = document.get("affected_route_ids", [])
    if not affected_nodes and not affected_routes:
        errors.append("affected_nodes: at least one affected node or route is required")

    node_ids: list[str] = []
    node_map = formation_node_map(formation)
    if isinstance(affected_nodes, list):
        for index, affected in enumerate(affected_nodes):
            if not isinstance(affected, dict):
                continue
            node_id = affected.get("node_id")
            if isinstance(node_id, str):
                node_ids.append(node_id)
            node = node_map.get(node_id)
            if formation is not None and node is None:
                errors.append(
                    f"affected_nodes[{index}].node_id: Formation node '{node_id}' was not found"
                )
                continue
            if node is not None:
                assignment_ref = node.get("assignment", {})
                expected = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
                if affected.get("assignment_id") != expected:
                    errors.append(
                        f"affected_nodes[{index}].assignment_id: does not match the Formation node"
                    )
    for value in duplicate_values(node_ids):
        errors.append(f"affected_nodes: duplicate node_id '{value}'")

    if isinstance(affected_routes, list):
        for index, route_id in enumerate(affected_routes):
            if not isinstance(route_id, str):
                continue
            route = known["federation_value_flow_route"].get(route_id)
            if route is None:
                errors.append(
                    f"affected_route_ids[{index}]: locally referenced route '{route_id}' was not found"
                )
            elif formation is not None:
                formation_ref = route.get("formation", {})
                if not isinstance(formation_ref, dict) or formation_ref.get("formation_id") != formation.get("formation_id"):
                    errors.append(
                        f"affected_route_ids[{index}]: route belongs to another Formation"
                    )

    severity = document.get("severity")
    if severity in {"major", "critical"} and document.get("containment_required") is not True:
        errors.append("containment_required: major or critical incidents require containment")

    status = document.get("incident_status")
    if document.get("containment_required") is True and status in {
        "contained", "under_investigation", "resolved", "closed"
    } and not document.get("containment_refs"):
        errors.append("containment_refs: required after a containment-required incident is contained")

    detected_at = parse_datetime(document.get("detected_at"))
    resolved_at = parse_datetime(document.get("resolved_at"))
    closed_at = parse_datetime(document.get("closed_at"))
    resolution = document.get("resolution")
    if status in {"resolved", "closed"}:
        if not isinstance(resolution, dict):
            errors.append(f"resolution: required when incident_status is '{status}'")
        if resolved_at is None:
            errors.append(f"resolved_at: required when incident_status is '{status}'")
    if isinstance(resolution, dict):
        internal_resolved_at = parse_datetime(resolution.get("resolved_at"))
        if resolved_at and internal_resolved_at and resolved_at != internal_resolved_at:
            errors.append("resolution.resolved_at: must equal top-level resolved_at")
    if detected_at and resolved_at and resolved_at < detected_at:
        errors.append("resolved_at: must not be earlier than detected_at")
    if status == "closed":
        if closed_at is None:
            errors.append("closed_at: required when incident_status is 'closed'")
        if resolved_at and closed_at and closed_at < resolved_at:
            errors.append("closed_at: must not be earlier than resolved_at")

    errors.extend(evidence_semantic_errors(document))
    return errors


def cell_isolation_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Isolation Order semantics."""
    errors: list[str] = []
    incident = resolved_record(
        document.get("incident", {}), "incident_id",
        "federation_operational_incident_record", known, "incident", errors,
    )
    formation = resolved_record(
        document.get("formation", {}), "formation_id",
        "federation_formation_record", known, "formation", errors,
    )
    if formation is not None and formation.get("federation_id") != document.get("federation_id"):
        errors.append("federation_id: does not match the Formation")
    target = document.get("target_node", {})
    node_id = target.get("node_id") if isinstance(target, dict) else None
    assignment_id = target.get("assignment_id") if isinstance(target, dict) else None
    node, assignment = assignment_for_node(formation, node_id, known)
    if formation is not None and node is None:
        errors.append(f"target_node.node_id: Formation node '{node_id}' was not found")
    if node is not None:
        assignment_ref = node.get("assignment", {})
        expected = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
        if assignment_id != expected:
            errors.append("target_node.assignment_id: does not match the Formation node")
    if incident is not None:
        affected = {
            item.get("node_id")
            for item in incident.get("affected_nodes", [])
            if isinstance(item, dict)
        }
        if node_id not in affected:
            errors.append("target_node.node_id: target is not identified by the Incident")

    scope = document.get("isolation_scope", {})
    if isinstance(scope, dict):
        mode = scope.get("mode")
        capabilities = scope.get("capabilities", [])
        connections = scope.get("connection_ids", [])
        routes = scope.get("route_ids", [])
        has_targets = any(isinstance(value, list) and value for value in [capabilities, connections, routes])
        if mode == "partial" and not has_targets:
            errors.append("isolation_scope: partial isolation requires at least one target")
        if mode == "full" and has_targets:
            errors.append("isolation_scope: full isolation must not enumerate partial targets")
        assigned_caps = {
            value for value in (assignment or {}).get("assigned_capabilities", [])
            if isinstance(value, str)
        }
        if isinstance(capabilities, list):
            for capability in capabilities:
                if isinstance(capability, str) and capability not in assigned_caps:
                    errors.append(
                        f"isolation_scope.capabilities: capability '{capability}' is not assigned to the target"
                    )
        connection_map = formation_connection_map(formation)
        if isinstance(connections, list):
            for connection_id in connections:
                connection = connection_map.get(connection_id)
                if connection is None:
                    errors.append(
                        f"isolation_scope.connection_ids: Formation connection '{connection_id}' was not found"
                    )
                elif node_id not in {connection.get("from_node_id"), connection.get("to_node_id")}:
                    errors.append(
                        f"isolation_scope.connection_ids: connection '{connection_id}' does not touch the target node"
                    )
        if isinstance(routes, list):
            for route_id in routes:
                if route_id not in known["federation_value_flow_route"]:
                    errors.append(
                        f"isolation_scope.route_ids: locally referenced route '{route_id}' was not found"
                    )

    status = document.get("isolation_status")
    issued_at = parse_datetime(document.get("issued_at"))
    effective_at = parse_datetime(document.get("effective_at"))
    if status in {"active", "lifted"} and effective_at is None:
        errors.append(f"effective_at: required when isolation_status is '{status}'")
    if issued_at and effective_at and effective_at < issued_at:
        errors.append("effective_at: must not be earlier than issued_at")
    if status == "lifted":
        lifted_at = parse_datetime(document.get("lifted_at"))
        if lifted_at is None:
            errors.append("lifted_at: required when isolation_status is 'lifted'")
        if not isinstance(document.get("lift_decision"), dict):
            errors.append("lift_decision: required when isolation_status is 'lifted'")
        if effective_at and lifted_at and lifted_at < effective_at:
            errors.append("lifted_at: must not be earlier than effective_at")
    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append("cancelled_at: required when isolation_status is 'cancelled'")
        if not document.get("cancellation_reason"):
            errors.append("cancellation_reason: required when isolation_status is 'cancelled'")
    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def route_suspension_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Route Suspension Receipt semantics."""
    errors: list[str] = []
    incident = resolved_record(
        document.get("incident", {}), "incident_id",
        "federation_operational_incident_record", known, "incident", errors,
    )
    formation = resolved_record(
        document.get("formation", {}), "formation_id",
        "federation_formation_record", known, "formation", errors,
    )
    route = resolved_record(
        document.get("route", {}), "route_id",
        "federation_value_flow_route", known, "route", errors,
    )
    if route is not None:
        if route.get("federation_id") != document.get("federation_id"):
            errors.append("federation_id: does not match the Value Flow Route")
        route_formation = route.get("formation", {})
        if formation is not None and (
            not isinstance(route_formation, dict)
            or route_formation.get("formation_id") != formation.get("formation_id")
        ):
            errors.append("route: does not belong to the referenced Formation")
    if incident is not None and route is not None:
        if route.get("route_id") not in incident.get("affected_route_ids", []):
            errors.append("route.route_id: route is not identified by the Incident")

    scope = document.get("suspension_scope", {})
    if isinstance(scope, dict):
        mode = scope.get("mode")
        stage_ids = scope.get("stage_ids", [])
        connection_ids = scope.get("connection_ids", [])
        if mode == "full" and (stage_ids or connection_ids):
            errors.append("suspension_scope: full suspension must not enumerate stages or connections")
        if mode == "stage" and not stage_ids:
            errors.append("suspension_scope.stage_ids: required for stage suspension")
        if mode == "connection" and not connection_ids:
            errors.append("suspension_scope.connection_ids: required for connection suspension")
        if mode == "stage" and connection_ids:
            errors.append("suspension_scope.connection_ids: must be omitted for stage suspension")
        if mode == "connection" and stage_ids:
            errors.append("suspension_scope.stage_ids: must be omitted for connection suspension")
        route_stage_ids = {
            stage.get("stage_id")
            for stage in (route or {}).get("stages", [])
            if isinstance(stage, dict)
        }
        if isinstance(stage_ids, list):
            for stage_id in stage_ids:
                if route is not None and stage_id not in route_stage_ids:
                    errors.append(
                        f"suspension_scope.stage_ids: route stage '{stage_id}' was not found"
                    )
        connection_map = formation_connection_map(formation)
        if isinstance(connection_ids, list):
            for connection_id in connection_ids:
                if formation is not None and connection_id not in connection_map:
                    errors.append(
                        f"suspension_scope.connection_ids: Formation connection '{connection_id}' was not found"
                    )

    fallback = document.get("fallback_action", {})
    status = document.get("suspension_status")
    if isinstance(fallback, dict):
        action = fallback.get("action")
        if action == "activate_candidate":
            if not fallback.get("candidate_id"):
                errors.append("fallback_action.candidate_id: required for activate_candidate")
            if not fallback.get("activation_ref"):
                errors.append("fallback_action.activation_ref: required for activate_candidate")
        if action == "switch_route":
            if not fallback.get("fallback_route_id"):
                errors.append("fallback_action.fallback_route_id: required for switch_route")
            if not fallback.get("activation_ref"):
                errors.append("fallback_action.activation_ref: required for switch_route")
        if status == "rerouted" and action not in {"activate_candidate", "switch_route"}:
            errors.append("fallback_action.action: rerouted status requires an activated fallback")
        if action == "activate_candidate" and route is not None:
            decision_ref = route.get("route_decision", {})
            decision_id = decision_ref.get("route_decision_id") if isinstance(decision_ref, dict) else None
            decision_doc = known["federation_cell_route_decision_receipt"].get(decision_id)
            candidates = {
                candidate.get("candidate_id")
                for candidate in (decision_doc or {}).get("candidate_routes", [])
                if isinstance(candidate, dict) and candidate.get("candidate_status") == "eligible"
            }
            candidate_id = fallback.get("candidate_id")
            if decision_doc is not None and candidate_id not in candidates:
                errors.append(
                    f"fallback_action.candidate_id: eligible route candidate '{candidate_id}' was not found"
                )

    issued_at = parse_datetime(document.get("issued_at"))
    effective_at = parse_datetime(document.get("effective_at"))
    if status in {"active", "rerouted", "lifted"} and effective_at is None:
        errors.append(f"effective_at: required when suspension_status is '{status}'")
    if issued_at and effective_at and effective_at < issued_at:
        errors.append("effective_at: must not be earlier than issued_at")
    if status == "lifted":
        lifted_at = parse_datetime(document.get("lifted_at"))
        if lifted_at is None:
            errors.append("lifted_at: required when suspension_status is 'lifted'")
        if not isinstance(document.get("lift_decision"), dict):
            errors.append("lift_decision: required when suspension_status is 'lifted'")
        if effective_at and lifted_at and lifted_at < effective_at:
            errors.append("lifted_at: must not be earlier than effective_at")
    if status == "cancelled":
        if not document.get("cancelled_at"):
            errors.append("cancelled_at: required when suspension_status is 'cancelled'")
        if not document.get("cancellation_reason"):
            errors.append("cancellation_reason: required when suspension_status is 'cancelled'")
    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def recovery_assessment_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Recovery Assessment semantics."""
    errors: list[str] = []
    incident = resolved_record(
        document.get("incident", {}), "incident_id",
        "federation_operational_incident_record", known, "incident", errors,
    )
    formation = resolved_record(
        document.get("formation", {}), "formation_id",
        "federation_formation_record", known, "formation", errors,
    )
    isolation = resolved_record(
        document.get("isolation_order", {}), "isolation_id",
        "federation_cell_isolation_order", known, "isolation_order", errors,
    )
    target = document.get("target_node", {})
    node_id = target.get("node_id") if isinstance(target, dict) else None
    assignment_id = target.get("assignment_id") if isinstance(target, dict) else None
    node, assignment = assignment_for_node(formation, node_id, known)
    if formation is not None and node is None:
        errors.append(f"target_node.node_id: Formation node '{node_id}' was not found")
    if node is not None:
        assignment_ref = node.get("assignment", {})
        expected = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
        if assignment_id != expected:
            errors.append("target_node.assignment_id: does not match the Formation node")
    if isolation is not None and isolation.get("target_node") != target:
        errors.append("target_node: does not match the Isolation Order")
    if incident is not None:
        affected = {
            item.get("node_id") for item in incident.get("affected_nodes", [])
            if isinstance(item, dict)
        }
        if node_id not in affected:
            errors.append("target_node.node_id: target is not identified by the Incident")

    suspension_ids: list[str] = []
    suspensions: list[dict[str, Any]] = []
    refs = document.get("route_suspensions", [])
    if isinstance(refs, list):
        for index, reference in enumerate(refs):
            local_errors: list[str] = []
            suspension = resolved_record(
                reference, "route_suspension_id",
                "federation_route_suspension_receipt", known,
                f"route_suspensions[{index}]", local_errors,
            )
            errors.extend(local_errors)
            if isinstance(reference, dict) and isinstance(reference.get("route_suspension_id"), str):
                suspension_ids.append(reference["route_suspension_id"])
            if suspension is not None:
                suspensions.append(suspension)
                suspension_incident = suspension.get("incident", {})
                if incident is not None and (
                    not isinstance(suspension_incident, dict)
                    or suspension_incident.get("incident_id") != incident.get("incident_id")
                ):
                    errors.append(f"route_suspensions[{index}]: belongs to another Incident")
    for value in duplicate_values(suspension_ids):
        errors.append(f"route_suspensions: duplicate route_suspension_id '{value}'")

    requirements = document.get("recovery_requirements", {})
    required_caps = set()
    if isinstance(requirements, dict):
        required_caps = {
            value for value in requirements.get("required_capabilities", [])
            if isinstance(value, str)
        }
    assigned_caps = {
        value for value in (assignment or {}).get("assigned_capabilities", [])
        if isinstance(value, str)
    }
    for capability in sorted(required_caps - assigned_caps):
        errors.append(
            f"recovery_requirements.required_capabilities: capability '{capability}' is not assigned to the target"
        )

    checks = document.get("checks", [])
    check_ids: list[str] = []
    required_statuses: list[str] = []
    capability_statuses: dict[str, list[str]] = {}
    categories: set[str] = set()
    if isinstance(checks, list):
        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                continue
            check_id = check.get("check_id")
            if isinstance(check_id, str):
                check_ids.append(check_id)
            category = check.get("category")
            if isinstance(category, str):
                categories.add(category)
            status = check.get("status")
            if check.get("required") is True and isinstance(status, str):
                required_statuses.append(status)
            if category == "capability_test":
                capability = check.get("capability")
                if not isinstance(capability, str):
                    errors.append(f"checks[{index}].capability: required for capability_test")
                else:
                    capability_statuses.setdefault(capability, []).append(status)
    for value in duplicate_values(check_ids):
        errors.append(f"checks: duplicate check_id '{value}'")
    for capability in required_caps:
        statuses = capability_statuses.get(capability, [])
        if not statuses:
            errors.append(f"checks: missing capability_test for '{capability}'")
        elif len(statuses) > 1:
            errors.append(f"checks: duplicate capability_test for '{capability}'")
    if isinstance(requirements, dict):
        if requirements.get("require_audit_clearance") is True and "audit_clearance" not in categories:
            errors.append("checks: audit_clearance check is required")
        if requirements.get("require_security_clearance") is True and "security_clearance" not in categories:
            errors.append("checks: security_clearance check is required")
        if requirements.get("route_revalidation_required") is True and "route_compatibility" not in categories:
            errors.append("checks: route_compatibility check is required")

    status = document.get("recovery_status")
    blockers = document.get("blockers", [])
    conditions = document.get("conditions", [])
    if status == "ready":
        if any(value != "pass" for value in required_statuses):
            errors.append("checks: ready assessment requires every required check to pass")
        if blockers:
            errors.append("blockers: ready assessment must not contain blockers")
        if document.get("recommended_action") not in {"reactivate_full", "reactivate_limited"}:
            errors.append("recommended_action: ready assessment must recommend reactivation")
    if status == "conditionally_ready":
        if "fail" in required_statuses:
            errors.append("checks: conditionally_ready assessment cannot contain a required fail")
        if not conditions:
            errors.append("conditions: required for conditionally_ready assessment")
        if document.get("recommended_action") != "reactivate_limited":
            errors.append("recommended_action: conditionally_ready must recommend reactivate_limited")
    if status == "not_ready":
        if not blockers and "fail" not in required_statuses:
            errors.append("blockers: not_ready assessment requires a blocker or required failure")
        if document.get("recommended_action") in {"reactivate_full", "reactivate_limited"}:
            errors.append("recommended_action: not_ready assessment cannot recommend reactivation")

    assessed_at = parse_datetime(document.get("assessed_at"))
    valid_until = parse_datetime(document.get("valid_until"))
    if assessed_at and valid_until and valid_until < assessed_at:
        errors.append("valid_until: must not be earlier than assessed_at")
    errors.extend(evidence_semantic_errors(document))
    return errors


def cell_reactivation_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Reactivation Receipt semantics."""
    errors: list[str] = []
    recovery = resolved_record(
        document.get("recovery_assessment", {}), "recovery_assessment_id",
        "federation_cell_recovery_assessment", known,
        "recovery_assessment", errors,
    )
    incident = resolved_record(
        document.get("incident", {}), "incident_id",
        "federation_operational_incident_record", known, "incident", errors,
    )
    formation = resolved_record(
        document.get("formation", {}), "formation_id",
        "federation_formation_record", known, "formation", errors,
    )
    isolation = resolved_record(
        document.get("isolation_order", {}), "isolation_id",
        "federation_cell_isolation_order", known, "isolation_order", errors,
    )
    target = document.get("target_node", {})
    node_id = target.get("node_id") if isinstance(target, dict) else None
    assignment_id = target.get("assignment_id") if isinstance(target, dict) else None
    node, assignment = assignment_for_node(formation, node_id, known)
    if formation is not None and node is None:
        errors.append(f"target_node.node_id: Formation node '{node_id}' was not found")
    if node is not None:
        assignment_ref = node.get("assignment", {})
        expected = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
        if assignment_id != expected:
            errors.append("target_node.assignment_id: does not match the Formation node")
    if recovery is not None:
        if recovery.get("target_node") != target:
            errors.append("target_node: does not match the Recovery Assessment")
        recovery_incident = recovery.get("incident", {})
        if incident is not None and (
            not isinstance(recovery_incident, dict)
            or recovery_incident.get("incident_id") != incident.get("incident_id")
        ):
            errors.append("incident: does not match the Recovery Assessment")
    if isolation is not None and isolation.get("target_node") != target:
        errors.append("target_node: does not match the Isolation Order")

    mode = document.get("reactivation_mode")
    status = document.get("reactivation_status")
    recovery_status = recovery.get("recovery_status") if recovery is not None else None
    if mode == "full" and recovery_status != "ready":
        errors.append("reactivation_mode: full reactivation requires a ready Recovery Assessment")
    if mode == "limited" and recovery_status not in {"ready", "conditionally_ready"}:
        errors.append("reactivation_mode: limited reactivation requires ready or conditionally_ready assessment")
    if mode == "limited" and not document.get("conditions"):
        errors.append("conditions: required for limited reactivation")

    assigned_caps = {
        value for value in (assignment or {}).get("assigned_capabilities", [])
        if isinstance(value, str)
    }
    reactivated_caps = {
        value for value in document.get("reactivated_capabilities", [])
        if isinstance(value, str)
    }
    for capability in sorted(reactivated_caps - assigned_caps):
        errors.append(
            f"reactivated_capabilities: capability '{capability}' is not assigned to the target"
        )
    if mode == "full" and assignment is not None and reactivated_caps != assigned_caps:
        errors.append("reactivated_capabilities: full reactivation must restore exactly the assigned capabilities")
    if mode == "limited" and not reactivated_caps:
        errors.append("reactivated_capabilities: limited reactivation requires at least one capability")

    recovery_suspension_ids = {
        ref.get("route_suspension_id")
        for ref in (recovery or {}).get("route_suspensions", [])
        if isinstance(ref, dict)
    }
    recoverable_route_ids: set[str] = set()
    for suspension_id in recovery_suspension_ids:
        suspension = known["federation_route_suspension_receipt"].get(suspension_id)
        if isinstance(suspension, dict):
            route_ref = suspension.get("route", {})
            route_id = route_ref.get("route_id") if isinstance(route_ref, dict) else None
            if isinstance(route_id, str):
                recoverable_route_ids.add(route_id)
            if status == "activated" and route_id in document.get("restored_route_ids", []) and suspension.get("suspension_status") != "lifted":
                errors.append(
                    f"restored_route_ids: route '{route_id}' still has an unlifted suspension"
                )
    for route_id in document.get("restored_route_ids", []):
        if route_id not in recoverable_route_ids:
            errors.append(
                f"restored_route_ids: route '{route_id}' was not assessed for recovery"
            )

    if status == "activated":
        if not document.get("effective_at"):
            errors.append("effective_at: required when reactivation_status is 'activated'")
        if isolation is not None and isolation.get("isolation_status") != "lifted":
            errors.append("isolation_order: activated reactivation requires a lifted Isolation Order")
        if incident is not None and incident.get("incident_status") not in {"resolved", "closed"}:
            errors.append("incident: activated reactivation requires a resolved Incident")
    if status == "rejected":
        if not document.get("rejected_at"):
            errors.append("rejected_at: required when reactivation_status is 'rejected'")
        if not document.get("status_reason"):
            errors.append("status_reason: required when reactivation_status is 'rejected'")
    if status == "revoked":
        if not document.get("revoked_at"):
            errors.append("revoked_at: required when reactivation_status is 'revoked'")
        if not document.get("revocation_reason"):
            errors.append("revocation_reason: required when reactivation_status is 'revoked'")

    issued_at = parse_datetime(document.get("issued_at"))
    effective_at = parse_datetime(document.get("effective_at"))
    if issued_at and effective_at and effective_at < issued_at:
        errors.append("effective_at: must not be earlier than issued_at")
    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def reconfiguration_plan_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Federation Reconfiguration Plan semantics."""
    errors: list[str] = []
    formation = resolved_record(
        document.get("formation"), "formation_id",
        "federation_formation_record", known, "formation", errors,
    )
    if formation is not None and formation.get("federation_id") != document.get("federation_id"):
        errors.append("federation_id: does not match the Formation")

    operations = document.get("proposed_operations", [])
    operation_ids: list[str] = []
    node_map: dict[str, dict[str, Any]] = {}
    if formation is not None:
        for node in formation.get("participating_nodes", []):
            if isinstance(node, dict) and isinstance(node.get("node_id"), str):
                node_map[node["node_id"]] = dict(node)

    if isinstance(operations, list):
        for index, operation in enumerate(operations):
            if not isinstance(operation, dict):
                continue
            operation_id = operation.get("operation_id")
            if isinstance(operation_id, str):
                operation_ids.append(operation_id)
            operation_type = operation.get("operation_type")
            target_id = operation.get("target_id")
            if operation_type in {"remove_node", "replace_assignment", "update_node_status", "update_position"}:
                if target_id not in node_map:
                    errors.append(f"proposed_operations[{index}].target_id: Formation node '{target_id}' was not found")
                    continue
            if operation_type == "remove_node" and target_id in node_map:
                node_map.pop(target_id, None)
            if operation_type == "replace_assignment" and target_id in node_map:
                source_id = operation.get("source_assignment_id")
                assignment_ref = node_map[target_id].get("assignment", {})
                current_id = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
                if source_id != current_id:
                    errors.append(f"proposed_operations[{index}].source_assignment_id: does not match Formation node")
                replacement_id = operation.get("replacement_assignment_id")
                replacement = known["federation_operational_role_assignment"].get(replacement_id)
                source = known["federation_operational_role_assignment"].get(current_id)
                if replacement is None:
                    errors.append(f"proposed_operations[{index}].replacement_assignment_id: local Assignment '{replacement_id}' was not found")
                else:
                    if source is not None and source.get("role_type") != replacement.get("role_type"):
                        errors.append(f"proposed_operations[{index}].replacement_assignment_id: replacement Role type differs from source")
                    node_map[target_id]["assignment"] = {"assignment_id": replacement_id}
            if operation_type == "add_node":
                replacement_id = operation.get("replacement_assignment_id")
                if not replacement_id:
                    errors.append(f"proposed_operations[{index}].replacement_assignment_id: required for add_node")
                elif replacement_id not in known["federation_operational_role_assignment"]:
                    errors.append(f"proposed_operations[{index}].replacement_assignment_id: local Assignment '{replacement_id}' was not found")
                elif isinstance(target_id, str):
                    node_map[target_id] = {"node_id": target_id, "assignment": {"assignment_id": replacement_id}, "node_status": "standby"}

    for operation_id in duplicate_values(operation_ids):
        errors.append(f"proposed_operations: duplicate operation_id '{operation_id}'")

    role_types: set[str] = set()
    for node in node_map.values():
        assignment_ref = node.get("assignment", {})
        assignment_id = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
        assignment = known["federation_operational_role_assignment"].get(assignment_id)
        if isinstance(assignment, dict) and isinstance(assignment.get("role_type"), str):
            role_types.add(assignment["role_type"])
    for required_role in document.get("required_role_types", []):
        if required_role not in role_types:
            errors.append(f"required_role_types: proposed Formation loses required Role '{required_role}'")

    status = document.get("plan_status")
    if status in {"approved", "executing", "completed"}:
        if not isinstance(document.get("decision"), dict):
            errors.append(f"decision: required when plan_status is '{status}'")
        rollback = document.get("rollback_operations")
        if not isinstance(rollback, list) or not rollback:
            errors.append(f"rollback_operations: required when plan_status is '{status}'")
        if not document.get("rollback_policy_ref"):
            errors.append(f"rollback_policy_ref: required when plan_status is '{status}'")
    if status == "approved" and not document.get("approved_at"):
        errors.append("approved_at: required for approved Plan")
    if status == "executing" and not document.get("started_at"):
        errors.append("started_at: required for executing Plan")
    if status == "completed":
        if not document.get("completed_at"):
            errors.append("completed_at: required for completed Plan")
        if not document.get("execution_refs"):
            errors.append("execution_refs: required for completed Plan")
    if status == "cancelled":
        if not document.get("cancelled_at") or not document.get("status_reason"):
            errors.append("cancelled_at and status_reason: required for cancelled Plan")
    if status == "superseded" and not document.get("superseded_by_ref"):
        errors.append("superseded_by_ref: required for superseded Plan")
    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def cell_replacement_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Cell Replacement Record semantics."""
    errors: list[str] = []
    plan = resolved_record(document.get("plan"), "plan_id", "federation_reconfiguration_plan", known, "plan", errors)
    formation = resolved_record(document.get("formation"), "formation_id", "federation_formation_record", known, "formation", errors)
    replacement = resolved_record(document.get("replacement_assignment"), "assignment_id", "federation_operational_role_assignment", known, "replacement_assignment", errors)
    if plan is not None and plan.get("plan_status") not in {"approved", "executing", "completed"}:
        errors.append("plan: replacement requires an approved or executing Reconfiguration Plan")
    if formation is not None and formation.get("federation_id") != document.get("federation_id"):
        errors.append("federation_id: does not match the Formation")

    source_node_ref = document.get("source_node", {})
    source_assignment = None
    if isinstance(source_node_ref, dict) and formation is not None:
        node_id = source_node_ref.get("node_id")
        assignment_id = source_node_ref.get("assignment_id")
        node = next((n for n in formation.get("participating_nodes", []) if isinstance(n, dict) and n.get("node_id") == node_id), None)
        if node is None:
            errors.append(f"source_node.node_id: Formation node '{node_id}' was not found")
        else:
            assignment_ref = node.get("assignment", {})
            current_id = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
            if current_id != assignment_id:
                errors.append("source_node.assignment_id: does not match the Formation node")
            source_assignment = known["federation_operational_role_assignment"].get(current_id)

    replacement_id = document.get("replacement_assignment", {}).get("assignment_id") if isinstance(document.get("replacement_assignment"), dict) else None
    source_id = source_node_ref.get("assignment_id") if isinstance(source_node_ref, dict) else None
    if replacement_id == source_id:
        errors.append("replacement_assignment.assignment_id: must differ from source Assignment")
    if source_assignment is not None and replacement is not None:
        if source_assignment.get("role_type") != replacement.get("role_type"):
            errors.append("replacement_assignment: Role type must match source Assignment")
        source_caps = {v for v in source_assignment.get("assigned_capabilities", []) if isinstance(v, str)}
        replacement_caps = {v for v in replacement.get("assigned_capabilities", []) if isinstance(v, str)}
        transferred = {v for v in document.get("transfer_scope", {}).get("capabilities", []) if isinstance(v, str)} if isinstance(document.get("transfer_scope"), dict) else set()
        for capability in sorted(transferred - source_caps):
            errors.append(f"transfer_scope.capabilities: capability '{capability}' was not assigned to the source")
        for capability in sorted(transferred - replacement_caps):
            errors.append(f"transfer_scope.capabilities: capability '{capability}' is not available on the replacement")
        if document.get("authority_preservation") == "exact" and source_caps != replacement_caps:
            errors.append("authority_preservation: exact replacement requires equal capability sets")

    status = document.get("replacement_status")
    acknowledgements = document.get("acknowledgements", {})
    if status in {"authorized", "in_progress", "completed"} and not isinstance(document.get("decision"), dict):
        errors.append(f"decision: required when replacement_status is '{status}'")
    if status == "completed":
        for party in ["source", "target", "coordinator"]:
            ack = acknowledgements.get(party, {}) if isinstance(acknowledgements, dict) else {}
            if not isinstance(ack, dict) or ack.get("status") != "accepted":
                errors.append(f"acknowledgements.{party}.status: must be accepted for completed replacement")
        if not document.get("execution_ref"):
            errors.append("execution_ref: required for completed replacement")
        if not document.get("completed_at"):
            errors.append("completed_at: required for completed replacement")
    if status == "rolled_back":
        if not document.get("rollback_ref") or not document.get("rolled_back_at"):
            errors.append("rollback_ref and rolled_back_at: required for rolled-back replacement")
    if status == "failed":
        if not document.get("failed_at") or not document.get("status_reason"):
            errors.append("failed_at and status_reason: required for failed replacement")
    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


def capacity_rebalancing_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Capacity Rebalancing Receipt semantics."""
    errors: list[str] = []
    plan = resolved_record(document.get("plan"), "plan_id", "federation_reconfiguration_plan", known, "plan", errors)
    formation = resolved_record(document.get("formation"), "formation_id", "federation_formation_record", known, "formation", errors)
    if plan is not None and plan.get("plan_status") not in {"approved", "executing", "completed"}:
        errors.append("plan: capacity rebalancing requires an approved Plan")
    node_assignments: dict[str, str] = {}
    if formation is not None:
        for node in formation.get("participating_nodes", []):
            if isinstance(node, dict):
                assignment_ref = node.get("assignment", {})
                assignment_id = assignment_ref.get("assignment_id") if isinstance(assignment_ref, dict) else None
                if isinstance(node.get("node_id"), str) and isinstance(assignment_id, str):
                    node_assignments[node["node_id"]] = assignment_id

    tolerance = Decimal("0")
    normalization = document.get("normalization", {})
    if isinstance(normalization, dict):
        parsed = to_decimal(normalization.get("tolerance"))
        if parsed is not None:
            tolerance = parsed
    distributions: dict[str, dict[str, Decimal]] = {}
    for field in ["before_distribution", "after_distribution"]:
        total = Decimal("0")
        nodes: list[str] = []
        shares: dict[str, Decimal] = {}
        values = document.get(field, [])
        if isinstance(values, list):
            for index, entry in enumerate(values):
                if not isinstance(entry, dict):
                    continue
                node_id = entry.get("node_id")
                assignment_id = entry.get("assignment_id")
                share = to_decimal(entry.get("share"))
                if isinstance(node_id, str):
                    nodes.append(node_id)
                if share is not None:
                    total += share
                    if isinstance(node_id, str):
                        shares[node_id] = share
                if node_id not in node_assignments:
                    errors.append(f"{field}[{index}].node_id: Formation node '{node_id}' was not found")
                elif node_assignments.get(node_id) != assignment_id:
                    errors.append(f"{field}[{index}].assignment_id: does not match Formation node")
        for node_id in duplicate_values(nodes):
            errors.append(f"{field}: duplicate node_id '{node_id}'")
        if not decimal_equal(total, Decimal("1"), tolerance):
            errors.append(f"{field}.share: shares must sum to 1; got {total}")
        distributions[field] = shares
    if distributions.get("before_distribution") == distributions.get("after_distribution"):
        errors.append("after_distribution: must differ from before_distribution")
    status = document.get("rebalance_status")
    if status in {"approved", "applied"} and not isinstance(document.get("decision"), dict):
        errors.append(f"decision: required when rebalance_status is '{status}'")
    if status == "applied" and not document.get("applied_at"):
        errors.append("applied_at: required for applied Rebalance")
    if status == "reverted" and not document.get("reverted_at"):
        errors.append("reverted_at: required for reverted Rebalance")
    if status == "failed" and (not document.get("failed_at") or not document.get("status_reason")):
        errors.append("failed_at and status_reason: required for failed Rebalance")
    errors.extend(decision_time_errors(document))
    errors.extend(evidence_semantic_errors(document))
    return errors


DRILL_EXECUTION_TYPES = {
    "reconfiguration_plan": ("federation_reconfiguration_plan", "plan_id"),
    "cell_replacement": ("federation_cell_replacement_record", "replacement_id"),
    "capacity_rebalance": ("federation_capacity_rebalancing_receipt", "rebalance_id"),
    "formation_change": ("federation_formation_change_record", "change_id"),
    "incident": ("federation_operational_incident_record", "incident_id"),
    "isolation": ("federation_cell_isolation_order", "isolation_id"),
    "route_suspension": ("federation_route_suspension_receipt", "route_suspension_id"),
    "recovery_assessment": ("federation_cell_recovery_assessment", "recovery_assessment_id"),
    "reactivation": ("federation_cell_reactivation_receipt", "reactivation_id"),
}


def federation_drill_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Federation Drill Record semantics."""
    errors: list[str] = []
    resolved_record(document.get("formation"), "formation_id", "federation_formation_record", known, "formation", errors)
    if document.get("reconfiguration_plan") is not None:
        resolved_record(document.get("reconfiguration_plan"), "plan_id", "federation_reconfiguration_plan", known, "reconfiguration_plan", errors)
    if document.get("environment") == "controlled_production":
        if not document.get("authorization_ref"):
            errors.append("authorization_ref: required for controlled-production drill")
        scenario = document.get("scenario", {})
        if not isinstance(scenario, dict) or scenario.get("protected_live_operations") is not True:
            errors.append("scenario.protected_live_operations: must be true for controlled-production drill")

    objectives = document.get("objectives", [])
    objective_map: dict[str, dict[str, Any]] = {}
    objective_ids: list[str] = []
    if isinstance(objectives, list):
        for objective in objectives:
            if isinstance(objective, dict) and isinstance(objective.get("objective_id"), str):
                objective_ids.append(objective["objective_id"])
                objective_map[objective["objective_id"]] = objective
    for objective_id in duplicate_values(objective_ids):
        errors.append(f"objectives: duplicate objective_id '{objective_id}'")

    result_ids: list[str] = []
    result_map: dict[str, str] = {}
    results = document.get("results", [])
    if isinstance(results, list):
        for index, result in enumerate(results):
            if not isinstance(result, dict):
                continue
            objective_id = result.get("objective_id")
            if isinstance(objective_id, str):
                result_ids.append(objective_id)
                result_map[objective_id] = result.get("status")
                if objective_id not in objective_map:
                    errors.append(f"results[{index}].objective_id: unknown objective '{objective_id}'")
    for objective_id in duplicate_values(result_ids):
        errors.append(f"results: duplicate objective_id '{objective_id}'")

    if document.get("drill_status") == "completed":
        for objective_id in objective_map:
            if objective_id not in result_map:
                errors.append(f"results: completed Drill is missing objective '{objective_id}'")
        if not document.get("started_at") or not document.get("completed_at"):
            errors.append("started_at and completed_at: required for completed Drill")
    if document.get("drill_status") == "aborted" and (not document.get("aborted_at") or not document.get("abort_reason")):
        errors.append("aborted_at and abort_reason: required for aborted Drill")

    outcome = document.get("outcome")
    mandatory_statuses = [result_map.get(objective_id) for objective_id, objective in objective_map.items() if objective.get("mandatory") is True]
    if outcome == "passed" and any(status != "pass" for status in mandatory_statuses):
        errors.append("outcome: passed requires every mandatory objective to pass")
    if outcome == "conditionally_passed" and any(status in {"fail", "not_run", None} for status in mandatory_statuses):
        errors.append("outcome: conditionally_passed cannot contain failed or unrun mandatory objectives")
    if outcome == "failed" and not any(status == "fail" for status in result_map.values()):
        errors.append("outcome: failed requires at least one failed result")

    for index, execution in enumerate(document.get("execution_refs", [])):
        if not isinstance(execution, dict):
            continue
        errors.extend(external_reference_errors(execution, f"execution_refs[{index}]"))
        if execution.get("resolution_status") == "resolved":
            mapping = DRILL_EXECUTION_TYPES.get(execution.get("record_type"))
            if mapping is not None and execution.get("record_id") not in known[mapping[0]]:
                errors.append(f"execution_refs[{index}].record_id: local record '{execution.get('record_id')}' was not found")
    scheduled = parse_datetime(document.get("scheduled_at"))
    started = parse_datetime(document.get("started_at"))
    completed = parse_datetime(document.get("completed_at"))
    if scheduled and started and started < scheduled:
        errors.append("started_at: must not be earlier than scheduled_at")
    if started and completed and completed < started:
        errors.append("completed_at: must not be earlier than started_at")
    errors.extend(evidence_semantic_errors(document))
    return errors


CONFORMANCE_RECORD_TYPES = {
    "activation_request": ("federation_cell_activation_request", "request_id"),
    "readiness_assessment": ("federation_cell_readiness_assessment", "assessment_id"),
    "activation_receipt": ("federation_cell_activation_receipt", "receipt_id"),
    "role_assignment": ("federation_operational_role_assignment", "assignment_id"),
    "authority_binding": ("federation_authority_scope_binding", "binding_id"),
    "formation": ("federation_formation_record", "formation_id"),
    "route_decision": ("federation_cell_route_decision_receipt", "route_decision_id"),
    "value_flow_route": ("federation_value_flow_route", "route_id"),
    "incident": ("federation_operational_incident_record", "incident_id"),
    "isolation": ("federation_cell_isolation_order", "isolation_id"),
    "route_suspension": ("federation_route_suspension_receipt", "route_suspension_id"),
    "recovery_assessment": ("federation_cell_recovery_assessment", "recovery_assessment_id"),
    "reactivation": ("federation_cell_reactivation_receipt", "reactivation_id"),
    "reconfiguration_plan": ("federation_reconfiguration_plan", "plan_id"),
    "cell_replacement": ("federation_cell_replacement_record", "replacement_id"),
    "capacity_rebalance": ("federation_capacity_rebalancing_receipt", "rebalance_id"),
    "federation_drill": ("federation_drill_record", "drill_id"),
}


def operational_conformance_semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Validate Operational Conformance Report semantics."""
    errors: list[str] = []
    resolved_record(document.get("formation"), "formation_id", "federation_formation_record", known, "formation", errors)
    evaluated = document.get("evaluated_records", [])
    evaluated_keys: list[str] = []
    evaluated_types: set[str] = set()
    if isinstance(evaluated, list):
        for index, item in enumerate(evaluated):
            if not isinstance(item, dict):
                continue
            record_type = item.get("record_type")
            record_id = item.get("record_id")
            if isinstance(record_type, str) and isinstance(record_id, str):
                evaluated_keys.append(f"{record_type}|{record_id}")
                evaluated_types.add(record_type)
            errors.extend(external_reference_errors(item, f"evaluated_records[{index}]"))
            if item.get("resolution_status") == "resolved":
                mapping = CONFORMANCE_RECORD_TYPES.get(record_type)
                if mapping is not None and record_id not in known[mapping[0]]:
                    errors.append(f"evaluated_records[{index}].record_id: local record '{record_id}' was not found")
    for key in duplicate_values(evaluated_keys):
        errors.append(f"evaluated_records: duplicate record '{key}'")

    check_ids: list[str] = []
    required_statuses: list[str] = []
    checks = document.get("checks", [])
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue
            if isinstance(check.get("check_id"), str):
                check_ids.append(check["check_id"])
            if check.get("required") is True and isinstance(check.get("status"), str):
                required_statuses.append(check["status"])
    for check_id in duplicate_values(check_ids):
        errors.append(f"checks: duplicate check_id '{check_id}'")

    status = document.get("conformance_status")
    if status == "conformant":
        for required_type in {"reconfiguration_plan", "cell_replacement", "capacity_rebalance", "federation_drill"}:
            if required_type not in evaluated_types:
                errors.append(f"evaluated_records: conformant v0.5 report requires '{required_type}'")
        if any(value != "pass" for value in required_statuses):
            errors.append("checks: conformant report requires every required check to pass")
    if status == "conditionally_conformant":
        if any(value in {"fail", "not_assessed"} for value in required_statuses):
            errors.append("checks: conditionally conformant report cannot contain failed or unassessed required checks")
        if not document.get("exceptions"):
            errors.append("exceptions: required for conditional conformance")
    if status == "nonconformant":
        if not document.get("findings") or not document.get("remediation_actions"):
            errors.append("findings and remediation_actions: required for nonconformant report")
    if status == "incomplete" and not any(value == "not_assessed" for value in required_statuses):
        errors.append("checks: incomplete report requires at least one unassessed required check")
    if document.get("report_status") == "superseded" and not document.get("superseded_by_ref"):
        errors.append("superseded_by_ref: required for superseded report")
    assessed = parse_datetime(document.get("assessed_at"))
    valid_until = parse_datetime(document.get("valid_until"))
    if assessed and valid_until and valid_until < assessed:
        errors.append("valid_until: must not be earlier than assessed_at")
    errors.extend(evidence_semantic_errors(document))
    return errors

def semantic_errors(
    document: dict[str, Any],
    known: KnownRecords,
) -> list[str]:
    """Dispatch semantic validation by record type."""
    record_type = document.get("record_type")

    if record_type == "federation_cell_activation_request":
        return activation_request_semantic_errors(document)

    if record_type == "federation_cell_readiness_assessment":
        return readiness_assessment_semantic_errors(document, known)

    if record_type == "federation_cell_activation_receipt":
        return activation_receipt_semantic_errors(document, known)

    if record_type == "federation_cell_suspension_receipt":
        return suspension_receipt_semantic_errors(document, known)

    if record_type == "federation_operational_role_assignment":
        return operational_role_assignment_semantic_errors(document, known)

    if record_type == "federation_authority_scope_binding":
        return authority_scope_binding_semantic_errors(document, known)

    if record_type == "federation_cell_handoff_record":
        return cell_handoff_semantic_errors(document, known)

    if record_type == "federation_duty_rotation_record":
        return duty_rotation_semantic_errors(document, known)

    if record_type == "federation_formation_record":
        return formation_record_semantic_errors(document, known)

    if record_type == "federation_cell_route_decision_receipt":
        return route_decision_semantic_errors(document, known)

    if record_type == "federation_value_flow_route":
        return value_flow_route_semantic_errors(document, known)

    if record_type == "federation_formation_change_record":
        return formation_change_semantic_errors(document, known)

    if record_type == "federation_operational_incident_record":
        return operational_incident_semantic_errors(document, known)

    if record_type == "federation_cell_isolation_order":
        return cell_isolation_semantic_errors(document, known)

    if record_type == "federation_route_suspension_receipt":
        return route_suspension_semantic_errors(document, known)

    if record_type == "federation_cell_recovery_assessment":
        return recovery_assessment_semantic_errors(document, known)

    if record_type == "federation_cell_reactivation_receipt":
        return cell_reactivation_semantic_errors(document, known)

    if record_type == "federation_reconfiguration_plan":
        return reconfiguration_plan_semantic_errors(document, known)

    if record_type == "federation_cell_replacement_record":
        return cell_replacement_semantic_errors(document, known)

    if record_type == "federation_capacity_rebalancing_receipt":
        return capacity_rebalancing_semantic_errors(document, known)

    if record_type == "federation_drill_record":
        return federation_drill_semantic_errors(document, known)

    if record_type == "federation_operational_conformance_report":
        return operational_conformance_semantic_errors(document, known)

    return [
        f"record_type: no semantic validator for '{record_type}'"
    ]


def validate_document(
    path: Path,
    validators: dict[str, Draft202012Validator],
    known: KnownRecords,
) -> list[str]:
    """Validate one YAML document."""
    try:
        document = load_yaml(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        return [f"[load] {error}"]

    errors = schema_errors(document, validators)

    if errors:
        return [f"[schema] {error}" for error in errors]

    return [
        f"[semantic] {error}"
        for error in semantic_errors(document, known)
    ]


def print_errors(errors: list[str]) -> None:
    """Print formatted validation errors."""
    for error in errors:
        print(f"  - {error}")


def main() -> int:
    """Run repository validation."""
    print(
        "=== Royalty Cell Federation Operations Protocol Validation ==="
    )
    print()

    try:
        validators = load_validators()
    except Exception as error:
        print(f"[fatal] unable to load schemas: {error}")
        return 1

    for record_type, schema_path in SCHEMA_PATHS.items():
        print(
            f"schema [{record_type}]: "
            f"{schema_path.relative_to(ROOT_DIR)}"
        )

    print()

    pass_files = collect_yaml_files(PASS_DIR)
    fail_files = collect_yaml_files(FAIL_DIR)

    if not pass_files:
        print("[fatal] no pass examples found")
        return 1

    if not fail_files:
        print("[fatal] no fail examples found")
        return 1

    known = collect_known_records(pass_files, validators)
    validation_failed = False

    print("[validate-pass]")

    for path in pass_files:
        print(f"  {path.relative_to(ROOT_DIR)}")
        errors = validate_document(path, validators, known)

        if errors:
            validation_failed = True
            print("  [failed]")
            print_errors(errors)
        else:
            print("  [schema-ok]")
            print("  [semantic-ok]")

        print()

    print("[validate-expected-fail]")

    for path in fail_files:
        print(f"  {path.relative_to(ROOT_DIR)}")
        errors = validate_document(path, validators, known)

        if not errors:
            validation_failed = True
            print("  [unexpected-pass]")
            print(
                "  - invalid example passed all validation stages"
            )
        else:
            print("  [expected-failure]")
            print_errors(errors)

        print()

    if validation_failed:
        print("Validation failed.")
        return 1

    print("Known local records:")

    for record_type in sorted(known):
        print(f"  [{record_type}]")

        for record_id in sorted(known[record_type]):
            print(f"    - {record_id}")

    print()
    print(
        "All Royalty Cell Federation Operations Protocol examples "
        "behaved as expected."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
