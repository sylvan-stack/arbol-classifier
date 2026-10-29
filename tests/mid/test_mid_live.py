"""Mid-tier selections. Write or run only in an explicitly requested testing task."""
from __future__ import annotations

import test_live as _support
from test_live import (ROOT ,SecurityStandIn ,live_check ,os ,patch ,sys)


class WithoutAKey(_support.WithoutAKey):
# TEST-TIER-BEGIN tests/test_live.py::WithoutAKey.test_a_build_made_while_no_key_is_stored_fails_the_live_check
    def test_a_build_made_while_no_key_is_stored_fails_the_live_check(self) -> None:
        folder = self.work / "build"
        (folder / "runtime/python/bin").mkdir(parents=True)
        (folder / "runtime/python/bin/python3.14").symlink_to(sys.executable)
        (folder / "scripts").symlink_to(ROOT / "scripts")
        stand_in = SecurityStandIn(self.work / "security")
        with patch.dict(os.environ, {live_check.SECURITY_SWITCH: str(stand_in.program)}):
            status, printed = self.live(folder)
        self.assertEqual(status, 1, printed)
        self.assertIn(f"live: {stand_in.program} takes the place of /usr/bin/security", printed)
        self.assertIn("live: `info` found no Jev key", printed)
        self.assertIn("`classify` ended with not_signed_in: No Jev API key was found.", printed)
        self.assertEqual({tuple(call["args"][:1]) for call in stand_in.calls()}, {("find-generic-password",)})
        self.assertEqual(live_check.command(folder, str(stand_in.program), "info")[3:6],
                         [str(folder / "scripts/contract_entry.py"), str(stand_in.program), "1.0"])
        self.assertEqual(live_check.command(folder, None, "info"), [str(folder / "bin/arbol-classifier"), "info"])
# TEST-TIER-END tests/test_live.py::WithoutAKey.test_a_build_made_while_no_key_is_stored_fails_the_live_check
