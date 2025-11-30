
resource "aws_ssm_parameter" "parameter_store" {
  name  = "/challenge/kantox"
  type  = "String"
  value = "cloud-engineer"
}
