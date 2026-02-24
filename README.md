# LINE AI 客服系統（Hybrid 版）

## 系統架構

```
LINE 用戶
    ↓ 傳訊息/語音
LINE Bot (line_bot.py)
    ↓ 回覆按鈕
用戶點擊 → Streamlit 網頁 (app_streamlit.io)
    ↓ 繼續對話
```

## 檔案說明

| 檔案 | 功能 |
|------|------|
| `app_streamlit.py` | Streamlit 網頁客服介面 |
| `line_bot.py` | LINE Bot（接收訊息，回覆按鈕） |
| `.env.example` | 環境變數範本 |

---

## 部署步驟

### 1. 部署 Streamlit 網頁
1. 推送代碼到 GitHub
2. 前往 https://share.streamlit.io
3. 連結 `line-ai-customer-service` 倉庫
4. Main file：`app_streamlit.py`
5. 設定 Secrets：
   ```toml
   [secrets]
   MINIMAX_API_KEY = "您的API金鑰"
   ```
6. 取得網址（例如：`https://your-name.streamlit.app`）

### 2. 部署 LINE Bot
選項 A：Zeabur（推薦）
1. Zeabur 新增服務 → Python
2. Main file：`line_bot.py`
3. 設定環境變數：
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `STREAMLIT_URL` = 步驟 1 的網址
4. 取得 Bot URL（例如：`https://xxx.zeabur.app`）

選項 B：Railway / Render / Heroku
1. 部署 `line_bot.py`
2. 設定環境變數

### 3. 設定 LINE Webhook
1. 前往 https://developers.line.me/
2. 選擇您的 Messaging API 頻道
3. Webhook URL 填入：`https://your-bot-url.zeabur.app/callback`
4. 啟用 Webhook

### 4. 宣傳
1. 取得 LINE 官方帳號連結
2. 分享給消費者
3. 消費者加入後傳訊息，會收到網頁按鈕

---

## 功能

### LINE Bot
- ✅ 關鍵詞自動回覆
- ✅ 網頁開啟按鈕
- ✅ 轉接真人選項

### Streamlit 網頁
- ✅ 文字/語音問答
- ✅ QA 知識庫
- ✅ MiniMax TTS 語音回覆
- ✅ 對話歷史

---

## 環境變數

```bash
# LINE Bot
LINE_CHANNEL_ACCESS_TOKEN=xxx
LINE_CHANNEL_SECRET=xxx
STREAMLIT_URL=https://xxx.streamlit.app

# MiniMax
MINIMAX_API_KEY=xxx
```
