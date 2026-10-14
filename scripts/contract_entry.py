"""Start the Build's program as the contract check does: with a stand-in for `/usr/bin/security`, and shorter times.

    runtime/python/bin/python3.14 -I -B scripts/contract_entry.py <stand-in for security> <time scale> <arguments>

It runs the same code as `bin/arbol-classifier`, from the same Build folder, with the same
interpreter and the same options, and changes two things: the path of the `security` command,
and the scale of every time of a call (the time limit and the waits between attempts), so that
a scenario about time takes a fraction of a second. The program itself has no option for
either, so the contract check never reaches the real Keychain and a person's key stays out of it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from arbol_classifier import key, limits  # noqa: E402
from arbol_classifier.cli import entry  # noqa: E402

key.SECURITY = sys.argv[1]
limits.SCALE = float(sys.argv[2])
sys.argv = [sys.argv[0], *sys.argv[3:]]
entry()
