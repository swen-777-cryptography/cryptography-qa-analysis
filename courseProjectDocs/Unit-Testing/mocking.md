# Unit Testing II (Mocking)

### Summary
As mentioned previously, the `cryptography` package has testing standards so high that it is nearly impossible to find areas that can be improved in any regard. Mocking is certainly no exception, and we are unable to add mocking in a useful regard. 

### Existing Mocks
The testing suite already uses mocking in two areas:
1. Mocking the built-in `time.time` module using `monkeypatch`
2. Using dummy versions of cipher and hashing algorithms.

### Explanation
The purpose of mocking is to abstract relationships between modules (especially with third-party dependencies) is to avoid unknown behavior by the dependency and ensure consistent evaluation of the tested system's behavior. However, `cryptography`'s testing suite includes independent testing of multiple versions of dependencies, effectively skipping the abstraction step and guaranteeing correct behavior *in the actual dependency*.

### Coverage Improvement Analysis
Our coverage remains at 100%, though we did not add any new test cases.
