# UI Automation Architecture Guidelines

## Purpose
Use this document as the development standard for scaling this framework from a few tests to ~50–300 UI tests without technical debt.

Constraints:
- Keep existing stack: Python, Pytest, Playwright (sync), POM
- Do not rewrite current framework
- Do not add new libraries
- Prioritize maintainability, readability, and stable execution

---

## 1) Project Structure (Medium Size)

Keep the current roots and expand consistently.

```text
core/
pages/
  components/
tests/
  ui/
    smoke/
    regression/
    features/
  data/
  fixtures/
utils/
conftest.py
pytest.ini
```

Rules:
- `core/`: shared framework behavior (base classes, config, session helpers)
- `pages/`: full page objects (one page class per file)
- `pages/components/`: reusable UI components used by multiple pages
- `tests/ui/smoke/`: critical path tests only
- `tests/ui/regression/`: broad behavior coverage
- `tests/ui/features/`: grouped by domain (tasks, calendar, messages)
- `tests/data/`: static input payloads used by tests
- `tests/fixtures/`: split fixture modules when `conftest.py` grows

---

## 2) Page Object Model Rules

### Page objects must contain
- Locators/selectors
- UI actions (click, fill, select, submit)
- State query helpers (`is_*`, `get_*`)
- Page-specific waits tied to deterministic UI state

### Tests must contain
- Scenario intent and business flow
- Assertions for expected outcomes
- Data choice for each scenario

### Keep methods focused
- Good: `login(email, password)`, `wait_until_logged_in(email)`, `is_auth_error_hidden()`
- Avoid: one giant method that performs full scenario + assertions

---

## 3) Reusable Components Strategy

Create component objects for repeated UI blocks:
- Navigation bar
- Modals
- Forms/form sections
- Data tables/list panels

Pattern:
- Component owns only its own selectors and actions
- Page object composes components
- Test interacts with page API (or component via page) instead of raw selectors

Example composition idea:
- `TasksPage` uses `NavBarComponent`, `TaskFormComponent`, `TaskTableComponent`

---

## 4) Test Layering Strategy

Use both folders and markers.

### Smoke
- Fast, critical-path coverage
- Examples: login, open key section, one happy-path create flow

### Regression
- Comprehensive positive + negative coverage
- Full user journeys and validation breadth

### Feature tests
- Deep coverage for one functional domain
- Examples: tasks only, calendar only, messages only

Pytest marker guidance:
- `@pytest.mark.smoke`
- `@pytest.mark.regression`
- `@pytest.mark.feature_tasks` (or equivalent per feature)

Target behavior:
- Smoke suite stays short and stable
- Regression can be larger and scheduled more broadly

---

## 5) Fixture Strategy (Pytest)

### Session fixtures
- Browser process lifecycle
- Global configuration/environment setup

### Function-level fixtures
- New browser context/page per test for isolation
- Per-test cleanup when needed

### Authenticated user fixture
- Encapsulate login once
- Return ready authenticated page/state for tests that require auth
- Keep account selection configurable via environment values

### Test data fixture
- Return structured test data objects/dicts
- Support unique value generation for mutable/create scenarios

Rule:
- Keep fixtures explicit and single-purpose

---

## 6) Test Data Management

Principles:
- Separate test logic from test data
- Avoid brittle hardcoded IDs
- Make mutable data unique per test run where needed

Recommended approach:
- Stable baseline data in `tests/data/`
- Dynamic factory helpers for unique emails/task titles
- Each test creates/owns its own data whenever possible

Anti-patterns to avoid:
- Cross-test data dependencies
- Order-dependent tests
- Reusing one mutable shared object across many tests

---

## 7) Naming Conventions

### Files
- Page object: `<feature>_page.py`
- Component: `<feature>_component.py`
- Test module: `test_<feature>_<area>.py`

### Classes
- Pages: `LoginPage`, `TasksPage`
- Components: `NavBarComponent`, `TaskFormComponent`

### Test functions
- Pattern: `test_<expected_behavior>_<condition>`
- Example: `test_user_can_create_task_with_valid_data`

### Methods
- Actions: verb-based (`open_home`, `submit_form`)
- Queries: boolean/getter style (`is_visible`, `get_error_text`)

---

## 8) Flakiness Prevention (Playwright)

Hard rules:
- Never use `time.sleep()`
- Wait for deterministic UI signals only
- Use stable selectors (`id`, semantic attributes)
- Keep interactions locator-based and scoped
- Isolate tests with fresh context/page per test

Wait strategy examples:
- Wait for element visibility/hidden state
- Wait for URL/state transition
- Wait for explicit confirmation UI (success banner, section visible)

Stability checklist:
- Does the test depend on another test? If yes, refactor.
- Does it require fixed timing? If yes, replace with condition wait.
- Does selector rely on layout/CSS chain? If yes, stabilize selector.

---

## 9) Assertion Placement

Default rule:
- Assertions live in tests
- Page objects expose query helpers used by assertions

Use page assertions sparingly and only for low-level guard checks if absolutely needed.

Preferred pattern:
- In page: `is_tasks_section_visible()`
- In test: `assert login_page.is_tasks_section_visible()`

This keeps tests readable and failure reasons clear.

---

## 10) CI Parallel-Ready Design

Prepare now so parallelization is easy later:
- No test order dependency
- No shared mutable state between tests
- Unique test data per test where creation/update is involved
- Keep fixtures stateless and safe for concurrent execution
- Use markers/folder split so CI can shard suites by scope

Execution strategy later:
- Run smoke on each PR
- Run regression on schedule and/or protected branch
- Shard feature suites in parallel by marker/folder

---

## 11) Practical Code Review Checklist

Before merging a new test:
- No selectors in test file
- No hardcoded sleeps
- Uses page/component methods only
- Assertions are clear and business-oriented
- Test is independent and repeatable
- Test/module naming follows convention
- Appropriate marker assigned (smoke/regression/feature)

Before adding a new page/component method:
- Method has one responsibility
- Name is explicit
- Includes proper deterministic wait when needed
- Does not hide unrelated behavior

---

## 12) Growth Threshold Rules

Apply these as the suite grows:
- If `conftest.py` gets large, split to `tests/fixtures/` modules
- If selector appears in 2+ places, move into page/component
- If test exceeds ~30 lines, extract intent into page/component methods
- If one page class gets too large, split reusable parts into components

---

## Decision Defaults

When in doubt:
1. Favor readability over cleverness
2. Favor explicit waits over implicit timing assumptions
3. Favor small, independent tests over long chained scenarios
4. Keep page/component APIs simple and domain-oriented
