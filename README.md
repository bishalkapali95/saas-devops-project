# SaaS Password-Reset DevOps Demonstration Project

> **Core DevOps Summary:**  
> *"Git controls the changes, GitHub Actions automates the pipeline, tests catch defects, Docker keeps the application environment consistent, Terraform keeps infrastructure consistent, and blue-green deployment provides a fast rollback option."*

---

## 1. Project Overview
This project is an educational demonstration developed for a **Level 5 Individual DevOps Assessment**. It demonstrates core DevOps practices using a lightweight Python Flask service implementing a **SaaS Password-Reset** workflow.

The application is intentionally kept small and clear so that every file, architectural decision, and pipeline stage can be easily understood, presented, and explained during an assessment.

---

## 2. Why the Project Exists
In software development, deploying code manually or without verification leads to frequent bugs, unexpected downtime, environment drift, and slow release cycles.

This project exists to demonstrate how modern DevOps practices solve these problems:
- **Version Control:** Tracking and isolating feature changes.
- **Automated Verification:** Catching errors before code reaches production.
- **Continuous Integration & Delivery (CI/CD):** Automating build, test, and release steps.
- **Containerisation:** Eliminating "works on my machine" discrepancies.
- **Infrastructure as Code (IaC):** Making environment setup declarative and reproducible.
- **Zero-Downtime Releases:** Mitigating deployment risk with instant rollback.

---

## 3. Application Functionality
The application is a RESTful microservice built with Flask exposing three primary endpoints:

| Method | Endpoint | Description | Expected Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint returning service status | `200 OK` |
| `POST` | `/password-reset` | Accepts an email, generates a secure 15-minute reset token | `200 OK` or `400 Bad Request` |
| `POST` | `/password-reset/validate` | Validates if a token is valid, active, and unexpired | `200 OK` (valid) or `400 Bad Request` |

### Token Rules
1. Generated using Python's cryptographically secure `secrets` library (`secrets.token_urlsafe(32)`).
2. Assigned an expiration window (15 minutes from generation).
3. Stored in memory for testing/demonstration.
4. Validation checks both existence and expiry against current UTC time.

---

## 4. Repository Structure

```text
saas-devops-project/
│
├── app/
│   ├── __init__.py           # Flask app factory, routing, and HTTP request handlers
│   └── password_reset.py     # Domain logic: token generation, validation, and in-memory store
│
├── tests/
│   ├── test_unit.py          # Isolated unit tests for token logic and edge cases
│   └── test_integration.py   # API integration tests for HTTP endpoints and workflows
│
├── terraform/
│   └── main.tf               # Infrastructure as Code demonstration with environment parameters
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # 6-stage GitHub Actions CI/CD automation workflow
│
├── Dockerfile                # Container definition based on official python:3.13-slim
├── requirements.txt          # Minimal Python dependencies (Flask, pytest, flake8)
├── .gitignore                # Rules to exclude caches, virtual environments, secrets, and TF state
└── README.md                 # Complete project documentation and operational guide
```

---

## 5. Branching Strategy
This project follows a streamlined **GitHub Flow / Feature Branching** strategy:

```text
main
  |
  +-- feature/password-reset
          |
          +-- commits (local development)
          |
          +-- pull request (triggers CI pipeline)
                  |
                  +-- automated tests & quality gates
                  |
                  +-- merge into main
                          |
                          +-- release tag (e.g., v1.0.0)
```

### Key Principles
- `main` always represents deployable, stable code.
- Developers never commit directly to `main`.
- All changes happen in dedicated feature branches (`feature/password-reset`).
- Merging into `main` requires passing automated tests and quality checks via a Pull Request.

---

## 6. Testing Strategy
Automated testing is divided into two distinct levels of the **Test Pyramid**:

1. **Unit Tests (`tests/test_unit.py`):**
   - Test individual Python functions in isolation.
   - Verify token generation, uniqueness, valid/invalid verification, and timestamp expiration.
   - Run in milliseconds without starting a web server.
2. **Integration Tests (`tests/test_integration.py`):**
   - Test the HTTP interface using Flask's built-in `test_client`.
   - Verify JSON payload parsing, HTTP status codes (`200`, `400`), error messaging, and end-to-end user journeys (request reset $\rightarrow$ receive token $\rightarrow$ validate token).

