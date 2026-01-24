############################################################
# Compute: ECS Fargate services and load balancing
############################################################

resource "aws_cloudwatch_log_group" "app" {
  name              = local.log_group_name
  retention_in_days = 30

  tags = merge(
    local.common_tags,
    {
      Name = local.log_group_name
    }
  )
}

data "aws_iam_policy_document" "ecs_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name_prefix}-ecs-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecs-exec"
    }
  )
}

resource "aws_iam_role" "ecs_task" {
  name               = "${local.name_prefix}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role.json

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-ecs-task"
    }
  )
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "ecs_task_cloudwatch" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

resource "aws_ecs_cluster" "main" {
  name = local.ecs_cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(
    local.common_tags,
    {
      Name = local.ecs_cluster_name
    }
  )
}

resource "aws_lb" "app" {
  name               = "${local.name_prefix}-alb"
  internal           = var.alb_internal
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-alb"
    }
  )
}

resource "aws_lb_target_group" "tg" {
  name        = "${local.name_prefix}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    enabled             = true
    interval            = 30
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 5
    matcher             = "200-399"
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-tg"
    }
  )
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${local.name_prefix}-task"
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = local.container_name
      image     = var.app_image
      essential = true
      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "PROJECT"
          value = var.project
        }
      ]
    }
  ])

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-task"
    }
  )
}

resource "aws_ecs_service" "app" {
  name             = "${local.name_prefix}-service"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.app.arn
  desired_count    = var.desired_task_count
  launch_type      = "FARGATE"
  platform_version = "LATEST"

  network_configuration {
    subnets          = [for subnet in aws_subnet.private : subnet.id]
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name   = local.container_name
    container_port   = var.container_port
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  depends_on = [
    aws_lb_listener.http
  ]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-service"
    }
  )
}

resource "aws_appautoscaling_target" "ecs_service" {
  count = var.enable_ecs_autoscaling ? 1 : 0

  max_capacity       = var.ecs_autoscaling_max_capacity
  min_capacity       = var.ecs_autoscaling_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [
    aws_ecs_service.app
  ]
}

resource "aws_appautoscaling_policy" "ecs_service_cpu" {
  count = var.enable_ecs_autoscaling ? 1 : 0

  name               = "${local.name_prefix}-ecs-cpu"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_service[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_service[count.index].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_service[count.index].service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = var.ecs_autoscaling_target_cpu_utilization

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_in_cooldown  = 60
    scale_out_cooldown = 60
  }
}
