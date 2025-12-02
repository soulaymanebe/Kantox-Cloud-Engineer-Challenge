# Kantox Cloud Engineer Challenge

This project demonstrates a complete cloud-native architecture featuring two Python Flask microservices (`main-api` and `aux-service`) deployed on a k3s Kubernetes cluster, managed through Argo CD, and integrated with AWS services including S3 and Systems Manager Parameter Store.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Terraform Infrastructure](#terraform-infrastructure)
- [CI/CD Pipeline](#cicd-pipeline)
- [Kubernetes Deployment](#kubernetes-deployment)
- [API Testing Guide](#api-testing-guide)
- [Monitoring](#monitoring)

---

## Architecture Overview

```
┌─────────────────┐
│  GitHub Actions │
│    (CI/CD)      │
└────────┬────────┘
         │
         ├──► AWS ECR (Container Registry)
         └──► Git Repository (Manifest Updates)
                    │
                    ▼
         ┌──────────────────┐
         │    Argo CD       │
         │  (GitOps Tool)   │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  k3s Kubernetes  │
         │     Cluster      │
         └────────┬─────────┘
                  │
         ┌────────┴─────────┐
         │                  │
    ┌────▼─────┐      ┌────▼──────┐
    │ main-api │      │aux-service│
    └────┬─────┘      └─────┬─────┘
         │                  │
         └─────────┬────────┘
                   │
         ┌─────────▼──────────┐
         │   AWS Services     │
         ├────────────────────┤
         │ • S3 Bucket        │
         │ • Parameter Store  │
         │ • IAM Roles        │
         └────────────────────┘
```

---

## Terraform Infrastructure

Terraform manages all AWS resources required for the application.

### `iam/main.tf`

**Purpose:** Configures secure GitHub Actions authentication using OIDC (OpenID Connect).

**Resources:**
- `aws_iam_openid_connect_provider.github` – Registers GitHub as a trusted OIDC identity provider
- `data.aws_iam_policy_document.github_oidc_assume_role` – Defines trust relationship for GitHub Actions
- `aws_iam_role.github_oidc_role` – IAM role assumed by GitHub Actions workflows
- `aws_iam_role_policy.github_oidc_policy` – Grants necessary AWS permissions.

### `s3/main.tf`

**Purpose:** Provisions object storage for application artifacts.

**Resources:**
- `aws_s3_bucket.bucket` – Creates bucket `kantox-challenge-bucket`

### `ssm/main.tf`

**Purpose:** Stores application configuration securely using AWS Systems Manager.

**Resources:**
- `aws_ssm_parameter.parameter_store` – String parameter at `/challenge/kantox` with value `cloud-engineer`

### Deploy Infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## CI/CD Pipeline

The GitHub Actions workflow automates the entire deployment process.

### Workflow Steps

```yaml
┌─────────────────────────────────────────────────────────┐
│ Job: build-and-push                                     │
├─────────────────────────────────────────────────────────┤
│ 1. Init repository                                      │
│ 2. Extract short commit SHA                             │
│ 3. Configure AWS credentials via OIDC                   │
│ 4. Login to AWS ECR                                     │
│ 5. Build Docker images:                                 │
│    • aux-service                                        │
│    • main-api                                           │
│ 6. Tag images:                                          │
│    • <service>-latest                                   │
│    • <service>-<sha>                                    │
│ 7. Push images to ECR                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Job: update-manifests                                   │
├─────────────────────────────────────────────────────────┤
│ 1. Checkout repository                                  │
│ 2. Update Kubernetes manifests with new image tags      │
│ 3. Commit changes with SHA reference                    │
│ 4. Push to GitHub (triggers Argo CD sync)               │
└─────────────────────────────────────────────────────────┘
```

### Image Tagging Strategy

Each build produces two tags per service:

| Tag Format            | Example                | Purpose                            |
|-----------------------|------------------------|------------------------------------|
| `<service>-latest`    | `aux-service-latest`   | Development/testing environments   |
| `<service>-<sha>`     | `aux-service-20aba86`  | Production deployments (immutable) |

---

## Kubernetes Deployment

### Argo CD Setup

#### 1. Install Argo CD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### 2. Retrieve Admin Password

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```

#### 3. Expose Argo CD UI

```bash
# Change service type to NodePort
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'

# Get the NodePort
kubectl get svc argocd-server -n argocd
```

#### 4. Access Argo CD

Navigate to `https://<node-ip>:<nodeport>` in your browser.

**Credentials:**
- **Username:** `admin`
- **Password:** Output from step 2

### Deploy Application

Connect argocd with my github account using a personal access tocken (using the argocd UI).
Create an Argo CD Application resource:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: kantox-challenge-app
  namespace: argocd
spec:
  project: default
  
  source:
    repoURL: https://github.com/soulaymanebe/Kantox-Cloud-Engineer-Challenge.git
    targetRevision: HEAD
    path: kubernetes/
  
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Verify Deployment

```bash
# Check application status
kubectl get applications -n argocd

# View deployed pods
kubectl get pods

# Check services
kubectl get svc

# View deployment details
kubectl describe deployment main-api
kubectl describe deployment aux-service
```

**Expected Output:**

```
NAME             READY   STATUS    RESTARTS   AGE
main-api-xxx     1/1     Running   0          2m
aux-service-xxx  1/1     Running   0          2m
```

---

## API Testing Guide

### Aux Service Endpoints

**Base URL:** `http://<node-ip>:30001`

#### List All S3 Buckets

```bash
curl http://<node-ip>:30001/buckets
```

**Response:**
```json
{
  "version": "0.0.1",
  "buckets": [
    "kantox-challenge-bucket"
  ]
}
```

#### List All SSM Parameters

```bash
curl http://<node-ip>:30001/params
```

**Response:**
```json
{
  "version": "0.0.1",
  "parameters": [
    "/challenge/kantox"
  ]
}
```

#### Get Specific Parameter

```bash
curl http://<node-ip>:30001/param/challenge/kantox
```

**Response:**
```json
{
  "version": "0.0.1",
  "value": "cloud-engineer"
}
```

---

### Main API Endpoints

**Base URL:** `http://<node-ip>:30002`

The Main API aggregates responses from the Aux Service and includes version information from both services.

#### List All Buckets (Aggregated)

```bash
curl http://<node-ip>:30002/buckets
```

**Response:**
```json
{
  "main_version": "0.0.1",
  "aux_version": "0.0.1",
  "buckets": [
    "kantox-challenge-bucket"
  ]
}
```

#### List All Parameters (Aggregated)

```bash
curl http://<node-ip>:30002/params
```

**Response:**
```json
{
  "main_version": "0.0.1",
  "aux_version": "0.0.1",
  "parameters": [
    "/challenge/kantox"
  ]
}
```

#### Get Specific Parameter (Aggregated)

```bash
curl http://<node-ip>:30002/param/challenge/kantox
```

**Response:**
```json
{
  "main_version": "0.0.1",
  "aux_version": "0.0.1",
  "value": "cloud-engineer"
}
```

---

## Additional Notes

### Port Mappings

| Service       | Internal Port | NodePort | Purpose              |
|---------------|---------------|----------|----------------------|
| `aux-service` | 5000          | 30001    | AWS resource queries |
| `main-api`    | 6000          | 30002    | Aggregation layer    |

## Acknowledgments

- **Kantox** for the challenge opportunity
- **Argo CD** for GitOps automation
- **k3s** for lightweight Kubernetes
- **AWS** for cloud infrastructure

---

## Monitoring
