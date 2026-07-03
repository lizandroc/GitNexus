"""Shared test environment — must run before any `app` module is imported,
because Settings reads the environment at import time. Keeping all env
setup here makes the suite order-independent.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["LAP_DATA_DIR"] = tempfile.mkdtemp(prefix="lap-test-")
os.environ["LAP_PROVIDER"] = "mock"
os.environ["LAP_MODEL"] = "mock-small"
os.environ["LAP_MODEL_FAST"] = "mock-fast"
os.environ["LAP_MODEL_QUALITY"] = "mock-quality"
