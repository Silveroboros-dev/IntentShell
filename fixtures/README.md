# Fixture Evidence

The demo fixture is intentionally small so category mismatches are obvious at a glance.

Top-level paths in `fixtures/demo_repo/`:

- `build/`, `dist/`, `coverage/`: generated artifacts
- `src/`: source code
- `config/`: configuration
- `README.md`: documentation

Primary demo scenarios:

- `rm -rf ./*` with `delete only build artifacts`
- `mv build src archive` with `move only build artifacts`

These scenarios are mirrored by automated tests in `tests/test_core.py`.
