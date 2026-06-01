terraform {
  backend "s3" {
    bucket         = "cloud-ml-genai-api-proj-153058521958-us-east-1-an"
    key            = "terraform/state/cloud-ml-genai/terraform.tfstate"
    region         = "us-east-1"
    use_lockfile   = true
    encrypt        = true
  }
}