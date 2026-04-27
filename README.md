# CI/CD Image Rebuild Automation System

Automates the 45-day golden-image rebuild policy for GCP-hosted microservices.

## Local Test Flow

```powershell
python -m pip install --target .deps -r requirements.txt
$env:PYTHONPATH=".deps"
python -m pytest -q
python -m src.core.scanner --dry-run
```

Dry-run mode evaluates image policy and logs intended Jenkins actions without triggering builds, writing state, or sending email.

## Production Flow

GitHub Actions authenticates to GCP with Workload Identity Federation using:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `GCP_PROJECT_ID`

The scanner reads `config/services.yaml`, evaluates Artifact Registry image versions, and triggers Jenkins for stale services with:

- `JENKINS_URL`
- `JENKINS_USER`
- `JENKINS_API_TOKEN`

Jenkins should call the Cloud Function webhook with build completion metadata. The webhook updates Firestore and sends QA rebuild tags using:

- `EMAIL_API_KEY`
- `QA_TEAM_EMAIL`

## Idempotency

Each rebuild uses an idempotency key:

```text
service_name:current_tag:new_tag
```

The scanner skips any existing `QUEUED`, `RUNNING`, `PENDING`, `SUCCESS`, or `UNSTABLE` record for the same key. `FAILURE` and `ABORTED` records may be retried.

## Terraform GCP Test Environment

The Terraform stack creates:

- GCP APIs
- Artifact Registry Docker repository
- Firestore Native database
- GitHub Actions Workload Identity Federation
- GitHub and Jenkins service accounts
- VPC, subnet, Jenkins firewall rules
- Jenkins VM with Java, Jenkins LTS, Docker, and Google Cloud CLI

### 1. Bootstrap Remote State Bucket

GCS remote state supports Terraform state locking and versioning. The bucket must exist before the main backend is initialized.

```powershell
cd terraform/state-bootstrap
terraform init
terraform apply `
  -var="project_id=YOUR_PROJECT_ID" `
  -var="region=us-central1" `
  -var="bucket_name=YOUR_UNIQUE_TF_STATE_BUCKET"
```

### 2. Configure Dev Variables

```powershell
Copy-Item terraform/envs/dev.tfvars.example terraform/envs/dev.tfvars
```

Edit `terraform/envs/dev.tfvars`:

```hcl
project_id     = "your-gcp-project-id"
project_number = "123456789012"
region         = "us-central1"
zone           = "us-central1-a"
github_repo    = "your-org/your-repo"

jenkins_allowed_source_ranges = [
  "YOUR_PUBLIC_IP/32"
]
```

### 3. Apply Main Infrastructure

```powershell
cd terraform
terraform init `
  -backend-config="backend.dev.hcl"

terraform plan -var-file="envs/dev.tfvars"
terraform apply -var-file="envs/dev.tfvars"
```

Save these outputs into GitHub Actions secrets:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `GCP_PROJECT_ID`
- `JENKINS_URL`

After Jenkins setup, also add:

- `JENKINS_USER`
- `JENKINS_API_TOKEN`

### 4. Seed Dummy Image

Artifact Registry stores image tags; it does not run containers. For this POC, the seed script builds and pushes a dummy Docker image tagged `v1.0.0`.

```powershell
.\scripts\seed_dummy_images.ps1 `
  -ProjectId "YOUR_PROJECT_ID" `
  -Region "us-central1" `
  -Repository "microservices" `
  -ServiceName "example-service" `
  -Tag "v1.0.0"
```

Wait at least 5 minutes. The test policy in `config/thresholds.yaml` marks images stale after `max_image_age_minutes: 5`.

### 5. Configure Jenkins Job

Open the Terraform output `jenkins_url`, unlock Jenkins, and create a parameterized Pipeline job:

```text
image-rebuild/example-service
```

Use [jenkins/Jenkinsfile.image-rebuild](C:/Users/nalla/OneDrive/Documents/codex_jenkins_job/jenkins/Jenkinsfile.image-rebuild) as the pipeline script. The Jenkins VM service account has Artifact Registry read/write permissions, so the job can rebuild and push tags.

### 6. Run Scanner

Dry-run first:

```powershell
$env:GCP_PROJECT_ID="YOUR_PROJECT_ID"
$env:JENKINS_URL="http://JENKINS_EXTERNAL_IP:8080"
$env:JENKINS_USER="YOUR_JENKINS_USER"
$env:JENKINS_API_TOKEN="YOUR_JENKINS_TOKEN"

python -m src.core.scanner --dry-run --use-firestore
```

Then trigger the real Jenkins rebuild:

```powershell
python -m src.core.scanner --use-firestore
```

When the POC is done, change `config/thresholds.yaml` back to the production policy by removing `max_image_age_minutes` and using:

```yaml
max_image_age_days: 45
```
