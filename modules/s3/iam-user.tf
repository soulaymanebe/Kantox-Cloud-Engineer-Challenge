data "aws_caller_identity" "current" {}

resource "aws_iam_user" "s3_manager" {

  name = "kantox-s3-manager"

  tags = {
    Name = "kantox-s3-manager"
  }
}

resource "aws_iam_policy" "policy" {
  name        = "S3Policy"
  description = "IAM policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:ListBucket",
          "s3:GetObject"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_user_policy_attachment" "s3_manager_policy" {
  user = aws_iam_user.s3_manager.name
  policy_arn = aws_iam_policy.policy.arn
}

resource "aws_iam_access_key" "s3_manager_access_key" {
  user = aws_iam_user.s3_manager.name
}
