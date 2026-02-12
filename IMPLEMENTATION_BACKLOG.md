# Automation Architecture Implementation Backlog

## Goal
Apply architecture improvements incrementally without rewriting the framework or breaking current tests.

---

## 1) Split UI tests by suite folders and markers
**Why first:** immediate execution control (smoke vs regression) with minimal code changes.

### Actions
- Create folders:
  - `tests/ui/smoke/`
  - `tests/ui/regression/`
  - `tests/ui/features/`
- Move existing login test to `tests/ui/smoke/` (or keep and duplicate by marker policy).
- Add markers in `pytest.ini`:
  - `smoke`
  - `regression`
  - `feature_tasks`, `feature_calendar`, `feature_messages` (as needed)
- Tag tests consistently.

### Definition of done
- Can run: `pytest -m smoke`
- Can run: `pytest -m regression`
- Marker warnings are gone.

---

## 2) Introduce reusable UI component layer
**Why second:** prevents selector duplication as test count grows.

### Actions
- Create `pages/components/`.
- Start with the most reused component (likely auth panel/navbar/modal/table).
- Move repeated selectors/actions from page objects into component classes.
- Compose components inside page objects (page exposes component via property).

### Definition of done
- At least one shared component used by 2+ page objects or tests.
- Repeated selectors removed from multiple page classes.

---

## 3) Add authenticated fixture + data factory fixture
**Why third:** reduces test setup noise and improves consistency.

### Actions
- Add authenticated fixture (login once per test context and return ready state).
- Add test data fixture/factory for unique values (email/title suffixes).
- Keep fixtures in `conftest.py` initially; split later only if file grows.

### Definition of done
- New tests no longer repeat raw login setup steps.
- Mutable-data tests use fixture-generated unique values.

---

## 4) Enforce page/test responsibility boundaries
**Why fourth:** controls long-term readability and avoids hidden test logic.

### Actions
- Audit tests for inline selectors and move them to page/component classes.
- Ensure page methods expose actions + `is_*/get_*` state queries only.
- Keep business assertions in test files.

### Definition of done
- No selectors in test modules.
- Test functions read as scenario steps + assertions only.

---

## 5) Make parallel-safe by design (before CI parallelization)
**Why fifth:** avoids painful refactor later.

### Actions
- Ensure each test is independent (no order assumptions).
- Use fresh browser context/page per test.
- Avoid shared mutable test data across tests.
- Keep run artifacts local and ignored (`allure-results/`, caches, temp output).

### Definition of done
- Tests pass in random order.
- No test fails due to data collision when run repeatedly.

---

## Suggested Rollout Plan (1–2 weeks)
- **Day 1–2:** Item 1 (suites + markers)
- **Day 3–4:** Item 3 (fixtures for auth + data)
- **Day 5–7:** Item 2 and 4 (component extraction + boundary cleanup)
- **Day 8+:** Item 5 hardening checks

---

## Weekly Health Checks
- % tests with selectors in test files (target: 0)
- Avg test duration by marker (`smoke`, `regression`)
- Flaky rerun count (target: decreasing trend)
- Duplicate selector hotspots across pages/components
