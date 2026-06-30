# Contributing to AI News Agent

Thank you for choosing to help improve the AI News Agent project! We welcome all contributions, from documentation fixes to major performance optimizations.

---

## 🛠️ Development Setup

1. Fork this repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/api-agent.git
   cd api-agent
   ```
3. Set up your virtual environment and install development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or .\venv\Scripts\Activate.ps1 on Windows
   pip install -r requirements.txt
   ```
4. Create a `.env` file from the example and verify with tests:
   ```bash
   copy .env.example .env
   python run_tests.py
   ```

---

## 📋 Pull Request Guidelines

Before opening a pull request, please make sure your changes follow these rules:

### 1. Code Quality & Typing
* All new public and helper functions should include clean **type hints** (e.g. `list[dict[str, any]]`).
* Exclude any raw/hardcoded secrets or credentials.

### 2. Execution Testing
* Run the interactive test suite:
   ```bash
   python run_tests.py
   ```
* Verify template generation:
   ```bash
   python preview_email.py
   ```
* Verify log creation by running the scheduler dry run test:
   ```bash
   python scheduler.py --test
   ```

### 3. Creating a Branch
Keep branch names descriptive:
* `feature/your-feature-name` for new components or settings.
* `bugfix/issue-description` for hotfixes or layout errors.

---

## 🤝 Code of Conduct

Be kind, respectful, and collaborative. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) for more details.
