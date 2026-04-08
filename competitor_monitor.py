import os
from google import genai
from google.genai import types
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. 環境變數與 API 配置
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_SENDER = "behappywillyou@gmail.com"  # 你的發信 Gmail
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # GitHub Secrets 中的 16 位應用程式密碼
EMAIL_RECEIVER = "jenny_lee@digifinex.org" # 接收報告的信箱

# 初始化新版 SDK client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_exchange_updates():
    """使用 Gemini 搜尋並生成競品分析表格"""
    print("🚀 正在啟動 Gemini 聯網監測...")
    
    # 計算時間範圍
    today = datetime.now().strftime('%Y-%m-%d')
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    prompt = f"""
    你是資深加密貨幣產品經理，現在的日期是 {today}。請針對以下頭部交易所，檢索 {last_week} 到 {today} 期間「已經發生」的產品功能更新：
    Binance, OKX, Kucoin, Bitget, Gate.io。
    
    要求：
    1. 僅限「產品功能、App介面改版、新交易工具、系統優化、幣種管理/法幣網關更新」。
    2. 請直接以 HTML 表格格式輸出內容，表格標籤內請包含 border="1" 和 cellpadding="5"。
    3. 不要包含 ```html 標籤字眼，直接給 <table>...</table> 內容。
    4. 欄位包含：交易所名稱、功能亮點、影響程度(High/Medium/Low)、官方更新連結。
    5. 使用繁體中文。
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        
        if response and response.text:
            print("✅ 成功獲取 AI 分析數據！")
            return response.text
        else:
            return "<h3>暫無偵測到重大功能更新</h3>"
    except Exception as e:
        error_msg = f"❌ AI 抓取失敗: {str(e)}"
        print(error_msg)
        return f"<h3>數據抓取失敗</h3><p>錯誤原因：{str(e)}</p>"

def send_email(content):
    """發送 HTML 郵件"""
    print("📧 正在產出郵件並發送...")
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    msg = MIMEMultipart()
    msg['From'] = f"產品監控機器人 <{EMAIL_SENDER}>"
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"【每週競品觀察】{date_str} 產品更新報告"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2c3e50;">Jenny，這是本週偵測到的競品動態：</h2>
        <div style="margin-top: 20px;">
            {content}
        </div>
        <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
            * 此報告由 Gemini AI 自動生成，偵測範圍：Binance, OKX, Kucoin, Bitget, Gate.io
        </p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ 報告已成功寄送至你的信箱！")
    except Exception as e:
        print(f"❌ 郵件發送失敗: {str(e)}")

if __name__ == "__main__":
    # 執行流程
    report_data = get_exchange_updates()
    send_email(report_data)
