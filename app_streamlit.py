"""
LINE AI 客服系統
Streamlit Web 介面 - 電子發票系統客服
"""
import streamlit as st
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ===== 頁面設定 =====
st.set_page_config(
    page_title="LINE AI 客服系統",
    page_icon="💬",
    layout="wide"
)

# ===== 環境變數 =====
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID", "")

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


def generate_answer(user_message):
    """生成回答"""
    answer = find_best_answer(user_message)
    
    if answer == "transfer":
        return "transfer"
    
    if answer:
        return answer
    
    return FALLBACK_ANSWER


# ===== MiniMax TTS =====
def tts_minimax(text):
    """使用 MiniMax TTS 語音合成"""
    if not MINIMAX_API_KEY:
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "speech-02 hd",
            "text": text,
            "voice_id": "female-shaoying",
            "speed": 1.0,
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
                import base64
                audio_bytes = base64.b64decode(audio_data)
                return audio_bytes
        
        return None
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None


# ===== Web Speech API (瀏覽器語音辨識) =====
def get_speech_recognition_html():
    """取得語音辨識 HTML"""
    return """
    <script>
    function startRecording() {
        // 檢查瀏覽器支援
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) {
            alert('您的瀏覽器不支援語音辨識！\\n\\n請使用 Chrome 瀏覽器，或直接輸入文字。');
            return;
        }
        
        const recognition = new SpeechRecognition();
        
        recognition.lang = 'zh-TW';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        // 顯示狀態
        const statusDiv = document.getElementById('voice_status');
        if (statusDiv) {
            statusDiv.innerHTML = '🎤 正在聆聽... 請說話';
            statusDiv.style.color = 'blue';
        }
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            
            // 填入輸入框
            const input = document.querySelector('input[type="text"]');
            if (input) {
                input.value = transcript;
            }
            
            if (statusDiv) {
                statusDiv.innerHTML = '✓ 已識別：' + transcript;
                statusDiv.style.color = 'green';
            }
            
            // 自動點擊發送按鈕
            setTimeout(() => {
                const buttons = document.querySelectorAll('button');
                buttons.forEach(btn => {
                    if (btn.textContent.includes('Send') || btn.querySelector('svg')) {
                        btn.click();
                    }
                });
            }, 500);
        };
        
        recognition.onerror = function(event) {
            let errorMsg = '語音辨識錯誤';
            switch(event.error) {
                case 'no-speech':
                    errorMsg = '沒有偵測到語音，請再試一次';
                    break;
                case 'audio-capture':
                    errorMsg = '無法使用麥克風，請檢查權限';
                    break;
                case 'not-allowed':
                    errorMsg = '麥克風權限被拒絕，請允許存取';
                    break;
                default:
                    errorMsg = '錯誤：' + event.error;
            }
            
            if (statusDiv) {
                statusDiv.innerHTML = '✗ ' + errorMsg;
                statusDiv.style.color = 'red';
            }
        };
        
        recognition.onend = function() {
            if (statusDiv && statusDiv.textContent.includes('聆聽')) {
                statusDiv.innerHTML = '👂 等待輸入...';
                statusDiv.style.color = 'gray';
            }
        };
        
        recognition.start();
    }
    </script>
    """


# ===== 側邊欄 =====
with st.sidebar:
    st.title("⚙️ 設定")
    
    st.subheader("API 設定")
    api_key = st.text_input("MiniMax API Key", value=MINIMAX_API_KEY, type="password")
    if api_key:
        os.environ["MINIMAX_API_KEY"] = api_key
    
    st.subheader("功能")
    enable_tts = st.toggle("啟用語音回覆 (TTS)", value=True)
    
    st.divider()
    
    st.subheader("📋 QA 知識庫")
    if st.button("查看 QA 列表"):
        st.session_state.show_qa = not st.session_state.get("show_qa", False)
    
    if st.session_state.get("show_qa", False):
        for i, qa in enumerate(QA_KNOWLEDGE_BASE):
            with st.expander(f"Q{i+1}: {qa['keywords'][0]}"):
                st.write("**關鍵詞：**", ", ".join(qa["keywords"]))
                st.write("**答案：**", qa["answer"])
    
    st.divider()
    
    st.subheader("ℹ️ 資訊")
    st.caption("關網資訊 AI 客服系統 v1.0")
    st.caption("電話：02-7750-5070")


# ===== 主頁面 =====
st.title("💬 LINE AI 客服系統")
st.markdown("### 電子發票客服機器人")

# 說明
with st.expander("📖 使用說明", expanded=True):
    st.markdown("""
    **歡迎使用 AI 客服系統！**
    
    - 直接輸入文字問題
    - 或使用麥克風語音輸入（支援 Chrome 瀏覽器）
    - 系統會自動從知識庫中找到答案
    - 複雜問題可轉接真人客服
    
    **常見問題關鍵詞：**
    - 電子發票、申請、查詢、對獎、作廢
    - 載具、統編、營業時間、聯絡電話
    """)

# 語音辨識控制
st.markdown(get_speech_recognition_html(), unsafe_allow_html=True)

# 狀態顯示
if 'status' not in st.session_state:
    st.session_state.status = ""

status_placeholder = st.empty()

# 對話歷史
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 顯示對話歷史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# 輸入區域
col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.chat_input("請輸入您的問題...")

with col2:
    # 語音輸入按鈕
    st.markdown('<div id="voice_status" style="padding: 10px; font-weight: bold;">👂 點擊按鈕說話</div>', unsafe_allow_html=True)
    
    if st.button("🎤 語音輸入", use_container_width=True):
        st.markdown("""
        <script>
        if (typeof startRecording === 'function') {
            startRecording();
        }
        </script>
        """, unsafe_allow_html=True)

# 處理輸入
if user_input:
    # 加入用戶訊息
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)
    
    # 生成回答
    answer = generate_answer(user_input)
    
    # 處理轉接
    if answer == "transfer":
        response_text = "好的，我已通知客服人員，請稍候由專人為您服務～\n\n如需緊急服務，請致電：02-7750-5070"
    else:
        response_text = answer
    
    # TTS 語音
    audio_data = None
    if enable_tts and answer != "transfer":
        with st.spinner("🔊 產生語音回覆中..."):
            audio_data = tts_minimax(response_text)
    
    # 加入 AI 訊息
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_text,
        "audio": audio_data
    })
    
    # 顯示回覆
    with st.chat_message("assistant"):
        st.write(response_text)
        if audio_data:
            st.audio(audio_data, format="audio/mp3")

# 清除對話
if st.button("🗑️ 清除對話"):
    st.session_state.messages = []
    st.rerun()
