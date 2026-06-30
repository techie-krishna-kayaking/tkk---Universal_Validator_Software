# terraform

## Purpose
Hosts infrastructure-as-code assets for multi-cloud deployment on AWS, Azure, and GCP.

## Responsibilities
- Define reusable IaC modules and state governance.
- Provision cloud platform foundations for EKS, AKS, and GKE.
- Maintain environment wrappers and tfvars-based configuration.
- Maintain drift-detection and approval requirements.

## Ownership
Cloud Platform Engineering

## Coding Standards
- Changes SHALL align with approved architecture and SRS requirement IDs.
- Naming SHALL follow repository naming standards and semantic versioning policies.
- Security, privacy, and tenant isolation requirements SHALL be reflected in all artifacts.

## Structure
- `modules/aws`: VPC, subnet, EKS, node group, and ECR repositories.
- `modules/azure`: Resource Group, VNet/Subnet, AKS, ACR, and Log Analytics.
- `modules/gcp`: VPC/Subnet, GKE cluster and node pool, Artifact Registry.
- `environments/aws/dev`: AWS provider and module invocation.
- `environments/azure/dev`: Azure provider and module invocation.
- `environments/gcp/dev`: GCP provider and module invocation.

## Prerequisites
- Terraform `>= 1.6`
- Cloud credentials configured for target provider.

## AWS Deploy
```bash
cd terraform/environments/aws/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## Azure Deploy
```bash
cd terraform/environments/azure/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## GCP Deploy
```bash
cd terraform/environments/gcp/dev
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

## Notes
- Example tfvars contain placeholder values; replace with tenant/environment specific values.
- Managed state backends (S3/AzureRM/GCS) should be configured before production rollout.
- Keep secrets out of tfvars tracked files.
