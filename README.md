# LINE AI 客服系統

## 環境變數 (.env)
```
LINE_CHANNEL_ACCESS_TOKEN=你的LINE_ACCESS_TOKEN
LINE_CHANNEL_SECRET=你的LINE_CHANNEL_SECRET
MINIMAX_API_KEY=你的MiniMax_API_Key
MINIMAX_GROUP_ID=你的MiniMax_Group_ID
ADMIN_LINE_ID=真人客服的LINE_ID
```

## 必要套件
```
flask>=2.3.0
line-bot-sdk>=3.0.0
requests>=2.28.0
python-dotenv>=1.0.0
```

## 部署
```bash
git add .
git commit -m "LINE AI客服系統"
git push origin main
```
然後在 Zeabur 部署，設定環境變數和 LINE Webhook URL。
