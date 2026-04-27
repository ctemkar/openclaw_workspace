from __future__ import annotations
import os
import yaml
from typing import Any, Dict
from .models import PlatformConfig


def _apply_env_overrides(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides using double-underscore notation.
    E.g. PLATFORM_MODE -> data["mode"]
         PLATFORM_RISK__KILL_SWITCH -> data["risk"]["kill_switch"]
    """
    prefix = "PLATFORM_"
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        path = key[len(prefix):].lower().split("__")
        target = data
        for part in path[:-1]:
            if part not in target or not isinstance(target[part], dict):
                target[part] = {}
            target = target[part]
        leaf = path[-1]
        # Coerce boolean strings
        if value.lower() in ("true", "1", "yes"):
            target[leaf] = True
        elif value.lower() in ("false", "0", "no"):
            target[leaf] = False
        else:
            try:
                target[leaf] = int(value)
            except ValueError:
                try:
                    target[leaf] = float(value)
                except ValueError:
                    target[leaf] = value
    return data


def load_config(path: str) -> PlatformConfig:
    """Load PlatformConfig from a YAML file with environment variable overrides."""
    with open(path, "r") as fh:
        raw: Dict[str, Any] = yaml.safe_load(fh) or {}
    raw = _apply_env_overrides(raw)
    return PlatformConfig(**raw)
