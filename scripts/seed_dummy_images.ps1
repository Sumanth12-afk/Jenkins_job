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
$registryHost = "$Region-docker.pkg.dev"
$gcloud = "gcloud"
$defaultGcloud = Join-Path $env:LOCALAPPDATA "Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"

function Invoke-Native {
  param(
    [Parameter(Mandatory = $true)][string]$FilePath,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments
  )

  & $FilePath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Command failed with exit code $LASTEXITCODE`: $FilePath $($Arguments -join ' ')"
  }
}

if (-not (Get-Command $gcloud -ErrorAction SilentlyContinue)) {
  if (Test-Path $defaultGcloud) {
    $gcloud = $defaultGcloud
  } else {
    throw "gcloud was not found on PATH and was not found at $defaultGcloud"
  }
}

$dockerConfigPath = Join-Path $env:USERPROFILE ".docker\config.json"
if (Test-Path $dockerConfigPath) {
  $dockerConfig = Get-Content $dockerConfigPath -Raw | ConvertFrom-Json
  if ($dockerConfig.credHelpers -and $dockerConfig.credHelpers.PSObject.Properties.Name -contains $registryHost) {
    $dockerConfig.credHelpers.PSObject.Properties.Remove($registryHost)
    $json = $dockerConfig | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText($dockerConfigPath, $json, [System.Text.UTF8Encoding]::new($false))
    Write-Host "Removed Docker credential helper for $registryHost so token login can be used."
  }
}

$token = & $gcloud auth print-access-token
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($token)) {
  throw "Unable to get gcloud access token"
}

$token | docker login -u oauth2accesstoken --password-stdin "https://$registryHost"
if ($LASTEXITCODE -ne 0) {
  throw "Docker login failed"
}

Invoke-Native docker build -t $image $serviceDir
Invoke-Native docker push $image

Write-Host "Seeded $image"
Write-Host "Wait 5+ minutes, then run the scanner to trigger a rebuild."