---

## 7. CI/CD Pipeline
The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automates the deployment lifecycle across 6 distinct stages:

```text
[Source] ➔ [Build] ➔ [Test] ➔ [Quality/Security] ➔ [Deploy (Blue-Green)] ➔ [Monitor]
```

1. **Source:** Checks out repository code on GitHub runner.
2. **Build:** Sets up Python 3.13 runtime, installs dependencies from `requirements.txt`, and byte-compiles code (`compileall`) to catch syntax errors.
3. **Test:** Runs `pytest -v` across all unit and integration test suites. Fails the pipeline if any test fails.
4. **Quality / Security:** Runs `flake8` static analysis to enforce code standards and scans repository for accidental secret leaks.
5. **Deploy (Blue-Green):** Validates the Docker container build and simulates switching traffic between Blue and Green environments.
6. **Monitor:** Demonstrates synthetic health checks against `/health` and records monitoring criteria.

---

## 8. Quality Gates
Quality gates prevent defective code from reaching production. In this project:
- **Build Gate:** Code must compile cleanly.
- **Test Gate:** All pytest assertions must pass with 100% success.
- **Static Analysis Gate:** `flake8` verifies syntax and cyclomatic complexity.
- **Security Gate:** Checks for hardcoded private keys or passwords before deployment.

---

## 9. Docker Containerisation
Docker packages the Python runtime, dependencies, and application into a lightweight, standalone image.

### Benefits
- **Consistency:** The same image runs identically on developer laptops, CI/CD runners, and production servers.
- **Isolation:** Application dependencies do not conflict with host machine packages.
- **Portability:** Can be deployed to any container runtime (Docker, AWS ECS, Azure App Service, etc.).

### Base Image Choice
- Uses `python:3.13-slim` to reduce image size and minimize potential security vulnerabilities.

---

## 10. Terraform / Infrastructure as Code (IaC)
Infrastructure as Code allows managing environments declaratively rather than using manual cloud consoles.

### Demonstrated Features in `terraform/main.tf`
- **Environment Parameterisation:** Uses `var.environment` to configure `dev`, `staging`, or `production`.
- **Drift Prevention:** Terraform compares the declarative state with actual provisioned resources, preventing manual, undocumented changes.
- **Safe Local Demonstration:** Uses the `hashicorp/local` provider to generate deployment configuration manifests (`generated_<env>_manifest.json`) without requiring cloud credentials or incurring costs.

---

## 11. Blue-Green Deployment Concept

### Why Blue-Green Deployment?
For a small SaaS startup, downtime during upgrades directly impacts user trust. Blue-Green deployment is chosen because:
1. **Zero Downtime:** The new version (Green) is fully deployed and tested while live users continue using the stable version (Blue).
2. **Instant Rollback:** If a defect is detected post-cutover, traffic can be redirected back to the Blue environment in seconds by switching the router/load balancer.

### Why Not Kubernetes?
Kubernetes was intentionally omitted for this project. For a small SaaS application with single-service architecture, Kubernetes adds substantial operational complexity, steep learning curves, and high infrastructure costs. A simple container runner or PaaS with Blue-Green routing provides the desired reliability without unnecessary complexity.

---

## 12. Monitoring & Observability
Post-deployment monitoring ensures ongoing service reliability:
- **Health Checks:** Periodic automated `GET /health` requests verify service uptime.
- **Application Metrics:** Tracking rates of password-reset requests and token validation successes.
- **Security Monitoring:** Alerting on high rates of failed token validation attempts (potential brute-force attacks).
- **Error Tracking:** Monitoring HTTP 5xx server errors vs 4xx client errors.

---

## 13. How to Run Locally

### Prerequisites
- Python 3.13 (accessible via `py` on Windows or `python3` on macOS/Linux).

### Step-by-Step Instructions (Windows PowerShell)

1. **Clone or navigate to the repository folder:**
   ```powershell
   cd saas-devops-project
   ```

