terraform {
  backend "gcs" {
    bucket = "terraform_poc_closed_llm" # 事前に作成したGCSバケット名を指定してください
    key = "root/default.tfstate"
  }
}
