# Unit Testing & Coverage

This directory contains the documentation and instructions for our enhanced unit testing suite, focusing on Boundary Value Analysis (BVA).

## How to Run the Tests

To reproduce the test results and generate the coverage report, follow these steps:

1. **Activate the Virtual Environment**
   Ensure you have the virtual environment activated. The project uses `uv` for dependency management.
   ```bash
   # On Windows
   .venv\Scripts\activate
   ```

2. **Run Tests via Nox (Recommended)**
   The canonical way to run the full local check (formats, lints, type-checks Python and Rust, and runs all test suites) is via Nox:
   ```bash
   nox -e local
   ```
   *Note: If nox is not in your global path, you can run `.venv\Scripts\nox.exe -e local`.*

3. **Run Pytest Directly (Faster)**
   If you only want to run the specific padding tests that were added:
   ```bash
   pytest tests/hazmat/primitives/test_padding.py
   ```

4. **View Coverage Report**
   After running the full test suite via `nox`, the Coverage HTML report is automatically generated.
   Open `courseProjectDocs/Setup/coverage-report/index.html` in your browser to view the interactive report and verify the 100% coverage metrics.
