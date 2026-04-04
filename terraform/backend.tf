terraform {
  backend "s3" {
    bucket  = "platform-api-terraform-state-richard-1"
    key     = "platform-self-service-api/dev/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}