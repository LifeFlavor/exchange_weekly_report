import google.generativeai as genai
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === 配置區 ===
# 建議將這些敏感資訊放在環境變數中，或 GitHub Secrets
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
EMAIL_SENDER = "你的發信郵件@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # Gmail 應用程式密碼
EMAIL_RECEIVER = "jenny_lee@digifinex.org"

# 1. 初始化 Gemini
genai.configure(api_key=GEMINI_API_KEY)

def get_exchange_updates():
    # 使用 1.5 Flash 模型（速度快且免費額度高）
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = """
    你是資深加密貨幣產品經理。請針對以下頭部交易所，檢索過去 7 天內（2026年3月底至4月初）的「產品功能更新」：
    Binance, OKX, Kucoin, Bitget, Gate.io。
    
    請注意：
    1. 僅限「產品功能、App介面改版、新交易工具、系統優化」。
    2. 排除「單純的上幣公告、行銷抽獎活動」。
    3. 請以 HTML 表格格式輸出。
    4. 欄位包含：交易所名稱、功能亮點、影響程度(High/Medium/Low)、官方連結。
    5. 使用繁體中文。
    """

    # 執行生成
    response = model.generate_content(prompt)
    return response.text

def send_email(html_table):
    subject = f"【每週競品觀察】{datetime.now().strftime('%Y-%m-%d')} 產品更新報告"
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    # 組合郵件內容
    full_html = f"""
    <html>
      <head>
        <style>
          table {{ border-collapse: collapse; width: 100%; }}
          th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
          th {{ background-color: #f2f2f2; }}
        </style>
      </head>
      <body>
        <h3>Jenny，這是本週偵測到的競品動態：</h3>
        {html_table}
        <br>
        <p><small>本報告由 Gemini AI 與 Python 自動化腳本生成。</small></p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(full_html, 'html'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ 報告已成功寄送至你的信箱！")
    except Exception as e:
        print(f"❌ 寄送失敗: {e}")

if __name__ == "__main__":
    print("🚀 正在啟動 Gemini 聯網監測...")
    content = get_exchange_updates()
    print("📧 正在產出郵件並發送...")
    send_email(content)
