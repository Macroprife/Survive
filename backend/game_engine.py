import random
import uuid
from .models import GameState, Player, Event, Item, ActionType


# ── Item Registry (single source of truth) ─────────────────────────────────
ITEM_REGISTRY = {
    "food":       {"name": "食物",   "usable": True,  "effect": "饱腹 +35"},
    "water":      {"name": "水",     "usable": True,  "effect": "水分 +40"},
    "medicine":   {"name": "药品",   "usable": True,  "effect": "HP +30"},
    "bandage":    {"name": "绷带",   "usable": True,  "effect": "HP +20"},
    "weapon":     {"name": "武器",   "usable": False, "effect": "攻击 +5"},
    "armor":      {"name": "护甲",   "usable": True,  "effect": "防御 12"},
    "torch":      {"name": "火把",   "usable": False, "effect": "降低遭遇率"},
    "tools":      {"name": "工具",   "usable": False, "effect": ""},
    "radio_parts": {"name": "无线电零件", "usable": False, "effect": "集齐3个前往通讯塔"},
    "cloth":      {"name": "布料",   "usable": False, "effect": ""},
    "wood":       {"name": "木头",   "usable": False, "effect": ""},
    "metal":      {"name": "金属",   "usable": False, "effect": ""},
    "alcohol":    {"name": "酒精",   "usable": False, "effect": ""},
    "herb":       {"name": "草药",   "usable": False, "effect": ""},
}


# ── Locations ────────────────────────────────────────────────────────────────
LOCATIONS = {
    "shelter": {
        "id": "shelter",
        "name": "废弃避难所",
        "description": "一间破旧但尚能遮风挡雨的地下室。墙壁上布满霉斑，角落里放着一张破旧的行军床。这里是你唯一的栖身之所。",
        "danger_level": "safe",
        "loot_table": [
            {"id": "cloth", "name": "破布条", "desc": "从旧衣服上撕下来的布条", "rate": 0.4},
            {"id": "wood", "name": "木板碎片", "desc": "从家具上拆下来的木头", "rate": 0.3},
        ],
        "encounter_rate": 0.05,
    },
    "supermarket": {
        "id": "supermarket",
        "name": "废弃超市",
        "description": "货架东倒西歪，地上散落着破碎的玻璃和腐烂的商品。空气中弥漫着一股酸臭味，但偶尔还能在角落里发现有用的物资。",
        "danger_level": "medium",
        "loot_table": [
            {"id": "food", "name": "罐头食品", "desc": "尚未过期的罐头，还能充饥", "rate": 0.35},
            {"id": "water", "name": "瓶装水", "desc": "密封完好的矿泉水", "rate": 0.30},
            {"id": "cloth", "name": "布料", "desc": "还算干净的布料", "rate": 0.20},
            {"id": "alcohol", "name": "酒精", "desc": "医用酒精，可以消毒", "rate": 0.10},
            {"id": "tools", "name": "简易工具", "desc": "螺丝刀和钳子", "rate": 0.05},
        ],
        "encounter_rate": 0.25,
    },
    "hospital": {
        "id": "hospital",
        "name": "市中心医院",
        "description": "白色的墙壁上布满了干涸的血迹。走廊尽头传来不明的声响。药品是最珍贵的资源，但这里也是最危险的地方之一。",
        "danger_level": "high",
        "loot_table": [
            {"id": "medicine", "name": "抗生素", "desc": "还能使用的消炎药物", "rate": 0.20},
            {"id": "bandage", "name": "医用绷带", "desc": "无菌包装的绷带", "rate": 0.25},
            {"id": "herb", "name": "草药", "desc": "晒干的草药，可以入药", "rate": 0.20},
            {"id": "alcohol", "name": "医用酒精", "desc": "高浓度酒精", "rate": 0.15},
            {"id": "water", "name": "蒸馏水", "desc": "纯净的蒸馏水", "rate": 0.10},
        ],
        "encounter_rate": 0.40,
    },
    "police_station": {
        "id": "police_station",
        "name": "警察局",
        "description": "大门半敞着，里面的文件散落一地。武器库的门被撬开了，但也许还有遗留的装备。这里经常有其他幸存者出没。",
        "danger_level": "high",
        "loot_table": [
            {"id": "weapon", "name": "警棍", "desc": "标准警用装备", "rate": 0.15},
            {"id": "armor", "name": "防刺背心", "desc": "虽然有些破损，但还能防护", "rate": 0.10},
            {"id": "metal", "name": "金属零件", "desc": "各种金属配件", "rate": 0.25},
            {"id": "tools", "name": "工具箱", "desc": "实用的工具套装", "rate": 0.15},
            {"id": "food", "name": "应急口粮", "desc": "警局储备的压缩饼干", "rate": 0.20},
        ],
        "encounter_rate": 0.45,
    },
    "residential": {
        "id": "residential",
        "name": "居民区废墟",
        "description": "曾经繁华的居民区如今只剩下断壁残垣。每栋楼都可能藏着物资，也可能藏着危险。小心翼翼地翻找着每一间屋子。",
        "danger_level": "medium",
        "loot_table": [
            {"id": "food", "name": "方便面", "desc": "还能吃的速食食品", "rate": 0.25},
            {"id": "water", "name": "桶装水", "desc": "大桶的饮用水", "rate": 0.20},
            {"id": "cloth", "name": "棉布", "desc": "从窗帘上扯下来的布", "rate": 0.15},
            {"id": "wood", "name": "木头", "desc": "家具拆下来的木料", "rate": 0.15},
            {"id": "metal", "name": "铁钉和铁丝", "desc": "各种金属碎片", "rate": 0.10},
            {"id": "herb", "name": "干草药", "desc": "阳台上枯萎的药用植物", "rate": 0.08},
            {"id": "radio_parts", "name": "电子元件", "desc": "从收音机里拆出来的零件", "rate": 0.05},
        ],
        "encounter_rate": 0.30,
    },
    "radio_tower": {
        "id": "radio_tower",
        "name": "通讯塔",
        "description": "高耸的通讯塔矗立在城市边缘，这里是向外求救的最后希望。但通往塔顶的道路危机四伏，只有做好充分准备的人才能到达。",
        "danger_level": "very_high",
        "loot_table": [
            {"id": "radio_parts", "name": "无线电元件", "desc": "完好的通讯设备零件", "rate": 0.30},
            {"id": "metal", "name": "铝材", "desc": "轻便结实的金属材料", "rate": 0.20},
            {"id": "tools", "name": "电工工具", "desc": "专业的电工套装", "rate": 0.15},
        ],
        "encounter_rate": 0.60,
    },
}

