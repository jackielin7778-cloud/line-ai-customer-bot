"""
LINE AI 客服系統
電子發票系統客服 - 支援語音輸入/輸出
"""
import os
import json
import requests
from flask import Flask, request, jsonify, send_file
from flask.helpers import make_response
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, AudioMessage, TextSendMessage, AudioSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ===== 環境變數 =====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID", "")
ADMIN_LINE_ID = os.getenv("ADMIN_LINE_ID", "")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(LINE_CHANNEL_SECRET)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# ===== QA 知識庫 =====
QA_KNOWLEDGE_BASE = [
    # 電子發票基礎
    {
        "keywords": ["什麼是電子發票", "電子發票定義", "什麼是電子發票"],
        "answer": "電子發票是指開立人或接收人透過網路或其他電子方式開立、傳輸或接收的統一發票。您可以參考關網資訊官網：https://www.gateweb.com.tw/information/"
    },
    {
        "keywords": ["如何申請電子發票", "申請電子發票", "開通電子發票"],
        "answer": "申請電子發票服務，請洽關網資訊：\n電話：02-7750-5070\nEmail：cs@gateweb.com.tw\n或直接加 LINE：https://lin.ee/ob1dBrB"
    },
    {
        "keywords": ["發票查詢", "查詢發票", "怎麼查發票"],
        "answer": "您可以透過以下方式查詢發票：\n1. 財政部電子發票整合平台\n2. 關網資訊會員中心\n3. 行動支付 APP（如街口支付、LINE Pay 等）"
    },
    {
        "keywords": ["對獎", "發票對獎", "中獎"],
        "answer": "電子發票自動對獎！中獎時會發送通知。\n每單月 25 日開獎（若逢假日順延）。\n中獎領取方式：\n- 載具中獎：至便利商店多媒体机列印\n- 紙本中獎：至代發獎金單位領取"
    },
    {
        "keywords": ["作廢發票", "發票作廢", "可以作廢嗎"],
        "answer": "電子發票開立後，若有錯誤可作廢重開。\n⚠️ 注意事項：\n1. 需在發票開立當期內作廢\n2. 逾 時不得修改\n3. 請聯繫您的開立廠商處理"
    },
    {
        "keywords": ["載具", "手機條碼", "自然人憑證", "共通性載具"],
        "answer": "電子發票載具有三種：\n1. 手機條碼（3J0002）\n2. 自然人憑證（CQ0001）\n3. 共通性載具（悠遊卡、一卡通、iCash 等）\n請向您的店家詢問如何使用載具存檔發票"
    },
    {
        "keywords": ["統編", "統一編號", "公司發票"],
        "answer": "如需開立有統編的發票，請提供：\n1. 公司統一編號\n2. 公司名稱\n3. 公司地址\n告知開立店家即可"
    },
    {
        "keywords": ["紙本發票", "紙發票"],
        "answer": "電子發票可選擇是否列印紙本。若需紙本，可請店家印出，或自行至超商多媒体機補印。"
    },
    # 服務時間
    {
        "keywords": ["營業時間", "服務時間", "上班時間", "客服時間"],
        "answer": "關網資訊服務時間：\n週一至週五 9:30~12:00 / 13:00~17:30\n電話：02-7750-5070"
    },
    {
        "keywords": ["聯絡電話", "客服電話", "電話"],
        "answer": "關網資訊聯絡資訊：\n電話：02-7750-5070\n傳真：02-8773-5339\nEmail：cs@gateweb.com.tw"
    },
    # 轉接真人
    {
        "keywords": ["真人", "客服人員", "真人客服", "轉接"],
        "answer": "好的，我為您轉接真人客服，請稍候..."
    },
    {
        "keywords": ["感謝", "謝謝", "了解了"],
        "answer": "不客氣！很高興為您服務～ 如有其他問題歡迎隨時詢問！😊"
    },
    {
        "keywords": ["再見", "bye", "掰掰"],
        "answer": "再見！感謝您的使用，祝您順心！👋"
    }
]

# ===== 預設回覆 =====
DEFAULT_ANSWER = """您好！我是關網資訊 AI 客服小幫手～

我可以幫您解答：
• 電子發票相關問題
• 申請服務諮詢
• 發票查詢與對獎
• 載具設定說明

請直接輸入您的問題，或說出您想了解的內容。

如需真人服務，請輸入「轉接真人客服」或「我要找客服」。

更多資訊：https://www.gateweb.com.tw/"""

FALLBACK_ANSWER = """抱歉，我不太理解您的問題...😔

您可以嘗試詢問：
• 什麼是電子發票？
• 如何申請電子發票？
• 發票如何查詢？
• 發票可以作廢嗎？

或者輸入「轉接真人客服」由專人為您服務。"""


# ===== MiniMax STT 語音辨識 =====
def stt_minimax(audio_url):
    """使用 MiniMax STT 語音辨識"""
    try:
        # 建立轉寫任務
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "speech-01a",
            "task": "transcription",
            "audio_url": audio_url,
            "language": "zh"
        }
        
        resp = requests.post(
            "https://api.minimax.chat/v1/stt/create",
            headers=headers,
            json=data,
            timeout=30
        )
        
        result = resp.json()
        
        if result.get("code") == 0:
            job_id = result.get("data", {}).get("job_id")
            # 取得結果（實際需輪詢，這裡簡化）
            return get_stt_result(job_id)
        else:
            return None
            
    except Exception as e:
        print(f"STT Error: {e}")
        return None


