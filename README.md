# LINE AI 客服系統（Streamlit 版本）

## 功能
- ✅ 文字問答（QA 知識庫）
- ✅ 語音輸入（瀏覽器 Web Speech API）
- ✅ 語音回覆（MiniMax TTS，可選）
- ✅ 真人轉接機制

## 環境變數 (.env)
```
MINIMAX_API_KEY=你的MiniMax_API_Key
```

## 本地運行
```bash
pip install -r requirements.txt
streamlit run app_streamlit.py
```

## 部署到 Streamlit Cloud
1. 推送代碼到 GitHub
2. 前往 https://share.streamlit.io
3. 連結 GitHub 倉庫
4. 設定環境變數
5. 部署完成！

## 部署到 Zeabur（Streamlit）
1. 在 Zeabur 新增服務
2. 選擇 Streamlit
3. 連結 GitHub 倉庫
4. 設定環境變數
5. 部署完成！

## QA 知識庫
可在 `app_streamlit.py` 中的 `QA_KNOWLEDGE_BASE` 陣列新增問題與答案。