# ── Crafting ─────────────────────────────────────────────────────────────────
CRAFT_RECIPES = {
    "medicine": {"ingredients": [("herb", 1), ("water", 1)], "result": {"id": "medicine", "name": "草药药剂", "desc": "用草药和水熬制的药剂"}},
    "bandage": {"ingredients": [("cloth", 1), ("alcohol", 1)], "result": {"id": "bandage", "name": "消毒绷带", "desc": "用酒精消毒过的绷带"}},
    "weapon": {"ingredients": [("metal", 2), ("wood", 1)], "result": {"id": "weapon", "name": "自制武器", "desc": "用金属和木头打造的简易武器"}},
    "armor": {"ingredients": [("metal", 3), ("cloth", 2)], "result": {"id": "armor", "name": "强化护甲", "desc": "用金属片和布料缝制的防护装备"}},
    "torch": {"ingredients": [("wood", 1), ("cloth", 1)], "result": {"id": "torch", "name": "火把", "desc": "简易照明工具，探索时降低遭遇率"}},
}

# ── Random events ────────────────────────────────────────────────────────────
EXPLORE_EVENTS = [
    {
        "type": "find_supplies",
        "rate": 0.25,
        "titles": ["意外收获", "隐藏的宝物", "幸运发现"],
        "descriptions": [
            "你在一堆废墟下发现了一个密封的储物箱，里面居然还有完好的物资！",
            "一具早已冰冷的尸体旁散落着一个背包，你颤抖着手翻找了有用的物品。",
            "墙角的一个暗格里藏着一些物资，也许是之前的幸存者留下的。",
        ],
    },
    {
        "type": "hostile",
        "rate": 0.20,
        "titles": ["遭遇敌对幸存者", "危险的相遇", "武装匪徒"],
        "descriptions": [
            "三个眼神疯狂的人挡住了你的去路，他们手持利器，嘴里念叨着要把你的一切都抢走。",
            "一个满脸伤疤的男人从暗处冲出来，他的眼里只有疯狂和贪婪。",
            "你听到身后传来脚步声，转身看到一群人正向你逼近，他们手里拿着武器。",
        ],
    },
    {
        "type": "weather",
        "rate": 0.15,
        "titles": ["沙尘暴来袭", "酸雨降临", "浓雾弥漫"],
        "descriptions": [
            "远处天际卷起一片昏黄，沙尘暴正向这边席卷而来，你必须找个地方躲避！",
            "天空突然暗了下来，带着腐蚀性的雨滴开始落下。暴露在外会让你受伤。",
            "浓雾不知从何处升起，能见度骤降到几米之内。危险可能就潜伏在身边。",
        ],
    },
    {
        "type": "clue",
        "rate": 0.10,
        "titles": ["发现线索", "求救信号", "神秘标记"],
        "descriptions": [
            "墙上用红漆写着一行字：'通讯塔在东边，带上零件就能求救。'",
            "你捡到一张皱巴巴的纸条，上面画着一张简陋的地图，标注了通讯塔的位置。",
            "一台还能工作的收音机里传出断断续续的信号：'……通讯……频率……求救……'",
        ],
    },
    {
        "type": "trap",
        "rate": 0.10,
        "titles": ["陷阱！", "暗藏杀机", "致命圈套"],
        "descriptions": [
            "你的脚突然踩空，整个人跌入一个伪装过的陷坑！尖锐的木刺扎进了你的小腿。",
            "一根绊线触发了简易的弓箭装置，一支箭擦过你的手臂。",
            "地板突然塌陷，你抓住了边缘才没有掉下去，但手指已经磨破了皮。",
        ],
    },
]


