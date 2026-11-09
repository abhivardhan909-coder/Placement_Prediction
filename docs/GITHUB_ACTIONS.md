# GitHub Actions

The Lab 8, Lab 9, and Lab 13 workflows use a dedicated Windows self-hosted runner with the labels `self-hosted`, `Windows`, `X64`, and `placement-prediction`. The runner must be online and have Python 3.11 at `C:\Users\abhiv\AppData\Local\Programs\Python\Python311\python.exe`, Docker Desktop, and `kubectl` configured for the intended Kubernetes cluster.

## End-to-end workflow

1. **Lab 8 - MLOps CI** runs on relevant pushes, trusted same-repository pull requests, or manual dispatch. It runs the MLOps pipeline, builds the API image, checks the container health endpoint, runs pytest, and uploads its outputs.
2. **Lab 9 - Failure and Recovery Tests** runs after a successful Lab 8 run or by manual dispatch. It runs the failure-injection suite, builds and deploys the API to Kubernetes, and uploads its evidence.
3. **Lab 13 - End-to-End MLOps** runs after successful Lab 9 runs, on its schedule, or by manual dispatch. It runs the monitoring trigger, checks the deployment and in-cluster API health, and uploads monitoring evidence.

The runner creates a workspace-local `.venv` for each checked-out job. Keep the runner host and its Kubernetes context available; scheduled jobs remain queued while the runner is offline. The workflows skip pull requests from forks rather than executing untrusted code on the self-hosted machine.

## Runner registration

Register the runner from **Repository Settings → Actions → Runners**. Use a fresh registration token only with the runner's `config.cmd`; do not store the token in the repository or workflow secrets. The runner must be registered to `abhivardhan909-coder/Placement_Prediction` and have the custom `placement-prediction` label.
