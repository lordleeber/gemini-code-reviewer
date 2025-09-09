import os
import sys
import json
import requests

# --- 從 GitHub Action 傳遞的環境變數中獲取資料 ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PR_DIFF = os.environ.get("PR_DIFF")

# --- 如果必要的資料缺失，則提前退出 ---
if not GEMINI_API_KEY:
    print("錯誤：環境變數 GEMINI_API_KEY 未設定。", file=sys.stderr)
    sys.exit(1)

if not PR_DIFF or PR_DIFF == "null":
    print("沒有需要審查的程式碼差異。")
    sys.exit(0)

# --- 呼叫 Gemini API ---
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

# Prompt 現在在 Python 中管理起來更乾淨、更容易
prompt = f"""
請扮演一位資深軟體工程師的角色。請審查以下的程式碼變更(git diff 格式)，
並提供有建設性的回饋。請專注於程式碼品質、潛在的錯誤、風格一致性以及最佳實踐。
如果沒有重大問題，請確認程式碼看起來不錯。
這是程式碼的 diff 內容：

{PR_DIFF}
"""

# 使用 Python 的字典來建立 JSON payload，既安全又簡單
payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

headers = {"Content-Type": "application/json"}

try:
    # 發送 API 請求
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()  # 如果 HTTP 狀態碼是錯誤的 (4xx 或 5xx)，就拋出例外

    response_json = response.json()

    # 提取審查的內容
    review_comment = response_json["candidates"][0]["content"]["parts"][0]["text"]

    # 將最終的留言印到標準輸出 (stdout)，這樣下一個 GitHub Action 步驟才能捕捉到它
    print(review_comment)

except requests.exceptions.RequestException as e:
    print(f"錯誤：呼叫 Gemini API 失敗: {e}", file=sys.stderr)
    sys.exit(1)
except (KeyError, IndexError) as e:
    print(f"錯誤：解析 Gemini API 回應失敗: {e}", file=sys.stderr)
    # print(f"完整的 API 回應: {response.text}", file=sys.stderr)
    sys.exit(1)