def create_new_game() -> GameState:
    game_id = str(uuid.uuid4())[:8]
    player = Player()
    inventory = [
        Item(id="food", name="压缩饼干", description="一块干硬的压缩饼干", quantity=2),
        Item(id="water", name="矿泉水", description="一瓶半满的矿泉水", quantity=2),
    ]
    initial_event = Event(
        type="narrative",
        title="末日求生",
        description=(
            "核战后的第三十天。\n\n"
            "你从避难所的废墟中醒来，外面的世界已经面目全非。"
            "天空永远是灰蒙蒙的，空气中弥漫着尘埃和腐朽的气息。\n\n"
            "你的食物和水所剩无几。在废墟中，也许还能找到生存的物资。"
            "你听说城市的东边有一座通讯塔，如果能修好它，也许能联系到其他幸存者……\n\n"
            "但首先，你需要活下去。"
        ),
    )
    return GameState(
        game_id=game_id,
        player=player,
        inventory=inventory,
        events_log=[initial_event],
    )


def get_item_name(item_id: str) -> str:
    meta = ITEM_REGISTRY.get(item_id)
    return meta["name"] if meta else item_id


def _add_item(inventory: list[Item], item_id: str, name: str, desc: str, qty: int = 1):
    for item in inventory:
        if item.id == item_id:
            item.quantity += qty
            return
    inventory.append(Item(id=item_id, name=name, description=desc, quantity=qty))


def _has_item(inventory: list[Item], item_id: str, qty: int = 1) -> bool:
    for item in inventory:
        if item.id == item_id and item.quantity >= qty:
            return True
    return False


def _consume_item(inventory: list[Item], item_id: str, qty: int = 1):
    for item in inventory:
        if item.id == item_id:
            item.quantity -= qty
            if item.quantity <= 0:
                inventory.remove(item)
            return


def _clamp(val: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, val))


def _day_scale(state: GameState) -> float:
    """Difficulty multiplier that increases with day number. Caps at 1.5x."""
    return 1.0 + min(state.day * 0.03, 0.5)


