resource "aws_s3_bucket" "bucket" {
  bucket                      = "challenge-bucket"
  force_destroy               = true

  tags  = {
    Name                    = "challenge-bucket"
  }
}
