import os
import json
import sys
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# prompts.pyからプロンプトテンプレートをインポート
from prompts import FIX_PROMPT_TEMPLATE


def get_vulnerability_details(sarif_file_path):
    """
    SARIFファイルを解析し、脆弱性の詳細を抽出する。
    簡単のため、最初の結果のみを処理する。
    """
    try:
        with open(sarif_file_path, 'r') as f:
            sarif_data = json.load(f)

        if not sarif_data["runs"] or not sarif_data["runs"][0]["results"]:
            print("脆弱性が見つかりませんでした。")
            return None

        result = sarif_data["runs"][0]["results"][0]
        message = result["message"]["text"]
        rule_id = result["ruleId"]

        # GitHub Actionsのワークスペースからの相対パスに変換
        location_uri = result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        location = Path(os.environ.get("GITHUB_WORKSPACE", ".")) / location_uri

        start_line = result["locations"][0]["physicalLocation"]["region"]["startLine"]

        return {
            "message": message,
            "rule_id": rule_id,
            "location": str(location),
            "start_line": start_line,
        }
    except (FileNotFoundError, IndexError, KeyError) as e:
        print(f"SARIFファイルの解析中にエラーが発生しました: {e}", file=sys.stderr)
        return None

def get_code_snippet(file_path, start_line, context_lines=40):
    """
    脆弱性が検出された箇所の前後のコードを取得する。
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        start = max(0, start_line - (context_lines // 2))
        end = min(len(lines), start_line + (context_lines // 2))

        snippet = "".join(lines[start:end])
        # 行番号を付けてわかりやすくする
        numbered_snippet = "".join(f"{i+1:4d}: {line}" for i, line in enumerate(lines[start:end], start=start))
        return numbered_snippet
    except FileNotFoundError:
        print(f"対象ファイルが見つかりません: {file_path}", file=sys.stderr)
        return None

def generate_fix_suggestion(vulnerability_info, code_snippet):
    """
    LangChainとGeminiモデルを使って修正案を生成する。
    """
    print("AIによる修正案を生成中...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("環境変数 GEMINI_API_KEY が設定されていません。", file=sys.stderr)
        sys.exit(1)

    # LLMのセットアップ
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)

    # プロンプトテンプレートの準備
    prompt = PromptTemplate.from_template(FIX_PROMPT_TEMPLATE)

    # LangChainチェーンの構築
    chain = prompt | llm | StrOutputParser()

    # チェーンを実行して修正案を生成
    suggestion = chain.invoke({
        "rule_id": vulnerability_info["rule_id"],
        "vulnerability_message": vulnerability_info["message"],
        "code_snippet": code_snippet
    })

    return suggestion

def main():
    """
    メインの処理フロー
    1. SARIFファイルパスを環境変数から取得
    2. 脆弱性情報を抽出
    3. 対象コードを取得
    4. 修正案を生成
    5. 修正案をファイルに出力 (GitHub Actionsで利用)
    """
    sarif_path = os.environ.get("SARIF_FILE_PATH")
    if not sarif_path:
        print("環境変数 SARIF_FILE_PATH が設定されていません。", file=sys.stderr)
        sys.exit(1)

    print(f"処理中のSARIFファイル: {sarif_path}")
    vuln_details = get_vulnerability_details(sarif_path)

    if vuln_details:
        print(f"脆弱性を検出しました: {vuln_details['message']} in {vuln_details['location']}:{vuln_details['start_line']}")
        code_snippet = get_code_snippet(vuln_details["location"], vuln_details["start_line"])

        if code_snippet:
            suggestion = generate_fix_suggestion(vuln_details, code_snippet)

            # PRコメント用のヘッダーを追加
            header = (
                "🤖 **AIによる脆弱性修正案**\n\n"
                f"CodeQLが `{vuln_details['rule_id']}` の問題を `{vuln_details['location']}` で検出しました。\n"
                "以下に修正案を提案します。\n\n"
            )
            final_output = header + suggestion

            print("\n--- 提案された修正 ---")
            print(final_output)

            with open("suggestion.txt", "w") as f:
                f.write(final_output)
            print("\n修正案を suggestion.txt に保存しました。")

if __name__ == "__main__":
    main()
