import os
import sys
import json
import requests

# --- 從 GitHub Action 傳遞的環境變數中獲取 API Key ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DIFF_FILE_PATH = "pr_diff.txt" # 定義要讀取的檔案路徑

# --- 如果 API Key 缺失，則提前退出 ---
if not GEMINI_API_KEY:
    print("錯誤：環境變數 GEMINI_API_KEY 未設定。", file=sys.stderr)
    sys.exit(1)

# --- 從檔案中讀取 diff 內容 ---
try:
    with open(DIFF_FILE_PATH, "r", encoding="utf-8") as f:
        PR_DIFF = f.read()
except FileNotFoundError:
    print(f"錯誤：找不到 diff 檔案 {DIFF_FILE_PATH}", file=sys.stderr)
    sys.exit(1)

if not PR_DIFF:
    print("Diff 檔案是空的，沒有需要審查的內容。", file=sys.stderr)
    sys.exit(0) # 正常退出

# --- 呼叫 Gemini API ---
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

prompt = f"""
請扮演一位資深軟體工程師的角色。請審查以下的程式碼變更(git diff 格式)，
並提供有建設性的回饋。請專注於程式碼品質、潛在的錯誤、風格一致性以及最佳實踐。
如果沒有重大問題，請確認程式碼看起來不錯。
這是程式碼的 diff 內容：

{PR_DIFF}
"""

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    response_json = response.json()
    review_comment = response_json["candidates"][0]["content"]["parts"][0]["text"]
    print(review_comment)

except requests.exceptions.RequestException as e:
    print(f"錯誤：呼叫 Gemini API 失敗: {e}", file=sys.stderr)
    sys.exit(1)
except (KeyError, IndexError) as e:
    print(f"錯誤：解析 Gemini API 回應失敗: {e}", file=sys.stderr)
    print(f"完整的 API 回應: {response.text}", file=sys.stderr)
    sys.exit(1)