def apply_daily_consumption(state: GameState) -> list[Event]:
    events = []
    p = state.player
    p.hunger = _clamp(p.hunger - 15)
    p.thirst = _clamp(p.thirst - 20)
    p.energy = _clamp(p.energy - 10)
    p.sanity = _clamp(p.sanity - 5)

    if p.hunger == 0:
        p.hp = _clamp(p.hp - 10)
        events.append(Event(type="damage", title="饥饿侵蚀", description="你已经很久没有进食了，饥饿像野兽一样啃噬着你的身体。生命值 -10"))
    if p.thirst == 0:
        p.hp = _clamp(p.hp - 15)
        events.append(Event(type="damage", title="脱水危机", description="你的嘴唇干裂，视线模糊。没有水，你撑不了多久了。生命值 -15"))
    if p.sanity == 0:
        bad = random.choice([
            ("精神崩溃", "你开始对着墙壁自言自语，分不清现实和幻觉。你浪费了一整天的时间。"),
            ("噩梦连连", "即使在休息时，噩梦也不断侵袭。你惊醒后发现自己弄伤了自己。生命值 -5"),
            ("暴怒发作", "一股无名的怒火涌上心头，你砸毁了身边的一些物资。"),
        ])
        events.append(Event(type="sanity_break", title=bad[0], description=bad[1]))
        if "生命值" in bad[1]:
            p.hp = _clamp(p.hp - 5)
        # 暴怒发作：随机移除 1~2 个物品
        if "砸毁" in bad[1] and state.inventory:
            remove_count = min(random.randint(1, 2), len(state.inventory))
            removed = []
            for _ in range(remove_count):
                victim = random.choice(state.inventory)
                removed.append(victim.name)
                state.inventory.remove(victim)
            events.append(Event(type="damage", title="物资损失", description=f"被砸毁的物品：{'、'.join(removed)}"))

    if p.hunger > 0 and p.thirst > 0:
        events.append(Event(
            type="daily",
            title=f"第 {state.day} 天",
            description=f"新的一天。你感到{'疲惫' if p.energy < 30 else '还行'}，"
                        f"{'饥肠辘辘' if p.hunger < 30 else '不太饿'}，"
                        f"{'口渴难耐' if p.thirst < 30 else '还能忍受'}。"
        ))
    return events


def use_item(state: GameState, item_id: str) -> Event:
    p = state.player
    if not _has_item(state.inventory, item_id):
        return Event(type="error", title="物品不足", description=f"你没有{get_item_name(item_id)}。")

    if item_id == "food":
        _consume_item(state.inventory, "food")
        p.hunger = _clamp(p.hunger + 35)
        return Event(type="use", title="进食", description="你打开罐头，狼吞虎咽地吃了下去。饥饿感稍微缓解了一些。饱腹感 +35")
    elif item_id == "water":
        _consume_item(state.inventory, "water")
        p.thirst = _clamp(p.thirst + 40)
        return Event(type="use", title="饮水", description="清凉的水流入干涸的喉咙，你感到一阵舒爽。水分 +40")
    elif item_id == "medicine":
        _consume_item(state.inventory, "medicine")
        p.hp = _clamp(p.hp + 30)
        return Event(type="use", title="服药", description="你吞下了药片，感觉身体在慢慢恢复。生命值 +30")
    elif item_id == "bandage":
        _consume_item(state.inventory, "bandage")
        p.hp = _clamp(p.hp + 20)
        return Event(type="use", title="包扎伤口", description="你小心地用绷带包扎好伤口，血止住了。生命值 +20")
    elif item_id == "armor":
        _consume_item(state.inventory, "armor")
        p.has_armor = True
        p.defense = 12
        return Event(type="equip", title="装备护甲", description="你穿上了防刺背心，感到安全了一些。防御力提升。")
    else:
        return Event(type="error", title="无法使用", description=f"{get_item_name(item_id)}无法在此时使用。")


def do_rest(state: GameState) -> Event:
    p = state.player
    p.energy = _clamp(p.energy + 40)
    p.sanity = _clamp(p.sanity + 10)
    p.hp = _clamp(p.hp + 5)
    state.day += 1
    daily_events = apply_daily_consumption(state)
    desc = "你在避难所里休息了一段时间，恢复了一些体力和精神。"
    if state.player.hp <= 0:
        state.game_over = True
        state.game_over_reason = "你在睡梦中再也没有醒来……"
        return Event(type="game_over", title="死亡", description=state.game_over_reason)
    return Event(type="rest", title="休息", description=desc, effects={"energy": "+40", "sanity": "+10", "hp": "+5"})


