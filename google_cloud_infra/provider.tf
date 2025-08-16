terraform {
  backend "gcs" {
    bucket = "<YOUR_TERRAFORM_STATE_BUCKET_NAME>" # 事前に作成したGCSバケット名を指定してください
    prefix = "terraform/state"
  }
}
