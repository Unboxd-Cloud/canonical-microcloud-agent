from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CommandSpec:
    tool: str
    action: str
    argv: list[str]
    mutating: bool = False
    cwd: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CommandResult:
    tool: str
    action: str
    argv: list[str]
    exit_code: int
    stdout: str
    stderr: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

