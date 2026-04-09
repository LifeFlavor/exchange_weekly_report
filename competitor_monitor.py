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
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # GitHub Secrets 中的 16 位應用程式密碼

# 更新收件人名單
EMAIL_RECEIVERS = [
    "jenny_lee@digifinex.org"
]

# 初始化新版 SDK client
client = genai.Client(api_key=GEMINI_API_KEY)

def get_exchange_updates():
    """使用 Gemini 聯網搜尋並生成競品分析表格"""
    print("🚀 正在啟動 Gemini 聯網監測...")

    # 計算時間範圍
    today = datetime.now().strftime('%Y-%m-%d')
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # 優化 Prompt：確保 AI 知道現在是 2026 年，且不要在表格內放網址
    prompt = f"""
    現在日期是 {today}。
    你是資深加密貨幣產品經理。請針對以下頭部交易所，搜尋 {last_week} 到 {today} 期間「已經發生」的「產品功能更新」：
    Binance, OKX, Kucoin, Bitget, Gate.io。

    要求：
    1. 僅限「產品功能、App介面改版、新交易工具、系統優化、幣種管理/法幣網關更新」。
    2. 請直接以 HTML 表格格式輸出內容，表格標籤內請包含 border="1" 和 cellpadding="5"。
    3. 不要包含 ```html 標籤字眼，直接給 <table>...</table> 內容。
    4. 欄位包含：交易所名稱、功能亮點、影響程度(High/Medium/Low)、官方更新說明。
    5. 使用繁體中文。
    6. 請務必根據實際搜尋結果填寫，若某交易所本週無重大更新請標註「本週無重大更新」。
    7. **絕對不要在表格欄位中放置連結**，所有連結我會透過系統自動提取。
    8. 在表格上方，寫出本週競品產品亮點功能更新摘要，並建議最適合我們中小型交易所跟進的功能。以分段重點呈現。
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        report_text = "<h3>暫無偵測到重大功能更新</h3>"
        sources_html = ""

        if response and response.text:
            print("✅ 成功獲取 AI 分析數據！")
            report_text = response.text

        # 從 grounding metadata 提取真實搜尋來源連結
        try:
            grounding = response.candidates[0].grounding_metadata
            chunks = grounding.grounding_chunks

            if chunks:
                sources_html = """
                <div style="margin-top:40px; padding:20px; background:#f4f7f9; border-top:2px solid #2c3e50;">
                    <h3 style="color:#2c3e50; margin-top:0;">📎 參考來源連結 (AI 搜尋證據)</h3>
                    <ul style="font-size: 14px; color: #34495e;">
                """
                # 使用 set 避免重複連結
                seen_uris = set()
                for chunk in chunks:
                    if chunk.web and chunk.web.uri and chunk.web.uri not in seen_uris:
                        title = chunk.web.title or chunk.web.uri
                        uri = chunk.web.uri
                        sources_html += f'<li style="margin-bottom:8px;"><a href="{uri}" target="_blank" style="color:#3498db;">{title}</a></li>'
                        seen_uris.add(uri)
                sources_html += "</ul></div>"
                print(f"✅ 成功提取 {len(seen_uris)} 筆不重複來源連結")
        except Exception as e:
            print(f"⚠️ 來源連結提取失敗: {str(e)}")

        return report_text, sources_html

    except Exception as e:
        error_msg = f"❌ AI 抓取失敗: {str(e)}"
        print(error_msg)
        return f"<h3>數據抓取失敗</h3><p>錯誤原因：{str(e)}</p>", ""


def send_email(report_text, sources_html):
    """發送 HTML 郵件給多位收件人"""
    print(f"📧 正在準備發送郵件給 {len(EMAIL_RECEIVERS)} 位收件人...")

    date_str = datetime.now().strftime('%Y-%m-%d')
    msg = MIMEMultipart()
    msg['From'] = f"產品監控機器人 <{EMAIL_SENDER}>"
    msg['To'] = ", ".join(EMAIL_RECEIVERS) # 在信件標頭顯示所有收件人
    msg['Subject'] = f"【每週競品觀察】{date_str} 產品更新報告"

    # 重新編排 HTML 結構，確保 sources_html 在最後
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #2c3e50;">Jenny，這是本週偵測到的競品動態：</h2>
        <div style="margin: 20px 0; overflow-x: auto;">
            {report_text}
        </div>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 40px 0;">
        {sources_html}
        <p style="color: #95a5a6; font-size: 12px; margin-top: 40px; border-top: 1px solid #eee; padding-top: 10px;">
            * 此報告由 Gemini AI 自動生成。偵測對象：Binance, OKX, Kucoin, Bitget, Gate.io<br>
            * 若內容有誤，請聯絡管理員更新指令。
        </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, 'html'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            # 實際發送時傳入名單清單
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())
        print("✅ 報告已成功寄送至所有指定信箱！")
    except Exception as e:
        print(f"❌ 郵件發送失敗: {str(e)}")


if __name__ == "__main__":
    report_text, sources_html = get_exchange_updates()
    send_email(report_text, sources_html)