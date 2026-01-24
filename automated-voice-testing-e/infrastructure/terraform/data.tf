############################################################
# Data layer: PostgreSQL (RDS) and Redis (ElastiCache)
############################################################

resource "aws_security_group" "db" {
  name        = "${local.name_prefix}-db-sg"
  description = "Allow PostgreSQL access from application services."
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Allow PostgreSQL traffic from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-db-sg"
      Tier = "data"
    }
  )
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = [for subnet in aws_subnet.private : subnet.id]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-db-subnets"
    }
  )
}

resource "aws_db_instance" "main" {
  identifier                 = "${local.name_prefix}-postgres"
  allocated_storage          = var.db_allocated_storage
  engine                     = "postgres"
  engine_version             = "15.4"
  instance_class             = var.db_instance_class
  db_name                    = var.db_name
  username                   = var.db_username
  password                   = var.db_password
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = [aws_security_group.db.id]
  multi_az                   = var.db_multi_az
  backup_retention_period    = var.db_backup_retention_period
  storage_encrypted          = true
  deletion_protection        = false
  skip_final_snapshot        = true
  publicly_accessible        = false
  apply_immediately          = true
  auto_minor_version_upgrade = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-postgres"
      Tier = "data"
    }
  )
}

resource "aws_security_group" "redis" {
  name        = "${local.name_prefix}-redis-sg"
  description = "Allow Redis access from application services."
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Allow Redis traffic from ECS tasks"
    from_port       = var.redis_port
    to_port         = var.redis_port
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis-sg"
      Tier = "cache"
    }
  )
}

resource "aws_elasticache_subnet_group" "main" {
  name       = "${local.name_prefix}-redis-subnets"
  subnet_ids = [for subnet in aws_subnet.private : subnet.id]

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis-subnets"
    }
  )
}

resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${local.name_prefix}-redis"
  description                = "Redis replication group for ${local.name_prefix}"
  engine                     = "redis"
  engine_version             = var.redis_engine_version
  node_type                  = var.redis_node_type
  port                       = var.redis_port
  automatic_failover_enabled = true
  multi_az_enabled           = true
  num_node_groups            = 1
  replicas_per_node_group    = 1
  subnet_group_name          = aws_elasticache_subnet_group.main.name
  security_group_ids         = [aws_security_group.redis.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = false
  apply_immediately          = true

  tags = merge(
    local.common_tags,
    {
      Name = "${local.name_prefix}-redis"
      Tier = "cache"
    }
  )
}
