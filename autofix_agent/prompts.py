FIX_PROMPT_TEMPLATE = """
あなたは、コードの脆弱性を修正するエキスパートセキュリティプログラマです。
以下の脆弱性情報とコードスニペットをレビューしてください。

## 脆弱性の詳細
- **ルールID**: {rule_id}
- **説明**: {vulnerability_message}

## 脆弱性を含むコード
```
{code_snippet}
```

## あなたのタスク
上記の脆弱性を修正するための、安全で効率的なコードを提案してください。

## 指示
- 修正後の完全なコードブロックのみを返してください。
- 元のコードのインデントとスタイルは、可能な限り維持してください。
- 説明や前置きは一切含めず、修正後のコードだけをMarkdown形式のコードブロックで出力してください。

例:
```python
def fixed_function(user_input):
    # 安全なコード実装
    sanitized_input = sanitize(user_input)
    return execute_query(sanitized_input)
```
"""
