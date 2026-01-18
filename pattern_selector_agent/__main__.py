"""
CLI entry point for the Pattern Selector Agent.

Run with:
    python -m pattern_selector_agent          # From parent directory
    python pattern_selector_agent/__main__.py # Direct execution
"""

import sys
from pathlib import Path

# Add parent directory to path for direct execution
# This allows running: python pattern_selector_agent/__main__.py
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from pattern_selector_agent.agent import run_interactive


if __name__ == "__main__":
    run_interactive()
