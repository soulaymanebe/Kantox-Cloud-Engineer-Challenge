module "S3" {
  source = "./modules/s3"
}

module "SSM" {
  source = "./modules/ssm"
}

module "IAM" {
  source = "./modules/iam"
}
