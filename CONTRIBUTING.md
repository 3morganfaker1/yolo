# Git Collaboration Guide

## Branch strategy
- `main`: stable branch for deployable code.
- `feature/*`: feature development branch (one feature per branch).
- `fix/*`: bugfix branch.

## Daily workflow
1. Update local `main`:
   - `git checkout main`
   - `git pull origin main`
2. Create a feature branch:
   - `git checkout -b feature/your-feature-name`
3. Commit in small increments:
   - `git add <files>`
   - `git commit -m "feat: concise change summary"`
4. Push branch:
   - `git push -u origin feature/your-feature-name`
5. Open PR, review, and merge to `main`.

## Commit convention
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code restructure without behavior changes
- `docs:` documentation updates
- `chore:` tooling/config updates

## Team rules
- Do not push directly to `main`.
- Rebase or merge `main` frequently to reduce conflicts.
- Resolve conflicts locally and run tests/build before pushing.
- Keep PRs small and focused.