def get_stt_result(job_id):
    """取得 STT 轉寫結果"""
    try:
        headers = {"Authorization": f"Bearer {MINIMAX_API_KEY}"}
        
        for _ in range(10):  # 最多等待 10 次
            resp = requests.get(
                f"https://api.minimax.chat/v1/stt/{job_id}",
                headers=headers,
                timeout=10
            )
            result = resp.json()
            
            if result.get("code") == 0:
                data = result.get("data", {})
                if data.get("status") == "completed":
                    return data.get("transcription", "")
                elif data.get("status") == "failed":
                    return None
            
            import time
            time.sleep(1)
        
        return None
    except:
        return None


# ===== MiniMax TTS 語音合成 =====
def tts_minimax(text, voice_id="female-shaoying"):
    """使用 MiniMax TTS 語音合成"""
    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "speech-02 hd",
            "text": text,
            "voice_id": voice_id,
            "speed": 1.0,
            "volume": 1.0,
            "pitch": 0,
            "audio_sample_rate": 32000,
            "bitrate": 128000,
            "format": "mp3"
        }
        
        resp = requests.post(
            "https://api.minimax.chat/v1/t2a_v2",
            headers=headers,
            json=data,
            timeout=60
        )
        
        result = resp.json()
        
        if result.get("code") == 0:
            audio_data = result.get("data", {}).get("audio")
            if audio_data:
                # 解碼 base64
                import base64
                audio_bytes = base64.b64decode(audio_data)
                return audio_bytes
        
        return None
    except Exception as e:
        print(f"TTS Error: {e}")
        return None


# ===== QA 匹配 =====
def find_best_answer(user_message):
    """從知識庫中找到最佳答案"""
    user_message = user_message.lower()
    
    best_match = None
    max_score = 0
    
    for qa in QA_KNOWLEDGE_BASE:
        score = 0
        for keyword in qa["keywords"]:
            if keyword in user_message:
                score += 1
        
        if score > max_score:
            max_score = score
            best_match = qa["answer"]
    
    if max_score > 0:
        return best_match
    
    # 檢查是否需要轉接真人
    transfer_keywords = ["轉接", "真人", "客服人員", "我要找客服", "人工"]
    for kw in transfer_keywords:
        if kw in user_message:
            return "transfer"
    
    return None


def generate_ai_answer(user_message):
    """使用 AI 生成回答（進階版）"""
    # 先嘗試從 QA 庫找到答案
    answer = find_best_answer(user_message)
    
    if answer == "transfer":
        return None, True  # 需要轉接真人
    
    if answer:
        return answer, False
    
    # 如果沒有匹配，返回默認答案
    return FALLBACK_ANSWER, False


# ===== LINE Webhook =====
@app.route("/callback", methods=["POST"])
def callback():
    """LINE Webhook 入口"""
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        return jsonify({"error": "Invalid signature"}), 400
    
    for event in events:
        if isinstance(event, MessageEvent):
            handle_message(event)
    
    return jsonify({"status": "ok"})


def handle_message(event):
    """處理接收到的訊息"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    # 文字訊息
    if isinstance(event.message, TextMessage):
        user_text = event.message.text
        handle_text_message(user_id, reply_token, user_text)
    
    # 語音訊息
    elif isinstance(event.message, AudioMessage):
        handle_audio_message(user_id, reply_token, event.message.id)


def handle_text_message(user_id, reply_token, user_text):
    """處理文字訊息"""
    # 生成回答
    answer, need_transfer = generate_ai_answer(user_text)
    
    if need_transfer:
        # 轉接真人
        transfer_to_human(user_id, user_text)
        reply_text(reply_token, "好的，我已通知客服人員，請稍候由專人為您服務～")
        return
    
    if answer:
        # 回覆文字
        reply_text(reply_token, answer)
        
        # 同時回覆語音（可選）
        audio = tts_minimax(answer)
        if audio:
            reply_audio(reply_token, audio)
    else:
        reply_text(reply_token, FALLBACK_ANSWER)


def handle_audio_message(user_id, reply_token, message_id):
    """處理語音訊息"""
    try:
        # 取得語音檔案
        audio_content = line_bot_api.get_message_content(message_id)
        audio_bytes = audio_content.content
        
        # 上傳到可訪問的 URL（簡化版：使用臨時儲存）
        # 實際部署時需要上傳到雲端儲存
        
        # 先回覆處理中
        reply_text(reply_token, "收到您的語音訊息，正在辨識...")
        
        # 使用 Web Speech API 作為替代方案（瀏覽器端）
        # 這裡暫時返回文字引導用戶輸入文字
        reply_text(reply_token, "您好！請直接輸入文字問題，我會立即為您服務～")
        
    except Exception as e:
        print(f"Audio Error: {e}")
        reply_text(reply_token, "抱歉，無法處理語音訊息。請輸入文字問題～")


def reply_text(reply_token, text):
    """回覆文字訊息"""
    try:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=text)
        )
    except Exception as e:
        print(f"Reply Error: {e}")


def reply_audio(reply_token, audio_bytes):
    """回覆語音訊息"""
    try:
        # 將音訊上傳到 LINE
        audio_content = BytesIO(audio_bytes)
        
        line_bot_api.reply_message(
            reply_token,
            AudioSendMessage(
                original_content_url="https://example.com/audio.mp3",  # 需要實際 URL
                duration=5000
            )
        )
    except Exception as e:
        print(f"Audio Reply Error: {e}")


def transfer_to_human(user_id, user_message):
    """轉接真人客服"""
    if ADMIN_LINE_ID:
        # 通知管理員
        notify_text = f"🔔 新客服轉接請求\n\n使用者 ID：{user_id}\n問題：{user_message}"
        try:
            line_bot_api.push_message(ADMIN_LINE_ID, TextSendMessage(text=notify_text))
        except:
            pass


# ===== 首頁 =====
@app.route("/")
def index():
    return jsonify({
        "status": "running",
        "service": "LINE AI 客服系統",
        "version": "1.0.0"
    })


# ===== 健康檢查 =====
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