def do_explore(state: GameState, location_id: str | None = None) -> list[Event]:
    events = []
    p = state.player

    if p.energy < 15:
        return [Event(type="error", title="太疲惫了", description="你的体力不足以支撑探索活动。先休息一下吧。")]

    target = location_id or state.current_location
    loc = LOCATIONS.get(target)
    if not loc:
        return [Event(type="error", title="未知地点", description="你不知道这个地方在哪里。")]

    if target not in state.explored_locations:
        state.explored_locations.append(target)

    state.current_location = target
    p.energy = _clamp(p.energy - 20)

    # Location description
    events.append(Event(type="move", title=loc["name"], description=loc["description"]))

    # Tower siege check — if at radio_tower with 3+ parts, start siege instead of normal explore
    if target == "radio_tower" and _count_item(state.inventory, "radio_parts") >= 3 and state.tower_siege_wave == 0:
        state.tower_siege_wave = 1
        siege_mult = _day_scale(state)
        enemy_hp = int(random.randint(30, 45) * siege_mult)
        events.append(Event(
            type="narrative", title="通讯塔保卫战",
            description=(
                "你将无线电零件插入通讯塔的设备，开始调试频率。\n\n"
                "但设备启动的信号引来了废土上的掠夺者——他们也想控制这座通讯塔！\n\n"
                "守卫通讯塔，击退所有敌人才能完成求救！")))
        siege_event = Event(
            type="combat", title="第一波进攻！",
            description="拾荒者从四面八方涌来！\n\n⚔️ 攻击 | 🛡️ 防御 | 🏃 逃跑（= 放弃守塔）",
            effects={"enemy": "拾荒者突击队", "enemy_hp": enemy_hp},
            resolved=False)
        state.pending_event = siege_event
        events.append(siege_event)
        return events

    # Danger check (torch halves encounter rate, day scales difficulty)
    has_torch = _has_item(state.inventory, "torch")
    day_mult = _day_scale(state)
    effective_rate = loc["encounter_rate"] * (0.5 if has_torch else 1.0) * day_mult
    danger_roll = random.random()
    if danger_roll < effective_rate:
        event = _generate_encounter(state, loc["danger_level"])
        events.append(event)
        if event.type == "combat" and not event.resolved:
            state.pending_event = event  # Set pending combat for player choice
            return events  # wait for player choice

    # Loot check
    loot_roll = random.random()
    if loot_roll < 0.6:
        for loot in loc["loot_table"]:
            if random.random() < loot["rate"]:
                _add_item(state.inventory, loot["id"], loot["name"], loot["desc"])
                events.append(Event(type="loot", title="发现物资", description=f"你找到了 {loot['name']}！({loot['desc']})"))
                break

    # Random event
    if random.random() < 0.3:
        evt = _generate_random_event(state)
        if evt:
            events.append(evt)
            # If random event triggered combat, wait for player choice
            if evt.type == "combat" and not evt.resolved:
                state.pending_event = evt
                return events

    # Day advance
    state.day += 1
    daily_events = apply_daily_consumption(state)
    events.extend(daily_events)

    # Score
    state.survival_score = state.day * 10 + p.hp + sum(i.quantity for i in state.inventory) * 2

    if p.hp <= 0:
        state.game_over = True
        state.game_over_reason = "你在废土中倒下了，再也没有站起来。"
        events.append(Event(type="game_over", title="死亡", description=state.game_over_reason))

    return events


