# Zenflow — GCP deployment (Cloud Run)

Provisions Artifact Registry + two Cloud Run services (frontend, backend) for
Zenflow. State is local (`terraform.tfstate` in this directory) — fine for a
solo test deployment; see "Moving to remote state" below when you outgrow that.

## CI/CD

[.github/workflows/deploy.yml](../.github/workflows/deploy.yml) redeploys both
services on every push to `main` (i.e. on merge), authenticating to GCP via
Workload Identity Federation (pool `github-pool`, provider `github-provider`,
service account `github-actions-deployer@zenflow-506701.iam.gserviceaccount.com`
— no long-lived key stored in GitHub). It builds and pushes images tagged with
the commit SHA and calls `gcloud run deploy` directly, **not** `terraform
apply` — this repo's Terraform state contains load-balancer resources
(`google_compute_*`) that aren't defined in any `.tf` file here, so an
untargeted `apply` from a fresh CI runner would try to destroy them.

This means `terraform apply` (run manually, per the flow below) and the CI
pipeline both update the same Cloud Run services out-of-band from each other.
If you run a manual `apply` without passing the current `backend_image`/
`frontend_image`, it will roll the service back to whatever tag is in
`terraform.tfvars` — always check `gcloud run services describe` for the
currently-live image first.

## Why this is a multi-step apply

The frontend is a static-exported client app: `NEXT_PUBLIC_API_BASE_URL` gets
compiled into the JS bundle at `next build` time, not read at container
runtime. That means the backend's Cloud Run URL must exist *before* you build
the frontend image. Terraform can't sequence "build a Docker image" as part of
its graph, so this is a scripted multi-step flow, not a single `apply`.

## Prerequisites

- `gcloud` CLI, authenticated (`gcloud auth login`) with a configured project
- Docker
- `gcloud auth configure-docker <region>-docker.pkg.dev`

## One-time setup

```sh
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars: set project_id (and region if not us-central1)
terraform init
```

## Deploy flow

1. **Create the registry** (backend/frontend images don't exist yet, so target
   just this):

   ```sh
   terraform apply -target=google_project_service.apis \
                    -target=google_artifact_registry_repository.zenflow
   ```

2. **Build and push the backend image**, then deploy it:

   ```sh
   REGISTRY=$(terraform output -raw artifact_registry_repository)
   docker build -t "$REGISTRY/backend:v1" ../backend
   docker push "$REGISTRY/backend:v1"

   terraform apply -var="backend_image=$REGISTRY/backend:v1" \
                    -target=google_cloud_run_v2_service.backend \
                    -target=google_cloud_run_v2_service_iam_member.backend_public
   ```

3. **Build and push the frontend image**, baking in the backend's URL:

   ```sh
   BACKEND_URL=$(terraform output -raw backend_url)
   docker build \
     --build-arg NEXT_PUBLIC_API_BASE_URL="$BACKEND_URL" \
     -t "$REGISTRY/frontend:v1" ../frontend
   docker push "$REGISTRY/frontend:v1"
   ```

4. **Deploy the frontend** (full apply now that both images/vars are known —
   put `backend_image` and `frontend_image` in `terraform.tfvars` at this point
   to avoid retyping `-var` flags):

   ```sh
   terraform apply -var="backend_image=$REGISTRY/backend:v1" \
                    -var="frontend_image=$REGISTRY/frontend:v1"
   ```

5. Open `terraform output frontend_url`.

## Redeploying after a code change

Repeat step 2 or 3 with a new tag (`:v2`, etc.) — Cloud Run image references
must change for `terraform apply` to roll a new revision.

## Current security posture (intentionally open for testing)

- Both services are public (`allUsers` / `roles/run.invoker`) — no auth in
  front of either one.
- Backend CORS (`backend/src/zenflow/routers/app.py`) allows `allow_origins=["*"]`.

Before this goes in front of real users:

- Narrow backend CORS to the actual `frontend_url`.
- Consider whether the backend needs to be reachable directly from the
  internet at all, or only from the frontend service (e.g. via
  `ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"` plus a serverless VPC
  connector, or Cloud Run's built-in service-to-service auth with
  `roles/run.invoker` scoped to the frontend's service account instead of
  `allUsers`).

## Moving to remote state

Create a GCS bucket, then add to `versions.tf`:

```hcl
terraform {
  backend "gcs" {
    bucket = "your-tfstate-bucket"
    prefix = "zenflow"
  }
}
```

Run `terraform init -migrate-state` afterward.
