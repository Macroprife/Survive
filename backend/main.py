import os
import json
import time
import sqlite3
from datetime import datetime
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import GameState, Action, ActionType, Event
from .models import NPCInteraction
from . import game_engine

app = FastAPI(title="废土求生 API")

# In-memory game sessions with TTL tracking
games: dict[str, tuple[float, GameState]] = {}  # (last_active_timestamp, state)
GAME_TTL = 24 * 3600  # 24 hours
MAX_SAVES_PER_GAME = 10


def _get_game(game_id: str) -> GameState | None:
    """Get game state, refreshing its TTL."""
    entry = games.get(game_id)
    if not entry:
        return None
    ts, state = entry
    # Check TTL
    if time.time() - ts > GAME_TTL:
        del games[game_id]
        return None
    # Refresh timestamp
    games[game_id] = (time.time(), state)
    return state


def _cleanup_stale_games():
    """Remove games that haven't been accessed for longer than TTL."""
    now = time.time()
    stale = [gid for gid, (ts, _) in games.items() if now - ts > GAME_TTL]
    for gid in stale:
        del games[gid]

DB_PATH = os.path.join(os.path.dirname(__file__), "saves.db")


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS saves (
            save_id TEXT PRIMARY KEY,
            save_name TEXT NOT NULL,
            game_state TEXT NOT NULL,
            saved_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


_init_db()


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/api/items")
def get_items():
    """Return item metadata registry for frontend use."""
    return game_engine.ITEM_REGISTRY


@app.get("/api/recipes")
def get_recipes():
    """Return crafting recipes for frontend use."""
    return game_engine.CRAFT_RECIPES


@app.get("/api/shelter/{game_id}")
def get_shelter(game_id: str):
    """Return shelter upgrade status for a game."""
    state = _get_game(game_id)
    if not state:
        raise HTTPException(404, "游戏不存在")
    return game_engine.get_shelter_info(state)


@app.post("/api/new-game")
def new_game():
    _cleanup_stale_games()
    state = game_engine.create_new_game()
    games[state.game_id] = (time.time(), state)
    return {
        "game_id": state.game_id,
        "state": state.model_dump(),
        "message": "新的一局开始了。在这个末日废土中，你能活多久？",
    }


@app.get("/api/game/{game_id}")
def get_game(game_id: str):
    state = _get_game(game_id)
    if not state:
        raise HTTPException(404, "游戏不存在")
    return state.model_dump()


@app.post("/api/game/{game_id}/action")
def do_action(game_id: str, action: Action):
    state = _get_game(game_id)
    if not state:
        raise HTTPException(404, "游戏不存在")

    if state.game_over:
        return {"events": [{"type": "info", "title": "游戏已结束", "description": "你的废土之旅已经终结。开始新游戏吧。"}], "state": state.model_dump()}

    events: list[Event] = []

    # If there's a pending combat, handle combat choices
    if state.pending_event and state.pending_event.type == "combat":
        if action.action_type in (ActionType.ATTACK, ActionType.DEFEND, ActionType.FLEE):
            combat_action = action.action_type.value
            if state.tower_siege_wave > 0:
                siege_events = game_engine.do_siege_combat(state, combat_action)
                events.extend(siege_events)
            else:
                evt = game_engine.do_combat_action(state, combat_action)
                events.append(evt)
        else:
            events.append(Event(type="error", title="战斗中", description="你正处于战斗中！请选择：攻击、防御或逃跑"))
    elif action.action_type == ActionType.EXPLORE:
        if state.player.energy < 15:
            events.append(Event(type="error", title="太疲惫了", description="你的体力不足以支撑探索活动。先休息一下吧。"))
        else:
            explore_events = game_engine.do_explore(state, action.target)
            events.extend(explore_events)
    elif action.action_type == ActionType.REST:
        events.append(game_engine.do_rest(state))
    elif action.action_type == ActionType.CRAFT:
        if not action.item_id:
            events.append(Event(type="error", title="未指定配方", description="请指定要合成的物品。可用：medicine, bandage, weapon"))
        else:
            events.append(game_engine.do_craft(state, action.item_id))
    elif action.action_type == ActionType.CHECK_INVENTORY:
        inv_desc = "=== 背包 ===\n"
        if not state.inventory:
            inv_desc += "空空如也……"
        else:
            for item in state.inventory:
                inv_desc += f"\n• {item.name} x{item.quantity} - {item.description}"
        events.append(Event(type="inventory", title="查看背包", description=inv_desc))
    elif action.action_type == ActionType.USE_ITEM:
        if not action.item_id:
            events.append(Event(type="error", title="未指定物品", description="请指定要使用的物品。"))
        else:
            events.append(game_engine.use_item(state, action.item_id))
    elif action.action_type == ActionType.MOVE:
        if not action.target or action.target not in game_engine.LOCATIONS:
            available = ", ".join(game_engine.LOCATIONS.keys())
            events.append(Event(type="error", title="未知地点", description=f"可前往的地点：{available}"))
        else:
            events.append(Event(type="move", title="移动", description=f"你向{game_engine.LOCATIONS[action.target]['name']}出发了。"))
            state.current_location = action.target
            if action.target not in state.explored_locations:
                state.explored_locations.append(action.target)
    elif action.action_type == ActionType.UPGRADE:
        if not action.item_id:
            events.append(Event(type="error", title="未指定设施", description="请指定要升级的设施。"))
        else:
            events.append(game_engine.do_upgrade(state, action.item_id))
    elif action.action_type == ActionType.INSPECT:
        if not action.target:
            events.append(Event(type="error", title="未指定目标", description="请指定要检查的物品。"))
        else:
            events.append(game_engine.do_inspect(state, action.target))
    else:
        events.append(Event(type="error", title="未知操作", description="无法理解你的行为。"))

    # Check win condition
    if game_engine.check_win_condition(state):
        events.append(Event(
            type="victory",
            title="逃离废土！",
            description=(
                "你将无线电零件组装到通讯塔的设备上，调整到正确的频率。\n\n"
                "\"这里是废土求生者，有人能听到吗？重复，有人能听到吗？\"\n\n"
                "漫长的沉默后，扬声器里传来了回应：\n"
                "\"收到！这里是北方幸存者基地！我们马上派人来接你！坚持住！\"\n\n"
                f"你在废土中存活了 {state.day} 天。你终于等到了希望。\n\n"
                "—— 游戏通关 ——"
            ),
        ))

    return {"events": [e.model_dump() for e in events], "state": state.model_dump()}


@app.post("/api/game/{game_id}/save")
def save_game(game_id: str):
    state = _get_game(game_id)
    if not state:
        raise HTTPException(404, "游戏不存在")
    save_id = f"save_{game_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    save_name = f"第{state.day}天 - HP:{state.player.hp}"
    saved_at = datetime.now().isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO saves (save_id, save_name, game_state, saved_at) VALUES (?, ?, ?, ?)",
            (save_id, save_name, state.model_dump_json(), saved_at),
        )
        # Limit: keep only the most recent MAX_SAVES_PER_GAME saves per game
        conn.execute(
            """DELETE FROM saves WHERE save_id IN (
                SELECT save_id FROM saves WHERE save_id LIKE ? ORDER BY saved_at DESC LIMIT -1 OFFSET ?
            )""",
            (f"save_{game_id}_%", MAX_SAVES_PER_GAME),
        )
        conn.commit()
    return {"save_id": save_id, "save_name": save_name, "saved_at": saved_at, "message": "游戏已保存。"}


