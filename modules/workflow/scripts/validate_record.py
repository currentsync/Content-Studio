#!/usr/bin/env python3
"""Validate a content-system YAML record against its declarative schema."""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[3]


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def required_now(spec: dict, parent: dict) -> bool:
    if spec.get("required") is True:
        return True
    expression = spec.get("required_when")
    if not expression:
        return False
    parts = str(expression).split("==", 1)
    if len(parts) != 2:
        raise ValueError(f"Unsupported required_when expression: {expression}")
    field, expected = (part.strip() for part in parts)
    return str(parent.get(field)) == expected


def validate_object(value, fields: dict, path: str, types: dict, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected map")
        return
    for name, spec in fields.items():
        if not isinstance(spec, dict):
            continue
        if name not in value:
            if required_now(spec, value):
                errors.append(f"{path}.{name}: required field missing")
            continue
        validate_value(value[name], spec, f"{path}.{name}", types, errors)
    unknown = sorted(set(value) - set(fields))
    for name in unknown:
        errors.append(f"{path}.{name}: unknown field")


def validate_value(value, spec: dict, path: str, types: dict, errors: list[str]) -> None:
    kind = spec.get("type")
    if kind is None:
        validate_object(value, spec, path, types, errors)
        return
    if kind in types:
        validate_object(value, types[kind], path, types, errors)
    elif kind == "string":
        if not isinstance(value, str):
            errors.append(f"{path}: expected string")
    elif kind == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{path}: expected integer")
        elif "minimum" in spec and value < spec["minimum"]:
            errors.append(f"{path}: must be >= {spec['minimum']}")
    elif kind == "boolean":
        if not isinstance(value, bool):
            errors.append(f"{path}: expected boolean")
    elif kind == "datetime":
        if not isinstance(value, (str, date, datetime)):
            errors.append(f"{path}: expected ISO datetime")
    elif kind == "enum":
        if value not in spec.get("values", []):
            errors.append(f"{path}: invalid value {value!r}")
    elif kind == "list":
        if not isinstance(value, list):
            errors.append(f"{path}: expected list")
        else:
            if len(value) < spec.get("min_items", 0):
                errors.append(f"{path}: requires at least {spec['min_items']} items")
            item_spec = spec.get("item")
            if isinstance(item_spec, dict):
                for index, item in enumerate(value):
                    validate_value(item, item_spec, f"{path}[{index}]", types, errors)
    elif kind == "map":
        if not isinstance(value, dict):
            errors.append(f"{path}: expected map")
        else:
            value_spec = spec.get("value")
            if isinstance(value_spec, dict):
                for key, item in value.items():
                    validate_value(item, value_spec, f"{path}.{key}", types, errors)
    else:
        errors.append(f"{path}: unknown schema type {kind!r}")

    if "const" in spec and value != spec["const"]:
        errors.append(f"{path}: expected constant {spec['const']!r}")
    required_fields = spec.get("required_fields", [])
    if required_fields and isinstance(value, dict):
        for field in required_fields:
            if field not in value:
                errors.append(f"{path}.{field}: required reference field missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()

    common = load_yaml(ROOT / "schemas/common-types.schema.yaml")
    types = common.get("types", {})
    schema = load_yaml(args.schema)
    fields = schema.get("record")
    if not isinstance(fields, dict):
        print("Schema has no record map", file=sys.stderr)
        return 2

    failed = False
    for record_path in args.records:
        errors: list[str] = []
        validate_object(load_yaml(record_path), fields, "$", types, errors)
        if errors:
            failed = True
            print(f"INVALID {record_path}")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"VALID {record_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
