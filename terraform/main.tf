resource "aws_ecr_repository" "api" {
  name = "cloud-ml-genai-api"
}

resource "aws_ecs_cluster" "main" {
  name = "cloud-ml-genai-cluster"
}