@app.get("/api/saves")
def list_saves():
    with get_db() as conn:
        rows = conn.execute("SELECT save_id, save_name, saved_at FROM saves ORDER BY saved_at DESC").fetchall()
    return [{"save_id": r["save_id"], "save_name": r["save_name"], "saved_at": r["saved_at"]} for r in rows]


@app.get("/api/npcs/{game_id}")
def get_npcs(game_id: str):
    """获取当前地点的NPC列表"""
    state = _get_game(game_id)
    if not state:
        raise HTTPException(404, "游戏不存在")
    npcs = game_engine.get_location_npcs(state)
    return {"npcs": npcs, "location": state.current_location}


@app.get("/api/npc/{npc_id}")
def get_npc_info(npc_id: str):
    """获取NPC详细信息"""
    from .npcs import get_npc
    npc = get_npc(npc_id)
    if not npc:
        raise HTTPException(404, "NPC不存在")
    return npc


@app.post("/api/game/{game_id}/npc")
def npc_interaction(game_id: str, interaction: NPCInteraction):
    """NPC交互"""
    state = _get_game(game_id)
    if not state:
        raise HTTPException(404, "游戏不存在")
    
    if state.game_over:
        return {"events": [{"type": "info", "title": "游戏已结束", "description": "你的废土之旅已经终结。"}], "state": state.model_dump()}
    
    events = []
    
    if interaction.action == "talk":
        events.append(game_engine.do_npc_talk(state, interaction.npc_id))
    elif interaction.action == "trade_buy":
        if not interaction.item_id:
            events.append(Event(type="error", title="未指定物品", description="请指定要购买的物品。"))
        else:
            events.append(game_engine.do_npc_trade_buy(state, interaction.npc_id, interaction.item_id, interaction.quantity))
    elif interaction.action == "trade_sell":
        if not interaction.item_id:
            events.append(Event(type="error", title="未指定物品", description="请指定要出售的物品。"))
        else:
            events.append(game_engine.do_npc_trade_sell(state, interaction.npc_id, interaction.item_id, interaction.quantity))
    elif interaction.action == "hire":
        events.append(game_engine.do_npc_hire(state, interaction.npc_id))
    elif interaction.action == "heal":
        events.append(game_engine.do_npc_heal(state, interaction.npc_id))
    elif interaction.action == "bless":
        events.append(game_engine.do_npc_bless(state, interaction.npc_id))
    elif interaction.action == "repair":
        if not interaction.item_id:
            events.append(Event(type="error", title="未指定类型", description="请指定升级类型：weapon 或 armor"))
        else:
            events.append(game_engine.do_npc_repair(state, interaction.npc_id, interaction.item_id))
    elif interaction.action == "bounty":
        if not interaction.item_id:
            events.append(Event(type="error", title="未指定地点", description="请指定清剿目标地点"))
        else:
            events.append(game_engine.do_npc_bounty(state, interaction.npc_id, interaction.item_id))
    elif interaction.action == "herb_garden":
        if not interaction.item_id:
            events.append(Event(type="error", title="未指定操作", description="请指定操作：activate 或 deactivate"))
        else:
            events.append(game_engine.do_npc_herb_garden(state, interaction.npc_id, interaction.item_id))
    elif interaction.action == "intel":
        events.append(game_engine.do_npc_intel(state, interaction.npc_id))
    elif interaction.action == "scavenge":
        events.append(game_engine.do_npc_scavenge(state, interaction.npc_id))
    else:
        events.append(Event(type="error", title="未知操作", description="无法理解你的行为。"))
    
    # 检查佣兵到期
    merc_events = game_engine.check_mercenary_expire(state)
    events.extend(merc_events)
    
    # 检查赏金猎人效果到期
    bounty_events = game_engine.check_bounty_expire(state)
    events.extend(bounty_events)
    
    return {"events": [e.model_dump() for e in events], "state": state.model_dump()}


@app.post("/api/load/{save_id}")
def load_game(save_id: str):
    with get_db() as conn:
        row = conn.execute("SELECT game_state FROM saves WHERE save_id = ?", (save_id,)).fetchone()
    if not row:
        raise HTTPException(404, "存档不存在")
    state = GameState.model_validate_json(row["game_state"])
    games[state.game_id] = (time.time(), state)
    return {"game_id": state.game_id, "state": state.model_dump(), "message": f"已加载第{state.day}天的存档。"}


# ── Static files (frontend) ─────────────────────────────────────────────────
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
assets_dir = os.path.join(frontend_dir, "assets")
if os.path.isdir(frontend_dir):
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # 不拦截API请求
        if full_path.startswith("api/"):
            raise HTTPException(404, "API路由不存在")
        file_path = os.path.realpath(os.path.join(frontend_dir, full_path))
        # Prevent path traversal attacks
        if not file_path.startswith(os.path.realpath(frontend_dir)):
            raise HTTPException(404, "文件未找到")
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))