2. **(Optional) Create and activate a virtual environment:**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   py -m pip install -r requirements.txt
   ```

4. **Run the Flask application:**
   ```powershell
   py -m flask --app app:create_app run --host=127.0.0.1 --port=5000
   ```

5. **Test the endpoints in another terminal or browser:**
   - **Health Check:**
     ```powershell
     Invoke-RestMethod -Uri http://127.0.0.1:5000/health -Method GET
     ```
   - **Request Password Reset:**
     ```powershell
     Invoke-RestMethod -Uri http://127.0.0.1:5000/password-reset -Method POST -ContentType "application/json" -Body '{"email": "student@example.com"}'
     ```
   - **Validate Password Reset Token:**
     ```powershell
     Invoke-RestMethod -Uri http://127.0.0.1:5000/password-reset/validate -Method POST -ContentType "application/json" -Body '{"token": "<PASTE_TOKEN_HERE>"}'
     ```

---

## 14. How to Run Tests

Run the full automated test suite using `pytest`:

```powershell
py -m pytest -v
```

To run unit tests only:
```powershell
py -m pytest tests/test_unit.py -v
```

To run integration tests only:
```powershell
py -m pytest tests/test_integration.py -v
```

To run code quality/linting checks:
```powershell
py -m flake8 app tests
```

---

## 15. How to Build & Run with Docker

### Prerequisites
- Docker Desktop installed and running.

### Commands

1. **Build the Docker container image:**
   ```powershell
   docker build -t saas-password-reset .
   ```

2. **Run the container:**
   ```powershell
   docker run -d -p 5000:5000 --name password-reset-app saas-password-reset
   ```

3. **Verify the container is running and healthy:**
   ```powershell
   docker ps
   Invoke-RestMethod -Uri http://127.0.0.1:5000/health -Method GET
   ```

4. **Stop and remove the container:**
   ```powershell
   docker stop password-reset-app
   docker rm password-reset-app
   ```

---

## 16. How to Run Terraform

### Prerequisites
- Terraform CLI installed (`terraform --version`).

### Commands

1. **Navigate to the terraform directory:**
   ```powershell
   cd terraform
   ```

2. **Initialise Terraform (downloads local provider):**
   ```powershell
   terraform init
   ```

3. **Plan infrastructure for development environment (default):**
   ```powershell
   terraform plan -var="environment=dev"
   ```

4. **Apply infrastructure configuration:**
   ```powershell
   terraform apply -var="environment=dev" -auto-approve
   ```

5. **Test Staging or Production configurations:**
   ```powershell
   terraform apply -var="environment=staging" -auto-approve
   terraform apply -var="environment=production" -auto-approve
   ```

6. **Clean up generated infrastructure files:**
   ```powershell
   terraform destroy -auto-approve
   cd ..
   ```

---

## 17. Git Workflow Commands (Step-by-Step)

Here are the exact PowerShell commands to initialize version control, develop on a feature branch, merge into `main`, and tag a release:

```powershell
# 1. Initialize Git repository
git init

# 2. Stage and commit the baseline project to main
git add .
git commit -m "chore: initial project structure with DevOps pipeline configuration"

# 3. Create and switch to a feature branch for password reset
git checkout -b feature/password-reset

# 4. Make code modifications or enhancements, then commit to feature branch
git add .
git commit -m "feat(auth): implement token generation and validation with automated tests"

# 5. Switch back to main branch
git checkout main

# 6. Merge feature branch into main (simulating PR merge after CI checks pass)
git merge --no-ff feature/password-reset -m "merge: pull request #1 from feature/password-reset"

# 7. Create a release tag
git tag -a v1.0.0 -m "release: v1.0.0 SaaS password reset service"

# 8. View the commit graph
git log --oneline --graph --all
```

---

## 18. Limitations of the Demonstration
To maintain educational clarity and avoid unnecessary cloud costs, the following simplifications were made:
- **In-Memory Storage:** Tokens are stored in a Python dictionary. A commercial system would use PostgreSQL or Redis with TTL.
- **Mocked Email Delivery:** Tokens are returned in the API response for demonstration purposes. In production, tokens are sent via email (AWS SES/SendGrid) and never exposed in the API response.
- **Local Terraform Provider:** Terraform manages local configuration manifests rather than AWS/Azure cloud resources to ensure zero cost and safe local execution.
- **Simulated Blue-Green Cutover:** The deployment step in GitHub Actions verifies container builds and prints orchestrator cutover logic without provisioning paid cloud load balancers.
