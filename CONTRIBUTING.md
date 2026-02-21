# Contributing to Resume Verification System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

---

## 🎯 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and constructive
- Welcome different perspectives
- Focus on what's best for the community
- Report harassment or inappropriate behavior

---

## 🚀 Getting Started

### 1. Fork the Repository
Click the **Fork** button on GitHub to create your own copy.

### 2. Clone Your Fork
```bash
git clone https://github.com/YOUR_USERNAME/UsMiniProject.git
cd UsMiniProject
git remote add upstream https://github.com/ORIGINAL_OWNER/UsMiniProject.git
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-sso-login` ✅
- `bugfix/handle-pdf-errors` ✅
- `docs/update-api-docs` ✅
- `test/add-ml-pipeline-tests` ✅

---

## 📝 Development Workflow

### Backend (Python/FastAPI)

#### Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Code Style
```bash
# Format code with Black
pip install black
black .

# Lint with Flake8
pip install flake8
flake8 .

# Type checking with mypy
pip install mypy
mypy .
```

#### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_auth.py::test_login -v

# Generate coverage report
pytest tests/ --cov --cov-report=html
```

#### Commit Format
```bash
git commit -m "feat(auth): add two-factor authentication

- Integrate TOTP-based 2FA
- Add backup codes for account recovery
- Update JWT token validation"
```

### Frontend (React/TypeScript)

#### Setup
```bash
cd frontend
npm install
```

#### Code Style
```bash
# Format with Prettier
npx prettier --write src/

# Lint with ESLint
npm run lint

# Type check
npx tsc --noEmit
```

#### Testing
```bash
# Run tests
npm test

# Coverage report
npm test -- --coverage

# Build production
npm run build
```

#### Commit Format
```bash
git commit -m "feat(dashboard): add real-time verification status

- WebSocket connection for live updates
- Toast notifications for completion
- Refetch data on completion"
```

### ML/NLP Pipeline

#### Changes to ML Code
When modifying `ml_engine/`:

```bash
# Test on sample data
python -c "from ml_engine.pipeline import MLClassifier; model = MLClassifier(); model.predict(...)"

# Evaluate on test set
python ml_engine/evaluate_model.py

# Compare with baseline
python ml_engine/benchmark.py
```

#### Model Training
If you retrain the model:

1. Document the dataset size and composition
2. Report performance metrics (F1, precision, recall, accuracy)
3. Include SHAP feature importance analysis
4. Commit model files in `backend/models/`

### Blockchain/Smart Contracts

#### Setup
```bash
cd blockchain
npm install -g hardhat
npm install
```

#### Testing
```bash
# Compile
npx hardhat compile

# Run tests
npx hardhat test

# Check coverage
npx hardhat coverage
```

#### Deployment
```bash
# Testnet
npx hardhat run scripts/deploy.js --network mumbai

# Mainnet (after audit)
npx hardhat run scripts/deploy.js --network polygon
```

---

## 🔄 Making Changes

### 1. Keep Your Fork Updated
```bash
git fetch upstream
git rebase upstream/main
```

### 2. Make Small, Focused Changes
- One feature per branch
- Keep commits atomic
- Write clear commit messages

### 3. Write Tests
```python
# Backend test example
def test_login_with_valid_credentials():
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

```typescript
// Frontend test example
test('renders login form', () => {
  render(<LoginComponent />);
  expect(screen.getByText('Login')).toBeInTheDocument();
  expect(screen.getByTestId('email-input')).toBeInTheDocument();
});
```

### 4. Update Documentation
- Update README if changing features
- Add docstrings to new functions
- Update ARCHITECTURE.md if changing structure
- Update API docs in code comments

### 5. Check Before Committing
```bash
# Backend
cd backend
black .
flake8 .
mypy .
pytest tests/ -v

# Frontend
cd frontend
npx prettier --write src/
npm run lint
npm test
```

---

## 📤 Submitting a Pull Request

### 1. Push Your Branch
```bash
git push origin feature/your-feature-name
```

### 2. Create Pull Request on GitHub

**Title:** Use conventional commits
```
feat(component): short description
fix(bug): description
docs(readme): description
```

**Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Security enhancement

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed
- [ ] No breaking changes

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Added tests
- [ ] All tests pass
```

### 3. Address Review Comments
- Respond to feedback professionally
- Make requested changes
- Push updates to same branch (auto-updates PR)

### 4. Merge
Once approved, your PR will be merged to `main`

---

## 🐛 Bug Reports

### Finding a Bug?

1. **Check existing issues** to avoid duplicates
2. **Create a detailed report** with:
   - Clear title
   - Description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/logs
   - Environment (OS, Python version, etc.)

### Bug Report Template
```markdown
## Bug Description
Clear description of what's broken

## Steps to Reproduce
1. Click...
2. Enter...
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [Windows/Linux/macOS]
- Python: [version]
- Node: [version]
- Browser: [if frontend issue]

## Error Logs
[Paste relevant error messages]
```

---

## ✨ Feature Requests

### Suggesting a Feature?

1. **Check discussions** for similar ideas
2. **Create a discussion** or issue with:
   - Clear title
   - Problem statement
   - Proposed solution
   - Example usage
   - Why it's needed

---

## 📚 Documentation

### Writing Documentation

- Use **Markdown** format
- Include **code examples**
- Keep language **clear and simple**
- Update table of contents

### Documentation Structure
```markdown
# Feature Title

## Overview
Brief description

## Use Cases
When/why to use this

## Installation/Setup
Step-by-step instructions

## Usage
Code examples and explanations

## API Reference
If applicable

## Troubleshooting
Common issues and solutions

## See Also
Related features/docs
```

---

## 🎓 Learning Resources

### Backend (FastAPI/Python)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Python PEP 8](https://pep8.org/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)

### Frontend (React/TypeScript)
- [React Docs](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Material UI Docs](https://mui.com/material-ui/getting-started/)

### ML/AI
- [SpaCy NLP](https://spacy.io/)
- [Scikit-learn](https://scikit-learn.org/)
- [SHAP Documentation](https://shap.readthedocs.io/)

### Blockchain
- [Solidity Docs](https://docs.soliditylang.org/)
- [Web3.py](https://web3py.readthedocs.io/)
- [Polygon Docs](https://polygon.technology/developers/)

---

## 🚀 Release Process

### Version Numbering
Semantic Versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version number bumped
- [ ] Git tag created
- [ ] GitHub release created
- [ ] Docker images tagged

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## ❓ Questions?

- Check [Documentation](DOCUMENTATION_INDEX.md)
- Review [Architecture](ARCHITECTURE.md)
- Open a [Discussion](https://github.com/yourusername/UsMiniProject/discussions)
- Email: [contact info]

---

## 🙏 Thank You!

We appreciate your contributions to making this project better! 🎉

**Happy coding! 💻**
