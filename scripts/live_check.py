# Compatibility entry: the mid-tier implementation lives in tests/mid/archived/scripts/live_check.py.
# Keep the original module/package and __file__ so existing fixtures resolve unchanged.
from pathlib import Path as _TierPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mid.archived.scripts.live_check import JEV as JEV
    from mid.archived.scripts.live_check import SECURITY_SWITCH as SECURITY_SWITCH
    from mid.archived.scripts.live_check import command as command
    from mid.archived.scripts.live_check import run_live as run_live
else:
    _tier_source = _TierPath(__file__).resolve().parents[1] / 'tests/mid/archived/scripts/live_check.py'
    exec(compile(_tier_source.read_bytes(), str(_tier_source), "exec"), globals())
