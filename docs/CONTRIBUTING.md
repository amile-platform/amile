# Contributing to AMILE

## Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/amile.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make changes, write tests
5. Push and open a Pull Request against `main`

## Branch Naming
- `feature/` — new features
- `fix/` — bug fixes
- `docs/` — documentation only
- `ml/` — model training changes

## Commit Message Format
`type(scope): short description`

Examples:
- `feat(dkt): add LSTM layer for improved mastery prediction`
- `fix(equity): correct gap calculation for ELL students`
- `docs(readme): update quick start instructions`

## Code Style
- Python: PEP 8, formatted with `black`
- TypeScript: ESLint + Prettier
- All public functions must have docstrings
