# Techmeme Ride Home 逐字稿 🎙️

每日科技新聞 Podcast 自動轉錄，瀑布流卡片式呈現。

## 功能

- 📱 **響應式設計** — 手機、平板、桌機
- 🔍 **即時搜尋** — 快速找到關鍵字
- 🃏 **瀑布流佈局** — Masonry 卡片
- 📊 **公司列表** — 每集提及的公司與股票
- 🤖 **自動轉錄** — Whisper AI

## 自動轉錄

使用 OpenAI Whisper 自動轉錄新集數：

```bash
# 列出新集數
python3 scripts/transcribe.py --list

# 轉錄最新 1 集
python3 scripts/transcribe.py --limit 1 --model base

# 轉錄多集（更高品質）
python3 scripts/transcribe.py --limit 5 --model medium
```

### Whisper 模型選擇

| 模型 | 大小 | 速度 | 品質 |
|------|------|------|------|
| tiny | 39M | 最快 | 一般 |
| base | 74M | 快 | 好 |
| small | 244M | 中 | 很好 |
| medium | 769M | 慢 | 非常好 |
| large | 1550M | 最慢 | 最佳 |

## 技術架構

```
techmeme-transcripts/
├── index.html
├── css/style.css
├── js/app.js
├── data/
│   └── episodes.json
├── audio/          # 下載的音檔
└── scripts/
    └── transcribe.py
```

---

Built by Pinji 🐧 | 2026
