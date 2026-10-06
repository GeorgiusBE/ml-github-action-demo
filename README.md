# ML GitHub Actions Demo

A deliberately small but realistic MLOps exercise for learning GitHub Actions hands-on.

The repository trains a binary classification model using scikit-learn's built-in breast-cancer dataset. The dataset ships with scikit-learn, so the CI runner does not need to download a dataset from the internet.

## What this project teaches

When you push to `main` or open a pull request targeting `main`, GitHub Actions will:

1. Create a fresh Ubuntu runner.
2. Check out your repository.
3. Install Python 3.12.
4. Install project dependencies.
5. Run unit tests with `pytest`.
6. Only if tests pass, run a second job.
7. Train the ML model.
8. Save `model.joblib` and `metrics.json`.
9. Fail the workflow if model accuracy is below 95%.
10. Upload the trained model and metrics as a GitHub Actions artifact.

This represents a simplified version of a real ML CI pipeline:

```text
Git push / Pull Request
          |
          v
    GitHub Actions
          |
          v
       pytest
          |
      tests pass?
       /      \
     no        yes
     |          |
   FAIL         v
            train model
                |
                v
          evaluate model
                |
           accuracy >= 95%?
             /        \
           no          yes
           |            |
         FAIL           v
                  upload artifacts
```

## Repository structure

```text
ml-github-actions-demo/
├── .github/
│   └── workflows/
│       └── ml-ci.yml
├── artifacts/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── train.py
│   ├── check_metrics.py
│   └── predict.py
├── tests/
│   └── test_train.py
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Run it locally first

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest -v
```

Using `python -m` runs pip and pytest with the selected Python interpreter.
After activating `.venv`, `python -c "import sys; print(sys.executable)"` should
show a path ending in `.venv\Scripts\python.exe` on Windows. The `pytest.ini`
configuration adds the project root to the import path so tests can import `src`.

Train the model:

```bash
python src/train.py
```

You should now have:

```text
artifacts/model.joblib
artifacts/metrics.json
```

Run the same quality gate used by CI:

```bash
python src/check_metrics.py --threshold 0.95
```

Try inference:

```bash
python src/predict.py
```

## Put it on GitHub

Create an empty repository on GitHub, then from this project directory run something like:

```bash
git init
git add .
git commit -m "Add ML GitHub Actions demo"
git branch -M main
git remote add origin <YOUR-GITHUB-REPOSITORY-URL>
git push -u origin main
```

Then open your repository's **Actions** tab. You should see the `ML CI` workflow run.

## Understand the workflow

### Trigger

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

The workflow runs when:

- code is pushed to `main`;
- a pull request targets `main`; or
- you manually click **Run workflow** in GitHub.

### Job 1: test

The `test` job installs the environment and runs:

```bash
python -m pytest -v
```

If a test fails, the workflow stops before model training.

### Job 2: train-and-evaluate

This job contains:

```yaml
needs: test
```

That means GitHub does not start it until `test` succeeds.

It then executes:

```bash
python src/train.py
python src/check_metrics.py --threshold 0.95
```

The second command acts as a model-quality gate.

### Artifact upload

At the end of the successful workflow, GitHub uploads:

```text
model.joblib
metrics.json
```

Open the completed workflow run in GitHub and look for its **Artifacts** section.

## Hands-on experiments

Do these in order rather than merely reading the YAML.

### Experiment 1 — deliberately break a unit test

Change this assertion in `tests/test_train.py`:

```python
assert metrics["accuracy"] >= 0.95
```

to:

```python
assert metrics["accuracy"] >= 0.9999
```

Commit and push. Watch the `test` job fail. Notice that `train-and-evaluate` does not run because it has `needs: test`.

Then revert the change.

### Experiment 2 — fail the ML quality gate

In `.github/workflows/ml-ci.yml`, change:

```yaml
python src/check_metrics.py --threshold 0.95
```

to:

```yaml
python src/check_metrics.py --threshold 0.9999
```

Push again. This time the unit tests should pass and training should run, but CI should fail at the model-quality gate.

That distinction is important in ML engineering: valid code does not necessarily mean an acceptable model.

### Experiment 3 — use a feature branch and pull request

```bash
git switch -c feature/change-model
```

Change the classifier or a model parameter, then:

```bash
git add .
git commit -m "Experiment with model configuration"
git push -u origin feature/change-model
```

Create a pull request into `main`.

Your workflow should run because of:

```yaml
pull_request:
  branches: [main]
```

This is how CI and pull requests normally work together.

### Experiment 4 — add branch protection

After the workflow has successfully run at least once, configure a GitHub ruleset / branch protection rule for `main` and require the workflow's status check before merging.

Your flow becomes:

```text
feature branch
      |
      v
Pull Request
      |
      v
GitHub Actions
      |
 tests + model checks
      |
      v
 merge permitted
      |
      v
     main
```

## Why the model artifact is ignored by Git

`.gitignore` contains:

```text
artifacts/*
!artifacts/.gitkeep
```

We normally do not want generated binary model files committed on every training run. The CI system generates them and stores them as workflow artifacts instead.

In a more advanced project, the artifact might instead go to a model registry such as MLflow, Azure ML, SageMaker, or another dedicated model store.

## What to add next

Once this basic project makes sense, natural upgrades are:

```text
Stage 1  GitHub Actions + pytest
Stage 2  Add linting (Ruff)
Stage 3  Add model-quality/data-quality checks
Stage 4  Add Docker
Stage 5  Build Docker image in GitHub Actions
Stage 6  Push image to a container registry
Stage 7  Deploy to Kubernetes/KServe
Stage 8  Add DVC or MLflow for data/model experiment management
Stage 9  Use Argo CD for GitOps deployment
```

Do not add everything at once. The point of this repository is to make the GitHub Actions execution model obvious first.
