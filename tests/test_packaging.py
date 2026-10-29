# Shared fixtures; case bodies live in top/ and mid/. See TESTS.md.
"""Delivery boundaries: the pinned archive, the Build record, the description and the checks."""

from __future__ import annotations
import hashlib
import json
import os
import tempfile
from unittest.mock import patch


import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_support  # noqa: E402
import package_build  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]


class Packaging(unittest.TestCase):
    pass  # TEST-TIER-EMPTY-SUITE; helpers remain importable.


# Archived complete imports; restore needed names in their original scope, not at this file tail.
