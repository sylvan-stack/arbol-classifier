# Shared fixtures only; test bodies are in top/ and mid/. See TESTS.md.
"""Delivery boundaries: the pinned archive, the Build record, the description and the checks."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

ROOT = Path(__file__).resolve().parents[1]


class Packaging(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
