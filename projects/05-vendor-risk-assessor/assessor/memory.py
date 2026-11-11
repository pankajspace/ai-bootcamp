"""
memory.py — long-term assessment memory (Deep Search Module 7 / Lab 8 + Policy SEC-12.1).

Stores reusable vendor assessment knowledge across runs without storing personal data (DPDP Act / Module 11):
  * vendor_profiles: previous VendorProfile snapshots keyed by vendor name (for SEC-12.1 incremental re-reviews)
  * look_alikes:     domains rejected by the identity gate for a given vendor
  * quarantined:     URLs quarantined for prompt injection
  * lessons:         planner tips learned from past runs
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Optional

from .config import RUNS_DIR
from .schemas import VendorProfile

DEFAULT_MEMORY_FILE = RUNS_DIR / "memory.json"


class AssessmentMemory:
    def __init__(self, path: Path | str = DEFAULT_MEMORY_FILE):
        self.path = Path(path)
        self.data: dict[str, Any] = {
            "vendors": {},
            "look_alikes": {},
            "quarantined_urls": [],
            "lessons": [],
        }
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:
                pass

    def last_profile(self, vendor: str) -> Optional[VendorProfile]:
        raw = self.data["vendors"].get(vendor.lower())
        if not raw:
            return None
        try:
            return VendorProfile.model_validate(raw["profile"])
        except Exception:
            return None

    def last_reviewed_on(self, vendor: str) -> Optional[date]:
        raw = self.data["vendors"].get(vendor.lower())
        if not raw or not raw.get("as_of"):
            return None
        return date.fromisoformat(raw["as_of"])

    def known_look_alikes(self, vendor: str) -> set[str]:
        return set(self.data["look_alikes"].get(vendor.lower(), []))

    def known_quarantined(self) -> set[str]:
        return set(self.data.get("quarantined_urls", []))

    def record_profile(self, profile: VendorProfile) -> dict[str, dict[str, Any]]:
        """Record a completed VendorProfile and return a diff against any prior snapshot (SEC-12.1)."""
        key = profile.vendor.lower()
        prev = self.last_profile(profile.vendor)
        changes: dict[str, dict[str, Any]] = {}
        if prev is not None:
            all_fields = set(prev.facts) | set(profile.facts)
            for f in sorted(all_fields):
                old_f = prev.facts.get(f)
                new_f = profile.facts.get(f)
                old_val = old_f.value if old_f else None
                new_val = new_f.value if new_f else None
                if json.dumps(old_val, sort_keys=True, default=str) != json.dumps(new_val, sort_keys=True, default=str):
                    changes[f] = {
                        "previous": old_f.display if old_f else "UNKNOWN",
                        "current": new_f.display if new_f else "UNKNOWN",
                        "as_of": str(new_f.as_of) if new_f and new_f.as_of else None,
                    }

        self.data["vendors"][key] = {
            "vendor": profile.vendor,
            "as_of": profile.as_of.isoformat(),
            "profile": profile.model_dump(mode="json"),
            "last_changes": changes,
        }
        if profile.rejected:
            la = self.data["look_alikes"].setdefault(key, [])
            for u in profile.rejected:
                if u not in la:
                    la.append(u)
        if profile.quarantined:
            q_list = self.data.setdefault("quarantined_urls", [])
            for u in profile.quarantined:
                if u not in q_list:
                    q_list.append(u)
        self.save()
        return changes

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def reset(self) -> None:
        self.data = {"vendors": {}, "look_alikes": {}, "quarantined_urls": [], "lessons": []}
        if self.path.exists():
            self.path.unlink()
