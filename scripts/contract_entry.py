"""Start the Build's program as the contract check does: with a stand-in in the place of `/usr/bin/security`.

    runtime/python/bin/python3.14 -I -B scripts/contract_entry.py <stand-in for security> <arguments>

It runs the same code as `bin/arbol-classifier`, from the same Build folder, with the same
interpreter and the same options, and changes one thing: the path of the `security` command.
The program itself has no option for that path, so the contract check never reaches the real
Keychain and a person's key stays out of it.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from arbol_classifier import key  # noqa: E402
from arbol_classifier.cli import entry  # noqa: E402

key.SECURITY = sys.argv[1]
sys.argv = [sys.argv[0], *sys.argv[2:]]
entry()
