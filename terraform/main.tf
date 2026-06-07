resource "aws_ecr_repository" "api" {
  name = "cloud-ml-genai-api"
}

resource "aws_ecs_cluster" "main" {
  name = "cloud-ml-genai-cluster"
}

resource "aws_ecs_task_definition" "api" {
  family                   = "cloud-ml-genai-api-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = "arn:aws:iam::153058521958:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::153058521958:role/cloud-ml-genai-task-role"

  container_definitions = jsonencode([])

  lifecycle {
    ignore_changes = [
      container_definitions,
      cpu,
      memory,
      execution_role_arn,
      task_role_arn
    ]
  }
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "cloud-ml-genai-worker-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = "arn:aws:iam::153058521958:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::153058521958:role/cloud-ml-genai-task-role"

  container_definitions = jsonencode([])

  lifecycle {
    ignore_changes = [
      container_definitions,
      cpu,
      memory,
      execution_role_arn,
      task_role_arn
    ]
  }
}

resource "aws_ecs_service" "api" {
  name            = "cloud-ml-genai-api-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 0

  availability_zone_rebalancing = "ENABLED"

  network_configuration {
    subnets          = ["subnet-01533c24603663304", "subnet-00bef667ea865c10f"]
    security_groups  = ["sg-0587c745516794755"]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [
      task_definition,
    ]
  }
}

resource "aws_ecs_service" "worker" {
  name            = "cloud-ml-genai-worker-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 0

  availability_zone_rebalancing = "ENABLED"

  network_configuration {
    subnets          = ["subnet-01533c24603663304", "subnet-00bef667ea865c10f"]
    security_groups  = ["sg-0587c745516794755"]
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [
      task_definition,
    ]
  }
}