def _generate_encounter(state: GameState, danger: str) -> Event:
    encounter_types = ["hostile", "weather", "trap"]
    weights = {"safe": [0.02, 0.02, 0.01], "medium": [0.15, 0.08, 0.07],
               "high": [0.25, 0.08, 0.07], "very_high": [0.35, 0.15, 0.10]}
    w = weights.get(danger, weights["medium"])
    etype = random.choices(encounter_types, weights=w, k=1)[0]

    if etype == "hostile":
        names = ["疯狂的拾荒者", "武装匪徒", "变异的流浪汉", "绝望的幸存者"]
        enemy = random.choice(names)
        day_mult = _day_scale(state)
        enemy_hp = int(random.randint(20, 50) * day_mult)
        return Event(
            type="combat", title="遭遇敌人！",
            description=f"{enemy}出现在你面前！他看起来充满敌意，手里握着武器。\n\n你需要做出选择：\n⚔️ 攻击 - 与敌人战斗\n🛡️ 防御 - 减少受到的伤害\n🏃 逃跑 - 尝试逃离（可能失败）",
            effects={"enemy": enemy, "enemy_hp": enemy_hp},
            resolved=False,
        )
    elif etype == "weather":
        weather_events = [
            ("沙尘暴", "漫天黄沙席卷而来，能见度几乎为零。你的皮肤被砂砾刮得生疼。", {"energy": -10, "hp": -5}),
            ("酸雨", "带着腐蚀性的雨滴打在身上，你赶紧寻找遮蔽处。", {"hp": -8}),
            ("浓雾", "浓雾笼罩了一切，你在迷失中消耗了大量体力。", {"energy": -15}),
        ]
        wev = random.choice(weather_events)
        p = state.player
        p.hp = _clamp(p.hp + wev[2].get("hp", 0))
        p.energy = _clamp(p.energy + wev[2].get("energy", 0))
        return Event(type="weather", title=wev[0], description=wev[1], effects=wev[2])
    else:
        trap_dmg = random.randint(10, 25)
        state.player.hp = _clamp(state.player.hp - trap_dmg)
        traps = [
            f"你踩到了一个隐蔽的捕兽夹，尖齿刺穿了你的脚踝。生命值 -{trap_dmg}",
            f"一根绊线触发了弩箭装置，箭矢射中了你的肩膀。生命值 -{trap_dmg}",
            f"脚下的地板突然塌陷，你跌了下去，摔伤了。生命值 -{trap_dmg}",
        ]
        return Event(type="trap", title="陷阱！", description=random.choice(traps), effects={"hp": -trap_dmg})


def _generate_random_event(state: GameState) -> Event | None:
    chosen = random.choices(EXPLORE_EVENTS, weights=[e["rate"] for e in EXPLORE_EVENTS], k=1)[0]
    etype = chosen["type"]
    title = random.choice(chosen["titles"])
    desc = random.choice(chosen["descriptions"])

    if etype == "find_supplies":
        possible = [("food", "罐头食品"), ("water", "瓶装水"), ("cloth", "布料"),
                     ("herb", "草药"), ("metal", "金属碎片")]
        item = random.choice(possible)
        _add_item(state.inventory, item[0], item[1], "在废墟中找到的物资")
        return Event(type="loot", title=title, description=f"{desc}\n\n你获得了 {item[1]}！")
    elif etype == "clue":
        # Add a radio_parts item to inventory (win condition checks inventory count)
        _add_item(state.inventory, "radio_parts", "无线电零件", "通过线索找到的通讯设备零件")
        return Event(type="clue", title=title, description=f"{desc}\n\n（获得无线电零件！）")
    elif etype == "hostile":
        enemy = random.choice(["疯狂的拾荒者", "武装匪徒", "绝望的幸存者"])
        enemy_hp = random.randint(15, 35)
        return Event(
            type="combat", title=title,
            description=f"{desc}\n\n你需要做出选择：\n⚔️ 攻击 - 与敌人战斗\n🛡️ 防御 - 减少受到的伤害\n🏃 逃跑 - 尝试逃离（可能失败）",
            effects={"enemy": enemy, "enemy_hp": enemy_hp},
            resolved=False,
        )
    elif etype == "weather":
        dmg = random.randint(3, 10)
        state.player.hp = _clamp(state.player.hp - dmg)
        return Event(type="weather", title=title, description=f"{desc}\n\n生命值 -{dmg}", effects={"hp": -dmg})
    elif etype == "trap":
        trap_dmg = random.randint(5, 15)
        state.player.hp = _clamp(state.player.hp - trap_dmg)
        return Event(type="trap", title=title, description=f"{desc}\n\n生命值 -{trap_dmg}", effects={"hp": -trap_dmg})
    return None


