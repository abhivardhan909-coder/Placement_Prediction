# Git workflow

The project repository is `abhivardhan909-coder/Placement_Prediction`.
Run Git commands from the repository root.

## Daily workflow

```powershell
git status
git switch -c feature/short-description
# edit and validate the changes
git add <files>
git commit -m "Describe the placement project change"
git push -u origin feature/short-description
```

Open a pull request to `main` after reviewing the diff and confirming the
test suite passes. Keep generated runtime state, credentials, virtual
environments, and local MLflow databases out of commits.

## Update the main branch

```powershell
git switch main
git pull --ff-only origin main
```

When a change is wrong after it has been shared, prefer `git revert <commit>`
to preserve history. Before pushing, verify `git status`, review
`git diff --cached`, and confirm the configured remote with `git remote -v`.
