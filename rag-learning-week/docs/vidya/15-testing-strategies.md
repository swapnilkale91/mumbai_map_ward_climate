# Testing Strategies

A test suite is only valuable if it catches real bugs and is fast enough to run on every commit.

## The Testing Pyramid
- **Unit tests** (base): test individual functions in isolation. Fast, numerous. Mock external dependencies.
- **Integration tests** (middle): test a slice of the system (e.g. API route + DB). Require a real or in-process DB.
- **End-to-end tests** (top): test the full system through the UI or API. Slow, brittle; use sparingly for critical paths.

## What to Unit Test
Pure functions, domain logic, data transformations. Anything that has many edge cases and doesn't require external state.

## What to Integration Test
API handlers, repository classes, event processors — anything where the interaction between components matters.

## Test Doubles
- **Stub**: returns a canned value.
- **Mock**: records calls and can assert on them.
- **Spy**: wraps a real function and records calls.
- **Fake**: a lightweight real implementation (e.g. in-memory DB).

Prefer fakes over mocks for external services (DB, message queue). Mocks that mimic the wrong interface give false confidence.

## Property-Based Testing
Generate random inputs and verify invariants ("the output is always sorted", "encode then decode is identity"). Fast-check and hypothesis are popular libraries.

## Coverage
Line/branch coverage is a useful floor, not a ceiling. 80% is a reasonable minimum; 100% is often counterproductive (you end up testing implementation details). What matters is that critical paths are covered.

## Test-Driven Development (TDD)
Write the test first, watch it fail, write the minimum code to pass, refactor. Forces clear interfaces and prevents over-engineering.

## Continuous Integration
Run the full test suite on every pull request. Fail fast — keep the suite under 5 minutes. Flaky tests erode trust; fix or quarantine them immediately.
