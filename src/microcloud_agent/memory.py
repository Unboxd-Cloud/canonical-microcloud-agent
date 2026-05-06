from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _memory_path() -> Path:
    explicit = os.environ.get("MICROCLOUD_AGENT_MEMORY_PATH", "").strip()
    if explicit:
        return Path(explicit).expanduser()
    snap_common = os.environ.get("SNAP_COMMON", "").strip()
    if snap_common:
        return Path(snap_common) / "memory.json"
    return Path.home() / ".local" / "state" / "canonical-microcloud-agent" / "memory.json"


@dataclass
class AgentMemory:
    operator_preferences: dict[str, Any] = field(default_factory=dict)
    host_observations: dict[str, dict[str, Any]] = field(default_factory=dict)
    recent_goals: list[str] = field(default_factory=list)


class MemoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or _memory_path()

    def load(self) -> AgentMemory:
        if not self.path.exists():
            return AgentMemory()
        try:
            return AgentMemory(**json.loads(self.path.read_text()))
        except (OSError, TypeError, json.JSONDecodeError):
            return AgentMemory()

    def save(self, memory: AgentMemory) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(memory), indent=2, sort_keys=True))

    def record_goal(self, goal: str) -> AgentMemory:
        memory = self.load()
        normalized = goal.strip()
        if normalized:
            memory.recent_goals = [normalized, *[item for item in memory.recent_goals if item != normalized]][:10]
            self.save(memory)
        return memory

    def remember_preference(self, key: str, value: Any) -> AgentMemory:
        memory = self.load()
        memory.operator_preferences[key] = value
        self.save(memory)
        return memory

    def remember_host(self, hostname: str, observation: dict[str, Any]) -> AgentMemory:
        memory = self.load()
        memory.host_observations[hostname] = observation
        self.save(memory)
        return memory
