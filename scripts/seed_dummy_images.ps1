param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Region = "us-central1",
  [string]$Repository = "microservices",
  [string]$ServiceName = "example-service",
  [string]$Tag = "v1.0.0"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$serviceDir = Join-Path $root "sample_services\$ServiceName"
$image = "$Region-docker.pkg.dev/$ProjectId/$Repository/$ServiceName`:$Tag"

gcloud auth configure-docker "$Region-docker.pkg.dev" --quiet
docker build -t $image $serviceDir
docker push $image

Write-Host "Seeded $image"
Write-Host "Wait 5+ minutes, then run the scanner to trigger a rebuild."
