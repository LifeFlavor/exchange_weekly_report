import google.generativeai as genai
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === 1. 初始化與環境配置 ===
# 從 GitHub Secrets 抓取金鑰
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_SENDER = "你的發信郵件@gmail.com" # 這裡請填入你的 Gmail
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # 這裡放 GitHub Secret 裡的應用程式密碼
EMAIL_RECEIVER = "jenny_lee@digifinex.org"

# 設定 Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def get_exchange_updates():
    print("🚀 正在啟動 Gemini 聯網監測...")
    
    # 使用目前最穩定的模型路徑格式
    model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
    
    # 這裡就是你提到的 Prompt 核心邏輯
    prompt = """
    你是資深加密貨幣產品經理。請針對以下頭部交易所，檢索過去 7 天內（2026年3月底至4月初）的「產品功能更新」：
    Binance, OKX, Kucoin, Bitget, Gate.io。
    
    請注意：
    1. 僅限「產品功能、App介面改版、新交易工具、系統優化」。
    2. 排除「單純的上幣公告、行銷抽獎活動」。
    3. 請直接以 HTML 表格格式輸出，不要包含額外的 Markdown 標籤 (如 ```html)。
    4. 欄位包含：交易所名稱、功能亮點、影響程度(High/Medium/Low)、官方連結。
    5. 使用繁體中文。
    """

    try:
        # 呼叫 Gemini 產出內容
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini 呼叫失敗: {e}")
        return f"<h3>數據抓取失敗</h3><p>{str(e)}</p>"

def send_email(html_table):
    print("📧 正在產出郵件並發送...")
    subject = f"【每週競品觀察】{datetime.now().strftime('%Y-%m-%d')} 產品更新報告"
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    # 組合完整的郵件 HTML 樣式
    full_html = f"""
    <html>
      <head>
        <style>
          table {{ border-collapse: collapse; width: 100%; font-family: sans-serif; }}
          th, td {{ border: 1px solid #dddddd; text-align: left; padding: 12px; }}
          th {{ background-color: #f8f9fa; color: #333; }}
          .high {{ color: #d9534f; font-weight: bold; }}
        </style>
      </head>
      <body>
        <h2 style="color: #2c3e50;">Jenny，這是本週偵測到的競品動態：</h2>
        <div style="margin-top: 20px;">
          {html_table}
        </div>
        <br>
        <hr>
        <p style="color: #7f8c8d; font-size: 12px;">本報告由 Gemini AI 與 GitHub Actions 自動化腳本生成。</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(full_html, 'html'))

    try:
        # 使用 Gmail SMTP 發信
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ 報告已成功寄送至你的信箱！")
    except Exception as e:
        print(f"❌ 郵件寄送失敗: {e}")

if __name__ == "__main__":
    # 執行主流程
    report_content = get_exchange_updates()
    send_email(report_content)