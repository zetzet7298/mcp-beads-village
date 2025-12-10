"""Allow running as: python -m beads_village.dashboard"""
from .app import main
import sys

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else None
    main(workspace)
