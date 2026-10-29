# Mid-tier source from scripts/live_check.py; see MID_TIER.md.
# Shared helpers and refusal entry points remain at the original path.

# TEST-TIER-DISABLED-BEGIN scripts/live_check.py::run_live
# def run_live(folder: Path) -> int:
#     security = os.environ.get(SECURITY_SWITCH)
#     try:
#         if security is not None:
#             if not Path(security).is_absolute() or not os.access(security, os.X_OK):
#                 raise LiveFailure(f"{SECURITY_SWITCH} must name an executable file by its absolute path.")
#             print(f"live: {security} takes the place of /usr/bin/security ({SECURITY_SWITCH}).", flush=True)
#         status, info = call(folder, security, "info")
#         if status != 0:
#             raise refused("info", status, info)
#         if info.get("endpoint") != JEV:
#             raise LiveFailure(f"The settings name the endpoint {info.get('endpoint')}; the live check asks Jev "
#                               f"itself, at {JEV}.")
#         if info.get("keyFound") is not True:
#             print("live: `info` found no Jev key; `classify` is asked anyway, so that its own refusal is shown.",
#                   flush=True)
#         started = time.monotonic()
#         status, result = call(folder, security, "classify", data=json.dumps(REQUEST).encode("utf-8"))
#         seconds = time.monotonic() - started
#         if status != 0 or "error" in result:
#             raise refused("classify", status, result)
#         print(f"live: passed in {seconds:.2f} s. {judge(info, result)}", flush=True)
#         return 0
#     except LiveFailure as failure:
#         print(f"live: failed. {failure}", flush=True)
#         return 1
# TEST-TIER-DISABLED-END scripts/live_check.py::run_live

# TEST-TIER-IMPORTS-BEGIN scripts/live_check.py:28
# import time
# TEST-TIER-IMPORTS-END scripts/live_check.py:28

raise RuntimeError("Mid-tier checks require an explicitly requested testing task; see MID_TIER.md.")
