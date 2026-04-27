module "apis" {
  source     = "./modules/apis"
  project_id = var.project_id
}

module "network" {
  source = "./modules/network"

  project_id                    = var.project_id
  region                        = var.region
  network_name                  = var.network_name
  subnet_name                   = var.subnet_name
  subnet_cidr                   = var.subnet_cidr
  jenkins_allowed_source_ranges = var.jenkins_allowed_source_ranges

  depends_on = [module.apis]
}

module "artifact_registry" {
  source = "./modules/artifact_registry"

  project_id    = var.project_id
  location      = var.region
  repository_id = var.artifact_registry_repo

  depends_on = [module.apis]
}

module "firestore" {
  source = "./modules/firestore"

  project_id  = var.project_id
  location_id = var.firestore_location

  depends_on = [module.apis]
}

module "iam" {
  source = "./modules/iam"

  project_id               = var.project_id
  github_service_account   = var.github_service_account
  jenkins_service_account  = var.jenkins_service_account
  artifact_registry_reader = true
  artifact_registry_writer = true
}

module "github_oidc" {
  source = "./modules/github_oidc"

  project_id                  = var.project_id
  project_number              = var.project_number
  pool_id                     = var.github_oidc_pool_id
  provider_id                 = var.github_oidc_provider_id
  github_repo                 = var.github_repo
  github_service_account_name = module.iam.github_service_account_name

  depends_on = [module.apis]
}

module "jenkins_vm" {
  source = "./modules/jenkins_vm"

  project_id             = var.project_id
  region                 = var.region
  zone                   = var.zone
  vm_name                = var.jenkins_vm_name
  machine_type           = var.jenkins_machine_type
  network_self_link      = module.network.network_self_link
  subnet_self_link       = module.network.subnet_self_link
  service_account_email  = module.iam.jenkins_service_account_email
  artifact_registry_repo = module.artifact_registry.repository_id

  depends_on = [module.apis, module.network, module.iam, module.artifact_registry]
}
