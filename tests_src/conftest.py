"""⚠ **No test may write into the real `.state/` tree.** — AB-19.

```text
╔══════════════════════════════════════════════════════════════════╗
║  FOUND 2026-08-27.  A unit test called the entrypoint's main()    ║
║  with no isolation, on a premise that had stopped being true, and ║
║  had quietly become a FULL LIVE DAILY RUN: real vendor calls, and ║
║  a real CT-11.7 run directory written into the user's .state/runs ║
║  on EVERY `make check`.  44 phantom records accumulated there.    ║
║                                                                  ║
║  ★ The test is fixed.  This makes the class of mistake impossible ║
║  rather than fixed-once: the failure was not that one test, it    ║
║  was that a test COULD reach production state at all.            ║
╚══════════════════════════════════════════════════════════════════╝
```

★ `_state_dir()` honours `PIPELINE_STATE`, so redirecting it here covers every
caller — present and future — without any test having to remember to.
"""

import pytest


@pytest.fixture(autouse=True)
def _isolate_pipeline_state(tmp_path, monkeypatch):
    """Point `PIPELINE_STATE` at a per-test directory.

    ⚠ A test that genuinely wants the real tree must set the variable itself,
    **and say why** — which is the point: it becomes a visible decision instead
    of an accident.
    """
    monkeypatch.setenv("PIPELINE_STATE", str(tmp_path / "state"))
