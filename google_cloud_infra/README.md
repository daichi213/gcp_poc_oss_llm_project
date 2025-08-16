# Terraform CI/CD 設計

このドキュメントは、GitHub Actionsを利用したTerraformのインフラ管理におけるCI/CDパイプラインの設計について記述します。

## 概要

パイプラインはPull Request（PR）へのコメントによってトリガーされ、Terraformの変更に対するplanとapplyを手動で制御します。

## CIパイプライン (Terraform Plan)

- **トリガー**: ユーザーがPRに対して `/terraform plan` というコメントを投稿します。
- **アクション**:
    1.  GitHub ActionsのワークフローがPRのブランチからコードをチェックアウトします。
    2.  Workload Identity Federationを使用してGoogle Cloudに認証します。
    3.  `terraform init` と `terraform plan` を実行します。
    4.  `plan`の実行結果をキャプチャします。
- **アウトプット**: ワークフローは `terraform plan` の実行結果を、対象のPRに新しいコメントとして投稿します。これにより、レビュー担当者は提案された変更内容を確認できます。

## CDパイプライン (Terraform Apply)

- **トリガー**: ユーザーがPRに対して `/terraform apply` というコメントを投稿します。
- **アクセス制御**: セキュリティを確保するため、このワークフローの実行は制限されています。リポジトリに対して **`MEMBER`**, **`OWNER`**, または **`COLLABORATOR`** 権限を持つユーザーからのコメントでのみ実行されます。これにより、権限のないユーザーによるインフラ変更を防ぎます。
- **アクション**:
    1.  GitHub ActionsのワークフローがPRのブランチからコードをチェックアウトします。
    2.  Workload Identity Federationを介して、昇格された権限を持つ専用のサービスアカウントを使用してGoogle Cloudに認証します。
    3.  `terraform init` と `terraform apply -auto-approve` を実行します。
- **アウトプット**: ワークフローは実行結果（成功または失敗）をPRにコメントとして投稿します。

## 事前準備

これらのパイプラインを有効にするには、以下のGitHubリポジトリシークレットを設定する必要があります：

- `GCP_PROJECT_ID`: Google CloudのプロジェクトID。
- `GCP_WORKLOAD_IDENTITY_PROVIDER`: Workload Identity Providerの完全なリソース名。
- `GCP_SERVICE_ACCOUNT`: Terraformが使用するGoogle Cloudサービスアカウントのメールアドレス。
