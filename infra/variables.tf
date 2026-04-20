variable "aws_region" {
  description = "Região da AWS onde os recursos serão criados"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto para fins de organização e tags"
  type        = string
  default     = "cloud-retail-automator"
}