def do_combat_action(state: GameState, action: str) -> Event:
    evt = state.pending_event
    if not evt or evt.type != "combat":
        return Event(type="error", title="没有战斗", description="当前没有进行中的战斗。")

    p = state.player
    enemy_hp = evt.effects.get("enemy_hp", 30)
    enemy_name = evt.effects.get("enemy", "敌人")
    enemy_atk = random.randint(8, 18)
    player_atk = p.attack_power + (5 if p.has_weapon else 0)

    if action == "attack":
        dmg = random.randint(player_atk - 3, player_atk + 5)
        enemy_hp -= dmg
        recv = max(0, random.randint(enemy_atk - 3, enemy_atk + 3) - (p.defense if p.has_armor else 0))
        p.hp = _clamp(p.hp - recv)
        if enemy_hp <= 0:
            state.pending_event = None
            loot = random.choice([("food", "补给品"), ("water", "饮用水"), ("metal", "金属碎片")])
            _add_item(state.inventory, loot[0], loot[1], f"从{enemy_name}身上搜刮的")
            return Event(type="combat_end", title="战斗胜利！",
                         description=f"你击倒了{enemy_name}！你在他的遗物中找到了 {loot[1]}。\n受到伤害：-{recv}")
        else:
            evt.effects["enemy_hp"] = enemy_hp
            state.pending_event = evt
            return Event(type="combat", title="战斗继续",
                         description=f"你对{enemy_name}造成了 {dmg} 点伤害！但你也受到了 {recv} 点伤害。\n\n敌人剩余生命：{enemy_hp}\n你的生命：{p.hp}\n\n继续攻击？防御？还是逃跑？",
                         effects={"enemy_hp": enemy_hp}, resolved=False)

    elif action == "defend":
        recv = max(0, random.randint(2, 8) - (p.defense if p.has_armor else 0))
        p.hp = _clamp(p.hp - recv)
        p.energy = _clamp(p.energy - 5)
        return Event(type="combat", title="防御姿态",
                     description=f"你举起防御，减少了受到的伤害。只受到了 {recv} 点伤害。\n\n你的生命：{p.hp}",
                     effects={"enemy_hp": enemy_hp}, resolved=False)

    elif action == "flee":
        if random.random() < 0.6:
            state.pending_event = None
            p.energy = _clamp(p.energy - 15)
            return Event(type="flee", title="成功逃脱", description=f"你转身就跑，成功甩掉了{enemy_name}！但你消耗了不少体力。")
        else:
            recv = random.randint(enemy_atk, enemy_atk + 10)
            p.hp = _clamp(p.hp - recv)
            return Event(type="combat", title="逃跑失败！",
                         description=f"你试图逃跑，但{enemy_name}拦住了你的去路，并对你造成了 {recv} 点伤害！\n\n你的生命：{p.hp}",
                         effects={"enemy_hp": enemy_hp}, resolved=False)

    return Event(type="error", title="无效操作", description="未知的战斗操作。")


