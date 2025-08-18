import os
import json
import argparse
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# --- LLMとプロンプトの定義 ---
def initialize_llm():
    """LLMを初期化する"""
    # 環境変数からAPIキーを読み込む
    if "GEMINI_API_KEY" not in os.environ:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)

# Agent 1: 脆弱性分析エージェント
analyzer_template = PromptTemplate.from_template(
    """**脆弱性分析レポート**

    **対象コード:**
    ```
    {code_snippet}
    ```

    **CodeQL警告:**
    - ファイル: {file_path}
    - 行番号: {start_line}
    - メッセージ: {message}

    **分析:**
    この脆弱性の根本原因を詳細に分析し、なぜこれがセキュリティ上の問題となるのかを説明してください。

    **フィードバック (再試行の場合):**
    {feedback}
    """
)

# Agent 2: 修正戦略立案エージェント
planner_template = PromptTemplate.from_template(
    """**修正戦略立案**

    **脆弱性分析レポート:**
    {analysis_report}

    **分析レポートに基づき、この脆弱性を修正するための具体的なステップを箇条書きで提案してください。コードは含めないでください。**
    """
)

# Agent 3: コード生成エージェント
generator_template = PromptTemplate.from_template(
    """**コード生成**

    **修正戦略:**
    {fix_strategy}

    **対象コードスニペット:**
    ```
    {code_snippet}
    ```

    **上記の戦略に従って、脆弱性を修正したコードのみを生成してください。説明や追加のテキストは不要です。**
    """
)

# Agent 4: 品質レビューエージェント
reviewer_template = PromptTemplate.from_template(
    """**品質レビュー**

    **脆弱性分析レポート:**
    {analysis_report}

    **元のコード:**
    ```
    {original_code}
    ```

    **生成された修正コード:**
    ```
    {generated_code}
    ```

    **レビュー:**
    生成されたコードは、分析レポートで指摘された問題を完全に解決していますか？
    また、新たな問題を引き起こしていませんか？

    **判定結果を `PASS` または `FAIL` で示し、`FAIL` の場合はその理由を具体的に記述してください。**
    例: `FAIL: 修正が不十分で、依然としてインジェクションの危険性があります。`
    """
)

# --- LangChainパイプラインの構築 ---
def create_agent_pipeline(llm):
    """4つのエージェントをつなげたLangChainパイプラインを構築する"""
    output_parser = StrOutputParser()

    # Agent 1: Analyzer
    analyzer_chain = analyzer_template | llm | output_parser

    # Agent 2: Planner
    planner_chain = planner_template | llm | output_parser

    # Agent 3: Generator
    generator_chain = generator_template | llm | output_parser

    # Agent 4: Reviewer
    reviewer_chain = reviewer_template | llm | output_parser

    # パイプラインの結合
    pipeline = (
        {
            "analysis_report": analyzer_chain,
            "original_code": lambda x: x["code_snippet"],
            "input_passthrough": RunnablePassthrough(),
        }
        | RunnablePassthrough.assign(
            fix_strategy=lambda x: {"analysis_report": x["analysis_report"]} | planner_chain
        )
        | RunnablePassthrough.assign(
            generated_code=lambda x: {
                "fix_strategy": x["fix_strategy"],
                "code_snippet": x["original_code"],
            }
            | generator_chain
        )
        | RunnablePassthrough.assign(
            review_result=lambda x: {
                "analysis_report": x["analysis_report"],
                "original_code": x["original_code"],
                "generated_code": x["generated_code"],
            }
            | reviewer_chain
        )
    )
    return pipeline

# --- メイン処理 ---
def main():
    parser = argparse.ArgumentParser(description="AI Agent for CodeQL Vulnerability Fix using LangChain")
    parser.add_argument("--sarif", required=True, help="Path to the SARIF file")
    parser.add_argument("--code-dir", required=True, help="Path to the source code directory")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retries for the fix loop")
    args = parser.parse_args()

    try:
        llm = initialize_llm()
        agent_pipeline = create_agent_pipeline(llm)
    except ValueError as e:
        print(f"Error: {e}")
        return

    sarif_file = Path(args.sarif)
    code_dir = Path(args.code_dir)

    if not sarif_file.is_file():
        print(f"Error: SARIF file not found at {sarif_file}")
        return

    with open(sarif_file, 'r') as f:
        sarif_data = json.load(f)

    for run in sarif_data.get("runs", []):
        for result in run.get("results", []):
            message = result.get("message", {}).get("text", "No message")
            locations = result.get("locations", [])
            if not locations:
                continue
            
            location = locations[0].get("physicalLocation", {})
            file_path = location.get("artifactLocation", {}).get("uri")
            region = location.get("region", {})
            start_line = region.get("startLine", 0)

            print(f"\n======= Processing Vulnerability: {message} in {file_path}:{start_line} =======")

            full_path = code_dir / file_path
            try:
                with open(full_path, 'r') as code_file:
                    lines = code_file.readlines()
                    code_snippet = lines[start_line - 1].strip() if start_line <= len(lines) else ""
            except Exception as e:
                print(f"Could not read file {full_path}: {e}")
                continue

            feedback = "N/A"
            for i in range(args.max_retries):
                print(f"\n--- Attempt {i + 1}/{args.max_retries} ---")

                input_data = {
                    "code_snippet": code_snippet,
                    "file_path": file_path,
                    "start_line": start_line,
                    "message": message,
                    "feedback": feedback,
                }

                # Agentパイプラインの実行
                pipeline_result = agent_pipeline.invoke(input_data)
                review_result = pipeline_result["review_result"].strip()

                print(f"Reviewer Output: {review_result}")

                if review_result.upper().startswith("PASS"):
                    print("\n[SUCCESS] Vulnerability fixed and reviewed.")
                    generated_code = pipeline_result["generated_code"]
                    print(f"Applying fix to {full_path}...")
                    # lines[start_line - 1] = generated_code + '\n' # 実際の修正適用
                    # with open(full_path, 'w') as code_file:
                    #     code_file.writelines(lines)
                    break
                else:
                    feedback = review_result # FAIL理由を次回のフィードバックとして利用
                    print(f"\n[RETRY] Review failed. Feedback for next attempt: {feedback}")
            else:
                print(f"\n[FAIL] Could not fix vulnerability after {args.max_retries} attempts.")

if __name__ == "__main__":
    main()