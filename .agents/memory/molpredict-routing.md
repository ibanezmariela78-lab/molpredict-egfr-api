---
name: MolPredict EGFR API — routing architecture
description: How the Python FastAPI app is wired into Replit's application router via the api-server artifact.
---

## Rule
The Python FastAPI app (`artifacts/molpredict-api/`) must be run through the **`artifacts/api-server`** artifact (kind=api, previewPath="/"), NOT as a standalone `.replit` workflow. Only registered artifacts appear in the application router.

**Why:** This workspace uses `router = "application"` in `.replit` `[deployment]`. That router only routes traffic to paths registered in `artifact.toml` files. Standalone workflows have no registered paths and return 404 through the proxy, even if they listen on port 8000 and `waitForPort` is set.

**How to apply:**
- `artifact.toml` `[services.development] run` must use an **absolute path**: `cd /home/runner/workspace/artifacts/molpredict-api && uvicorn ...`
- Relative paths like `cd artifacts/molpredict-api` fail because the managed workflow CWD is not the workspace root.
- `[[ports]]` entries are stripped by `verifyAndReplaceDotReplit` in this workspace — do not use them.
- The `Settings` class reads env vars at **class definition time** (class-level attrs), not at instantiation. Patching `os.environ` then calling `Settings()` has no effect on already-defined attrs. Patch instance attrs directly in tests.
