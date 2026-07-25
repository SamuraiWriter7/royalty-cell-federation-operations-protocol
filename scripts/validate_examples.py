#!/usr/bin/env python3
"""
Validate Royalty Cell Federation Operations Protocol examples.

Supported v0.1-v0.2 records:

- Federation Cell Activation Request
- Federation Cell Readiness Assessment
- Federation Cell Activation Receipt
- Federation Cell Suspension Receipt
- Federation Operational Role Assignment
- Federation Authority Scope Binding
- Federation Cell Handoff Record
- Federation Duty Rotation Record

Validation stages:

1. YAML loading
2. Record-type-specific JSON Schema validation
3. Record-type-specific semantic validation
4. Local cross-record reference validation
5. Lifecycle, role, capability, and time-order validation

Files under examples/pass must pass every validation stage.
Files under examples/fail must fail at least one validation stage.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
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
