# Mutation Testing Setup and Execution

To run mutation testing using `mutmut` on this project, you must use **Windows Subsystem for Linux (WSL)**. The project relies on OpenSSL and `mutmut` utilizes the POSIX `fork()` mechanism, neither of which are natively available or easy to configure on Windows.

## 1. Use WSL

## 2. Using the Automated Scripts

We have provided two bash scripts to automatically provision the WSL environment, install Rust/OpenSSL, and execute the mutation tests securely without polluting your Windows environment.

### Setup Environment

Run the setup script inside WSL. It will ask for your `sudo` password to install system dependencies (like `pkg-config`, `libssl-dev`), create a Linux-native virtual environment (`.venv-wsl`), install all testing packages, and compile the Rust extensions.

```bash
bash courseProjectDocs/mutation-testing/setup-mutmut-wsl.sh
```

### Run Mutation Tests

Once setup is complete, use the run script to automatically clear old caches and execute `mutmut run`. It reads from our updated `setup.cfg` configuration file automatically.

```bash
bash courseProjectDocs/mutation-testing/run-mutmut-wsl.sh
```

## 3. Investigating Results

The run script will output the results at the end. To see the diff for a specific surviving mutant (e.g., mutant #5), activate the environment and use `mutmut show`:

```bash
source .venv-wsl/bin/activate
mutmut show cryptography.utils.x_int_to_bytes__mutmut_5
```
