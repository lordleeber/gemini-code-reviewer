# .github/scripts/review.py (偵錯專用版本)
import os
import sys
import json
import requests

# 從環境變數獲取 API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("錯誤：環境變數 GEMINI_API_KEY 未設定。", file=sys.stderr)
    sys.exit(1)

# 為測試目的，使用一個寫死的、非常簡短的 diff 字串
PR_DIFF = "diff --git a/main.py b/main.py\n--- a/main.py\n+++ b/main.py\n@@ -1,1 +1,1 @@\n-print('hello')\n+print('hello world')"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

prompt = f"Please review this short code diff:\n\n{PR_DIFF}"

payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}
headers = {"Content-Type": "application/json"}

print("--- 正在嘗試呼叫 Gemini API ---")

try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()  # 檢查 HTTP 錯誤
    response_json = response.json()

    print("--- API 呼叫成功 ---")
    print(response_json["candidates"][0]["content"]["parts"][0]["text"])

except Exception as e:
    print(f"--- API 呼叫失敗 ---", file=sys.stderr)
    print(f"發生了無法預期的錯誤: {e}", file=sys.stderr)
    # 嘗試印出 API 的原始回應，這對於除錯非常有幫助
    if 'response' in locals() and hasattr(response, 'text'):
        print(f"API 的原始回應內容: {response.text}", file=sys.stderr)
    sys.exit(1)