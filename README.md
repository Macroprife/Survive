# 🏚️ 废土求生 (Wasteland Survive)

末日生存文字游戏 + 像素帧动画

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎮 游戏简介

核战后的废土世界，你是一名幸存者。管理生存指标、探索废墟、收集物资、合成装备，最终找到无线电零件向外界求救。

## ✨ 特性

- **5 维生存系统** — 生命/饥饿/口渴/精力/理智
- **6 个探索地点** — 从安全的庇护所到极度危险的通讯塔
- **合成系统** — 药物、绷带、武器、护甲、火把
- **战斗系统** — 攻击/防御/逃跑，武器加成，护甲减伤
- **随机事件** — 遭遇战、天气灾害、陷阱、线索
- **存档系统** — SQLite 持久化存档
- **像素动画** — Canvas 绘制的场景、角色、天气效果
- **CRT 复古风** — 扫描线 + 像素字体 + 暗黑末日色调

## 🚀 快速开始

### 本地运行

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# 启动服务
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Docker 运行

```bash
docker compose up --build
```

然后浏览器打开 `http://localhost:8000`

## 🎹 操作指南

| 按键 | 功能 |
|------|------|
| `E` | 探索当前地点 |
| `R` | 休息恢复体力 |
| `C` | 打开合成菜单 |
| `I` | 使用物品 |
| `M` | 地点导航 |
| `Ctrl+S` | 保存游戏 |
| `H` | 帮助 |
| `A/D/F` | 战斗中：攻击/防御/逃跑 |

## 📁 项目结构

```
wasteland-survive/
├── backend/
│   ├── main.py          # FastAPI 服务 (API + 静态文件)
│   ├── game_engine.py   # 游戏引擎 (生存/探索/战斗/合成)
│   ├── models.py        # Pydantic 数据模型
│   └── requirements.txt
├── frontend/
│   ├── index.html       # 游戏界面
│   ├── style.css        # 暗黑末日风格 + CRT 扫描线
│   ├── game.js          # 客户端逻辑 + 打字机效果
│   └── animations.js    # Canvas 像素动画 (篝火/雨/沙暴/场景)
├── Dockerfile
├── docker-compose.yml
├── DESIGN.md
└── README.md
```

## 🏆 通关条件

收集 **3 个无线电零件** → 前往 **通讯塔** → 修复通讯设备 → 等待救援

## 📄 License

MIT