def do_siege_combat(state: GameState, action: str) -> list[Event]:
    """Handle combat during tower siege. Returns list of events."""
    evt = state.pending_event
    if not evt or evt.type != "combat":
        return [Event(type="error", title="没有战斗", description="当前没有进行中的战斗。")]

    p = state.player
    enemy_hp = evt.effects.get("enemy_hp", 30)
    enemy_name = evt.effects.get("enemy", "敌人")
    enemy_atk = random.randint(10, 20)
    player_atk = p.attack_power + (5 if p.has_weapon else 0)
    siege_mult = _day_scale(state)

    if action == "attack":
        dmg = random.randint(player_atk - 3, player_atk + 5)
        enemy_hp -= dmg
        recv = max(0, random.randint(enemy_atk - 3, enemy_atk + 3) - (p.defense if p.has_armor else 0))
        p.hp = _clamp(p.hp - recv)

        if p.hp <= 0:
            state.pending_event = None
            state.game_over = True
            state.game_over_reason = "你在通讯塔保卫战中倒下了……求救信号未能发出。"
            return [Event(type="game_over", title="死亡", description=state.game_over_reason)]

        if enemy_hp <= 0:
            state.tower_siege_wave += 1
            state.pending_event = None

            if state.tower_siege_wave > 3:
                # Victory! Consume parts
                _consume_item(state.inventory, "radio_parts", 3)
                state.game_over = True
                state.ending_reached = True
                state.game_over_reason = "good"
                return [Event(
                    type="victory", title="求救成功！",
                    description=(
                        "你击退了所有掠夺者，成功启动了通讯设备！\n\n"
                        "\"这里是废土求生者，有人能听到吗？重复，有人能听到吗？\"\n\n"
                        "漫长的沉默后，扬声器里传来了回应：\n"
                        "\"收到！这里是北方幸存者基地！我们马上派人来接你！坚持住！\"\n\n"
                        f"你在废土中存活了 {state.day} 天。你终于等到了希望。\n\n"
                        "—— 游戏通关 ——"))]

            # Next wave
            wave_info = {
                2: ("武装匪徒精锐", 40, 60),
                3: ("掠夺者首领", 55, 75),
            }
            next_name, lo, hi = wave_info[state.tower_siege_wave]
            next_hp = int(random.randint(lo, hi) * siege_mult)

            result = [Event(
                type="combat_end", title=f"第{state.tower_siege_wave - 1}波击退！",
                description=f"你击倒了{enemy_name}！受到伤害：-{recv}\n\n但下一波已经来了……")]

            next_combat = Event(
                type="combat", title=f"第{state.tower_siege_wave}波进攻！",
                description=f"{next_name}出现了！\n\n⚔️ 攻击 | 🛡️ 防御 | 🏃 逃跑（= 放弃守塔）",
                effects={"enemy": next_name, "enemy_hp": next_hp},
                resolved=False)
            state.pending_event = next_combat
            result.append(next_combat)
            return result

        else:
            evt.effects["enemy_hp"] = enemy_hp
            state.pending_event = evt
            return [Event(type="combat", title="战斗继续",
                         description=f"你对{enemy_name}造成了 {dmg} 点伤害！但你也受到了 {recv} 点伤害。\n\n敌人剩余生命：{enemy_hp}\n你的生命：{p.hp}",
                         effects={"enemy_hp": enemy_hp}, resolved=False)]

    elif action == "defend":
        recv = max(0, random.randint(2, 8) - (p.defense if p.has_armor else 0))
        p.hp = _clamp(p.hp - recv)
        p.energy = _clamp(p.energy - 5)

        if p.hp <= 0:
            state.pending_event = None
            state.game_over = True
            state.game_over_reason = "你在通讯塔保卫战中倒下了……求救信号未能发出。"
            return [Event(type="game_over", title="死亡", description=state.game_over_reason)]

        return [Event(type="combat", title="防御姿态",
                     description=f"你举起防御，减少了受到的伤害。只受到了 {recv} 点伤害。\n\n你的生命：{p.hp}",
                     effects={"enemy_hp": enemy_hp}, resolved=False)]

    elif action == "flee":
        state.pending_event = None
        state.tower_siege_wave = 0
        p.energy = _clamp(p.energy - 15)
        return [Event(type="flee", title="放弃守塔",
                     description="你逃离了通讯塔，放弃了这次求救机会。\n也许下次准备更充分再来……")]

    return [Event(type="error", title="无效操作", description="未知的战斗操作。")]


def do_craft(state: GameState, recipe_id: str) -> Event:
    recipe = CRAFT_RECIPES.get(recipe_id)
    if not recipe:
        return Event(type="error", title="未知配方", description="你不知道这个配方。可用配方：medicine, bandage, weapon")

    for item_id, qty in recipe["ingredients"]:
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="材料不足",
                         description=f"合成{get_item_name(recipe_id)}需要：" +
                         "、".join(f"{get_item_name(i)}x{q}" for i, q in recipe["ingredients"]))

    for item_id, qty in recipe["ingredients"]:
        _consume_item(state.inventory, item_id, qty)

    res = recipe["result"]
    _add_item(state.inventory, res["id"], res["name"], res["desc"])

    if res["id"] == "weapon":
        state.player.has_weapon = True
        state.player.attack_power = 18

    return Event(type="craft", title="合成成功",
                 description=f"你成功制作了 {res['name']}！({res['desc']})")


def _count_item(inventory: list[Item], item_id: str) -> int:
    """Count total quantity of an item in inventory."""
    for item in inventory:
        if item.id == item_id:
            return item.quantity
    return 0


def check_win_condition(state: GameState) -> bool:
    if state.game_over:
        return False
    # Victory requires: at radio_tower, siege completed (wave > 3), and parts available
    if (state.tower_siege_wave > 3 and
            state.current_location == "radio_tower" and
            _count_item(state.inventory, "radio_parts") >= 3):
        _consume_item(state.inventory, "radio_parts", 3)
        state.game_over = True
        state.ending_reached = True
        state.game_over_reason = "good"
        return True
    return False
