"""
LINE AI 客服 Bot
使用 Push Message 方式回覆
"""
import os
import logging
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, AudioMessage, FollowEvent
from linebot.exceptions import InvalidSignatureError
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "https://line-ai-customer-bot-dpd8h2rkqdyyeqm9ry99yn.streamlit.app/")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)

WELCOME_MESSAGE = """您好！👋

我是關網資訊 AI 客服小幫手～

我可以幫您解答：
• 電子發票相關問題
• 申請服務諮詢
• 發票查詢與對獎
• 載具設定說明

請直接輸入您的問題～

📞 客服專線：02-7750-5070
🌐 官網：https://www.gateweb.com.tw/"""

QA_REPLIES = {
    "什麼是電子發票": "電子發票是指開立人或接收人透過網路或其他電子方式開立、傳輸或接收的統一發票。",
    "如何申請": "申請電子發票服務，請洽關網資訊：\n電話：02-7750-5070\nEmail：cs@gateweb.com.tw\nLINE：https://lin.ee/ob1dBrB",
    "發票查詢": "您可以透過以下方式查詢發票：\n1. 財政部電子發票整合平台\n2. 關網資訊會員中心\n3. 行動支付 APP",
    "對獎": "電子發票自動對獎！\n每單月 25 日開獎。\n中獎後會發送通知到您的手機條碼/載具。",
    "作廢": "電子發票開立後若有錯誤可作廢重開，但需在發票開立當期內處理，請聯繫您的開立廠商。",
    "載具": "電子發票載具有三種：\n1. 手機條碼（3J0002）\n2. 自然人憑證（CQ0001）\n3. 共通性載具（悠遊卡、一卡通等）",
    "營業時間": "關網資訊服務時間：\n週一至週五 9:30~12:00 / 13:00~17:30\n電話：02-7750-5070",
    "電話": "關網資訊聯絡資訊：\n電話：02-7750-5070\n傳真：02-8773-5339\nEmail：cs@gateweb.com.tw",
    "統編": "如需開立有統編的發票，請提供：公司統一編號、公司名稱、公司地址，告知開立店家即可。",
}

FALLBACK_REPLY = """抱歉，我不太理解您的問題... 😔

您可以嘗試詢問：
• 什麼是電子發票？
• 如何申請電子發票？
• 發票如何查詢？
• 發票可以作廢嗎？

或致電 02-7750-5070 由專人服務。"""


def find_keyword_reply(text):
    text = text.lower()
    for keyword, reply in QA_REPLIES.items():
        if keyword in text:
            return reply
    return None


@app.route("/callback", methods=["POST"])
def callback():
    if request.method != "POST":
        return jsonify({"error": "Method not allowed"}), 405
    
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    
    logger.info("收到 LINE Webhook")
    
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    for event in events:
        if isinstance(event, FollowEvent):
            user_id = event.source.user_id
            try:
                line_bot_api.push_message(user_id, TextSendMessage(text=WELCOME_MESSAGE))
                logger.info(f"歡迎訊息已發送給 {user_id}")
            except Exception as e:
                logger.error(f"Push error: {e}")
        
        elif isinstance(event, MessageEvent):
            user_id = event.source.user_id
            
            # 處理所有訊息類型
            msg_type = type(event.message).__name__
            logger.info(f"收到訊息類型: {msg_type}")
            
            if isinstance(event.message, AudioMessage):
                # 語音訊息
                try:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text="您好！我收到您的語音訊息了～\n\n請直接輸入文字問題，我會立即為您服務！")
                    )
                except Exception as e:
                    logger.error(f"Push error: {e}")
            elif isinstance(event.message, TextMessage):
                # 文字訊息
                user_text = event.message.text
                keyword_reply = find_keyword_reply(user_text)
                reply_text = keyword_reply if keyword_reply else FALLBACK_REPLY
                try:
                    line_bot_api.push_message(user_id, TextSendMessage(text=reply_text))
                except Exception as e:
                    logger.error(f"Push error: {e}")
            else:
                # 其他訊息類型
                try:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(text="您好！我已收到您的訊息。\n\n請輸入文字問題，我會立即為您服務！")
                    )
                except Exception as e:
                    logger.error(f"Push error: {e}")
    
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return jsonify({
        "status": "running",
        "service": "LINE AI 客服 Bot",
        "version": "2.0.0"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "line_configured": bool(LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET)
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"啟動伺服器，PORT={port}")
    app.run(host="0.0.0.0", port=port)
