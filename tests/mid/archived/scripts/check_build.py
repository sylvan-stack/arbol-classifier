# Mid-tier source from scripts/check_build.py; see MID_TIER.md.
# Shared helpers and refusal entry points remain at the original path.

# TEST-TIER-DISABLED-BEGIN scripts/check_build.py::unit
# def unit(folder: Path, number: str | None) -> int:
#     sys.path.insert(0, str(folder))
#     sys.path.insert(0, str(folder / "src"))
#     os.chdir(folder)
#     suite = unittest.TestLoader().discover(str(folder / "tests"))
#     if suite.countTestCases() == 0:
#         raise ValueError("The packaged unit check discovered no tests.")
#     return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
# TEST-TIER-DISABLED-END scripts/check_build.py::unit

# TEST-TIER-DISABLED-BEGIN scripts/check_build.py::contract
# def contract(folder: Path, number: str | None) -> int:
#     from contract_checks import run_contract
#
#     version, _ = metadata(folder)
#     return run_contract(folder / ENTRY, folder, version, number or "0")
# TEST-TIER-DISABLED-END scripts/check_build.py::contract

# TEST-TIER-DISABLED-BEGIN scripts/check_build.py::live
# def live(folder: Path, number: str | None) -> int:
#     from live_check import run_live
#
#     return run_live(folder)
# TEST-TIER-DISABLED-END scripts/check_build.py::live

# TEST-TIER-IMPORTS-BEGIN scripts/check_build.py:10
# import unittest
# TEST-TIER-IMPORTS-END scripts/check_build.py:10

raise RuntimeError("Mid-tier checks require an explicitly requested testing task; see MID_TIER.md.")
