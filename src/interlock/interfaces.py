"""Interface records: every handoff states its contract.

A boundary is honest only when it declares its guarantees, its constraints,
its owner, and what happens when it fails. Declared interfaces are kept in
the module-level :data:`REGISTRY`, keyed by name.
"""

from dataclasses import dataclass

REGISTRY: dict[str, "InterfaceRecord"] = {}


@dataclass
class InterfaceRecord:
    """The contract of one handoff."""

    name: str
    guarantees: str
    constraints: str
    owner: str
    failure_behavior: str

    def validate(self) -> "InterfaceRecord":
        """Require every field to be non-empty. Returns self for chaining."""
        missing = [
            field
            for field in ("name", "guarantees", "constraints", "owner", "failure_behavior")
            if not getattr(self, field)
        ]
        if missing:
            raise ValueError(f"interface record missing required fields: {missing}")
        return self


def declare(
    name: str,
    guarantees: str,
    constraints: str,
    owner: str,
    failure_behavior: str,
) -> InterfaceRecord:
    """Declare an interface, validate it, and register it in :data:`REGISTRY`."""
    record = InterfaceRecord(
        name=name,
        guarantees=guarantees,
        constraints=constraints,
        owner=owner,
        failure_behavior=failure_behavior,
    ).validate()
    REGISTRY[name] = record
    return record
