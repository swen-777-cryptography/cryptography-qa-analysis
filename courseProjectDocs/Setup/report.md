# Baseline Build & Test

## Test Suite Summary

The testing framework evaluates the core cryptographic operations, bindings, and extensions within the repository.

- **Unit Tests**: All the tests run were unit tests, focusing on isolated verification of individual functions and classes in both the Python and Rust environments. [GitHub CI Run Here](https://github.com/swen-777-cryptography/cryptography-qa-analysis/actions/workflows/ci.yml)
- **Integration/System Tests**: Not explicitly separated; integration logic is generally covered within the extensive unit test suite.

**Execution Instructions:**

- **GitHub Actions**: You can run the GitHub Action manually to execute the test suite in a clean CI environment.
- **Local Testing**: Clone the repo, install the `nox` pip package, run `nox -e local`. Many tests will be skipped due to your environment not having the correct openssl.
- **Coverage Results**: Clone the repo the [Index.html](courseProjectDocs\Setup\coverage-report\function_index.html) is screenshot of a CI run from 09/18/2026

## Baseline Coverage Metrics

The test suite is highly comprehensive, covering both the Python package and the Rust extension.

### Test Results

- **Total Tests Run**: 4,819
- **Passed**: 4,819
- **Failed**: 0
  - *Python Tests*: 4,711
  - *Rust Tests*: 108

### Coverage Summary

Based on the generated coverage HTML report:

- **Overall Coverage**: 100%
- **Statement Coverage**: 100%
- **Branch Coverage**: 100%

## Observations

- **Comprehensive Coverage**: The test suite is extremely thorough, maintaining 100% statement and branch coverage across the project.
- **Dependency Testing**: Dependency testing is highly rigorous "Dependency testing psychopaths", effectively verifying compatibility against multiple supported python versions (3.9 - 3.15) across multiple versions of macos, latest windows, several linux distributions along with various OpenSSL, LibreSSL, BoringSSL, and AWS-LC versions and edge cases.
