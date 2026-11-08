#!/usr/bin/env python3
"""Deprecated legacy importer: deliberately blocked after isolated skill refactor.

The old ZIP layout could overwrite the repository root and create an extra
root SKILL.md, causing incorrect CLI installation. Reconcile manually on a
separate branch and use selective, reviewed Git changes instead.
"""
import sys
if __name__ == "__main__":
    sys.exit("Legacy ZIP direct import is DISABLED to protect isolated Skill packaging. See docs/GITHUB_RELEASE_PROCEDURE_FA.md.")

