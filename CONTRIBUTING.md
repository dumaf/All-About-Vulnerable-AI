# Contributing to AAVAI

Thank you for your interest in contributing to **All About Vulnerable AI (AAVAI)**! Contributions help improve the platform and expand the range of AI security challenges available for learners and researchers.

---

## License

This project is licensed under the **Apache License 2.0**. By contributing, you agree that your contributions will be licensed under the same license.

A copy of the license will be included in the repository as `LICENSE`.

---

## How to Contribute

### Reporting Issues

If you find a bug, have a feature request, or notice a documentation gap:

1. Check existing [Issues](../../issues) to avoid duplicates.
2. Open a new issue with a clear title and detailed description.
3. Include steps to reproduce (for bugs), expected behavior, and screenshots if applicable.

### Submitting Changes

1. **Fork** the repository.
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the guidelines below.
4. **Test** your changes locally (see [Running Locally](#running-locally)).
5. **Commit** with a clear, descriptive message:
   ```bash
   git commit -m "Add: brief description of change"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a **Pull Request** against `main` with a summary of what changed and why.

---

## Development Setup

### Prerequisites

* Python 3.10+
* Node.js 18+
* NVIDIA GPU with CUDA drivers (for LLM inference)

### Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/dumaf/All-About-Vulnerable-AI.git
   cd All-About-Vulnerable-AI
   ```

2. Copy the environment template and configure:
   ```bash
   cp .env.example .env
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running Locally

Start both the backend and frontend:

```bash
cd frontend
npm run dev
```

* **Frontend**: `http://localhost:5173`
* **Backend API**: `http://localhost:5000`

---

## Contribution Guidelines

### Code Style

* **Python**: Follow PEP 8 conventions. Use type hints where practical.
* **TypeScript/React**: Use functional components with hooks. Follow the existing patterns in the codebase.
* **Commits**: Use clear, imperative-tense commit messages (e.g., `Add context poisoning module`, `Fix RAG retrieval bug`).

### Adding a New Challenge Module

If you want to add a new vulnerability sandbox:

1. **Backend**: Create a new directory under `backend/modules/<module_name>/` with:
   * `routes.py` — Flask blueprint with at least a `POST /chat` endpoint.
   * `system_prompt.txt` — System prompt template using `{{FLAG_PLACEHOLDER}}` syntax for flag injection.
   * Any additional files the module needs (e.g., `db.py` for database-backed challenges).

2. **Configuration**:
   * Add the module's flag to `.env`, `.env.example`, and `backend/config.py`.
   * Register the flag in `backend/modules/score/routes.py` under `_FLAGS`.
   * Register the blueprint in `backend/app.py`.

3. **Frontend**: Create a new page under `frontend/src/pages/` and:
   * Add a route in `frontend/src/App.tsx`.
   * Add an API function in `frontend/src/api/client.ts`.
   * Add a card on the Home dashboard in `frontend/src/pages/Home.tsx`.

4. **Documentation**: Update `README.md` with:
   * The new module in the Vulnerability Mapping table.
   * The new files in the Project Structure tree.

### Security Considerations

* **Never commit `.env`** — it is git-ignored and contains challenge flags.
* Use `.env.example` as the committable template.
* All configuration values must be loaded from environment variables via `backend/config.py`. Do not hardcode secrets, flags, or server settings.
* System prompt files use `{{PLACEHOLDER}}` syntax — the actual values are injected at runtime by the corresponding `routes.py`.

---

## Code of Conduct

Please be respectful and constructive in all interactions. This is an educational project — contributions should aim to improve learning outcomes for AI security practitioners.

---

## Questions?

If you're unsure about anything, open an issue or start a discussion. We're happy to help guide your contribution.
