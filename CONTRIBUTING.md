# Contributing to LeafGuard AI

Thank you for considering contributing to **LeafGuard AI**! 🌿  
We welcome bug reports, feature requests, documentation improvements, and code contributions.

## Getting Started

1. **Fork** the repository and clone it locally.
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the code style guidelines below.
4. Run the test suite to make sure nothing is broken.
5. Push to your fork and open a **Pull Request** against `main`.

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### ML Pipeline
```bash
cd ml
pip install -r requirements.txt
python scripts/download_dataset.py   # downloads PlantVillage subset
python training/train.py             # trains and evaluates the model
```

## Code Style Guidelines

### Python (Backend / ML)
- Follow **PEP 8** conventions.
- Use type hints for all function signatures.
- Write docstrings for public classes and functions.
- Keep functions focused — single responsibility principle.

### JavaScript / React (Frontend)
- Use functional components with hooks.
- Keep components small and reusable.
- Follow the existing file/folder naming convention.

## Testing

### Backend tests
```bash
cd backend
pytest -v
```

### ML tests
```bash
cd ml
pytest -v
```

### Frontend tests
```bash
cd frontend
npm run test
```

All three test suites must pass before a PR will be merged.

## Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <short description>
```

| Type       | When to use                              |
|------------|------------------------------------------|
| `feat`     | A new feature                            |
| `fix`      | A bug fix                                |
| `docs`     | Documentation only changes               |
| `test`     | Adding or updating tests                 |
| `chore`    | Maintenance, build scripts, CI changes   |
| `refactor` | Code change that is not a feature or fix |
| `perf`     | Performance improvement                  |

### Examples
```
feat(backend): add rate-limiting middleware
fix(frontend): correct confidence bar overflow on mobile
docs: add contributing guide
test(ml): add edge-case tests for preprocessing pipeline
```

## Reporting Issues

Please use the GitHub Issues tracker and include:
- A clear title and description.
- Steps to reproduce the problem.
- Expected vs actual behaviour.
- Environment details (OS, Python version, Node version).

## Code of Conduct

Be respectful, inclusive and constructive. We follow the standard  
[Contributor Covenant](https://www.contributor-covenant.org/) code of conduct.

---

Happy contributing! 🚀
