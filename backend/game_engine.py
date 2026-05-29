import random
import uuid
from .models import GameState, Player, Event, Item, ActionType


# ── Item Registry (single source of truth) ─────────────────────────────────
ITEM_REGISTRY = {
    "food":       {"name": "食物",   "usable": True,  "effect": "饱腹 +35"},
    "water":      {"name": "水",     "usable": True,  "effect": "水分 +40"},
    "medicine":   {"name": "药品",   "usable": True,  "effect": "HP +30"},
    "bandage":    {"name": "绷带",   "usable": True,  "effect": "HP +20"},
    "weapon":     {"name": "武器",   "usable": True,  "effect": "攻击 18"},
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

# ── Shelter Upgrades ──────────────────────────────────────────────────────
UPGRADE_RECIPES = {
    "rain_collector": {
        "name": "雨水收集器",
        "desc": "利用雨水净化设备，每天自动收集水分",
        "cost": [("metal", 2), ("wood", 2)],
        "bonus": "每天清晨自动产出 1 瓶水",
    },
    "garden": {
        "name": "无土药草槽",
        "desc": "在避难所内培育废土草药",
        "cost": [("wood", 2), ("herb", 1)],
        "bonus": "每天清晨自动产出 1 个草药",
    },
    "bed": {
        "name": "强化床铺",
        "desc": "用木板和布料搭建的舒适床铺",
        "cost": [("wood", 2), ("cloth", 2)],
        "bonus": "休息时额外恢复 HP +10、理智 +5",
    },
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

    # ── Shelter upgrade daily yields ──
    upgrades = state.shelter_upgrades
    if upgrades.get("rain_collector", 0) > 0:
        _add_item(state.inventory, "water", "瓶装水", "雨水收集器净化的水")
        events.append(Event(type="shelter", title="雨水收集器",
                            description="清晨，雨水收集器滴滴答答地工作着。你获得了一瓶净化水。"))
    if upgrades.get("garden", 0) > 0:
        _add_item(state.inventory, "herb", "草药", "避难所药草槽种植的草药")
        events.append(Event(type="shelter", title="药草槽",
                            description="药草槽里的植物长势喜人。你收获了一株草药。"))
    
    # ── 草药园每日产出 ──
    herb_events = check_herb_garden(state)
    events.extend(herb_events)

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
    elif item_id == "weapon":
        _consume_item(state.inventory, "weapon")
        p.has_weapon = True
        p.attack_power = 18
        return Event(type="equip", title="装备武器", description="你装备了自制武器，感觉自己更有力量了。基础攻击提升至 18。")
    else:
        return Event(type="error", title="无法使用", description=f"{get_item_name(item_id)}无法在此时使用。")


def do_rest(state: GameState) -> Event:
    p = state.player
    p.energy = _clamp(p.energy + 40)
    p.sanity = _clamp(p.sanity + 10)
    p.hp = _clamp(p.hp + 5)

    # Bed upgrade bonus
    bed_desc = ""
    if state.shelter_upgrades.get("bed", 0) > 0:
        p.hp = _clamp(p.hp + 10)
        p.sanity = _clamp(p.sanity + 5)
        bed_desc = " 强化床铺让你睡得更香，额外恢复了 HP +10、理智 +5。"

    state.day += 1
    daily_events = apply_daily_consumption(state)
    desc = "你在避难所里休息了一段时间，恢复了一些体力和精神。" + bed_desc
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


def do_upgrade(state: GameState, upgrade_id: str) -> Event:
    """Upgrade a shelter facility."""
    recipe = UPGRADE_RECIPES.get(upgrade_id)
    if not recipe:
        available = ", ".join(UPGRADE_RECIPES.keys())
        return Event(type="error", title="未知设施", description=f"没有这个基建项目。可用：{available}")

    current_level = state.shelter_upgrades.get(upgrade_id, 0)
    if current_level >= 3:
        return Event(type="error", title="已满级", description=f"{recipe['name']}已达到最高等级。")

    # Check and consume ingredients
    for item_id, qty in recipe["cost"]:
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="材料不足",
                         description=f"升级{recipe['name']}需要：" +
                         "、".join(f"{get_item_name(i)}x{q}" for i, q in recipe["cost"]))

    for item_id, qty in recipe["cost"]:
        _consume_item(state.inventory, item_id, qty)

    state.shelter_upgrades[upgrade_id] = current_level + 1
    new_level = current_level + 1

    return Event(
        type="upgrade", title=f"{recipe['name']} Lv.{new_level}",
        description=f"你完成了避难所改造——{recipe['name']}升级到了 Lv.{new_level}！\n{recipe['desc']}。{recipe['bonus']}"
    )


def get_shelter_info(state: GameState) -> dict:
    """Return shelter upgrade status for API/frontend use."""
    result = {}
    for uid, recipe in UPGRADE_RECIPES.items():
        level = state.shelter_upgrades.get(uid, 0)
        cost_str = "、".join(f"{get_item_name(i)}x{q}" for i, q in recipe["cost"])
        result[uid] = {
            "name": recipe["name"],
            "desc": recipe["desc"],
            "bonus": recipe["bonus"],
            "level": level,
            "max_level": 3,
            "cost": recipe["cost"],
            "cost_str": cost_str,
        }
    return result


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


# ── NPC System ───────────────────────────────────────────────────────────────
from .npcs import get_npc, get_npcs_by_location, NPC_REGISTRY


def get_location_npcs(state: GameState) -> list[dict]:
    """获取当前地点的NPC列表，包含好感度信息"""
    npcs = get_npcs_by_location(state.current_location)
    result = []
    for npc in npcs:
        npc_info = npc.copy()
        npc_info["met"] = npc["id"] in state.npc_met
        npc_info["relationship"] = state.npc_relationships.get(npc["id"], 0)
        result.append(npc_info)
    return result


def do_npc_talk(state: GameState, npc_id: str) -> Event:
    """与NPC对话"""
    npc = get_npc(npc_id)
    if not npc:
        return Event(type="error", title="NPC不存在", description="找不到这个幸存者。")
    
    # 检查是否在同一个地点
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    # 标记已遇到
    if npc_id not in state.npc_met:
        state.npc_met.append(npc_id)
        state.npc_relationships[npc_id] = 0
        dialogue = npc["dialogue"]["first_meet"]
        return Event(
            type="npc_meet",
            title=f"遇到 {npc['name']}",
            description=f"【{npc['faction']}】\n\n{npc['personality']}\n\n\"{dialogue}\"",
            effects={"npc_id": npc_id, "relationship": 0}
        )
    else:
        # 随机闲聊
        import random
        muttering = random.choice(npc["dialogue"]["idle_muttering"])
        rel = state.npc_relationships.get(npc_id, 0)
        
        if rel >= 50:
            attitude = "友善"
        elif rel >= 20:
            attitude = "中立"
        elif rel >= 0:
            attitude = "冷淡"
        else:
            attitude = "敌对"
        
        return Event(
            type="npc_talk",
            title=f"与 {npc['name']} 对话",
            description=f"【态度：{attitude}】\n\n\"{muttering}\"",
            effects={"npc_id": npc_id, "relationship": rel}
        )


def do_npc_trade_buy(state: GameState, npc_id: str, item_id: str, quantity: int = 1) -> Event:
    """从NPC处购买物品"""
    npc = get_npc(npc_id)
    if not npc:
        return Event(type="error", title="NPC不存在", description="找不到这个幸存者。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    trade = npc.get("trade_table", {}).get("buy", {})
    if item_id not in trade:
        return Event(type="error", title="物品不存在", description=f"{npc['name']}不卖这个东西。")
    
    item_info = trade[item_id]
    total_cost = item_info["price"] * quantity
    
    # 检查库存
    if item_info.get("stock", 0) < quantity:
        return Event(type="error", title="库存不足", description=f"{npc['name']}没有那么多{get_item_name(item_id)}。")
    
    # 检查玩家是否有足够的食物/水作为货币
    # 这里简化为用食物作为通用货币
    if not _has_item(state.inventory, "food", total_cost):
        return Event(type="error", title="物资不足", 
                     description=f"需要{total_cost}个食物来购买。你没有那么多。")
    
    # 执行交易
    _consume_item(state.inventory, "food", total_cost)
    _add_item(state.inventory, item_id, get_item_name(item_id), f"从{npc['name']}处购买")
    
    # 增加好感度
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 2
    
    return Event(
        type="npc_trade",
        title="交易成功",
        description=f"你用{total_cost}个食物从{npc['name']}处购买了{quantity}个{get_item_name(item_id)}。\n\n\"{npc['dialogue']['trade_success']}\"",
        effects={"npc_id": npc_id, "relationship": state.npc_relationships[npc_id]}
    )


def do_npc_trade_sell(state: GameState, npc_id: str, item_id: str, quantity: int = 1) -> Event:
    """向NPC出售物品"""
    npc = get_npc(npc_id)
    if not npc:
        return Event(type="error", title="NPC不存在", description="找不到这个幸存者。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    trade = npc.get("trade_table", {}).get("sell", {})
    if item_id not in trade:
        return Event(type="error", title="不收此物", description=f"{npc['name']}不收这个东西。")
    
    if not _has_item(state.inventory, item_id, quantity):
        return Event(type="error", title="物品不足", description=f"你没有那么多{get_item_name(item_id)}。")
    
    price = trade[item_id]["price"]
    total_gain = price * quantity
    
    # 执行交易
    _consume_item(state.inventory, item_id, quantity)
    _add_item(state.inventory, "food", "食物", f"卖给{npc['name']}获得", total_gain)
    
    # 增加好感度
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 1
    
    return Event(
        type="npc_trade",
        title="交易成功",
        description=f"你向{npc['name']}出售了{quantity}个{get_item_name(item_id)}，获得{total_gain}个食物。\n\n\"{npc['dialogue']['trade_success']}\"",
        effects={"npc_id": npc_id, "relationship": state.npc_relationships[npc_id]}
    )


def do_npc_hire(state: GameState, npc_id: str) -> Event:
    """雇佣佣兵（仅安娜）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_002":
        return Event(type="error", title="无法雇佣", description="这个NPC不能被雇佣。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    if state.hired_mercenary:
        return Event(type="error", title="已有佣兵", description="你已经雇佣了佣兵，不能同时雇佣多人。")
    
    merc = npc.get("mercenary", {})
    cost = merc.get("hire_cost", {})
    
    # 检查物资
    for item_id, qty in cost.items():
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="物资不足", 
                         description=f"雇佣{npc['name']}需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
    
    # 扣除物资
    for item_id, qty in cost.items():
        _consume_item(state.inventory, item_id, qty)
    
    state.hired_mercenary = npc_id
    state.mercenary_expire_day = state.day + merc.get("duration", 3)
    state.player.attack_power += merc.get("attack_bonus", 0)
    state.player.defense += merc.get("defense_bonus", 0)
    
    return Event(
        type="npc_hire",
        title=f"雇佣 {npc['name']}",
        description=f"你成功雇佣了{npc['name']}！她将在{merc.get('duration', 3)}天内保护你。\n\n攻击 +{merc.get('attack_bonus', 0)}，防御 +{merc.get('defense_bonus', 0)}",
        effects={"npc_id": npc_id, "duration": merc.get("duration", 3)}
    )


def do_npc_heal(state: GameState, npc_id: str) -> Event:
    """找老陈治疗（仅老陈）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_003":
        return Event(type="error", title="无法治疗", description="这个NPC不能提供治疗。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    heal = npc.get("healing", {})
    cost = heal.get("cost", {})
    
    # 检查物资
    for item_id, qty in cost.items():
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="物资不足", 
                         description=f"治疗需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
    
    # 扣除物资
    for item_id, qty in cost.items():
        _consume_item(state.inventory, item_id, qty)
    
    # 恢复HP
    old_hp = state.player.hp
    state.player.hp = _clamp(state.player.hp + heal.get("hp_restore", 50))
    actual_restore = state.player.hp - old_hp
    
    # 增加好感度
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 3
    
    return Event(
        type="npc_heal",
        title="治疗完成",
        description=f"{npc['name']}帮你处理了伤口。HP恢复了{actual_restore}点。\n\n\"别乱动，我还没洗手呢...不对，我洗了七次了。\"",
        effects={"npc_id": npc_id, "hp_restore": actual_restore}
    )


def do_npc_bless(state: GameState, npc_id: str) -> Event:
    """找玛丽亚祝福（仅玛丽亚）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_004":
        return Event(type="error", title="无法祝福", description="这个NPC不能提供祝福。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    bless = npc.get("blessing", {})
    cost = bless.get("cost", 20)
    
    # 检查理智值
    if state.player.sanity < cost:
        return Event(type="error", title="理智不足", description=f"你需要至少{cost}点理智值来接受祝福。")
    
    # 扣除理智
    state.player.sanity = _clamp(state.player.sanity - cost)
    
    # 恢复理智
    old_sanity = state.player.sanity
    state.player.sanity = _clamp(state.player.sanity + bless.get("sanity_restore", 30))
    actual_restore = state.player.sanity - old_sanity
    
    # 增加好感度
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 2
    
    return Event(
        type="npc_bless",
        title="接受祝福",
        description=f"玛丽亚为你进行了'祝福'仪式。理智恢复了{actual_restore}点，但你感觉自己的独立思考能力似乎下降了...\n\n\"愿神保佑你，孩子。\"",
        effects={"npc_id": npc_id, "sanity_restore": actual_restore}
    )


def check_mercenary_expire(state: GameState) -> list[Event]:
    """检查佣兵是否到期"""
    events = []
    if state.hired_mercenary and state.day >= state.mercenary_expire_day:
        npc = get_npc(state.hired_mercenary)
        if npc:
            merc = npc.get("mercenary", {})
            state.player.attack_power -= merc.get("attack_bonus", 0)
            state.player.defense -= merc.get("defense_bonus", 0)
            events.append(Event(
                type="npc_leave",
                title=f"{npc['name']} 离开了",
                description=f"雇佣期限到了，{npc['name']}收拾东西离开了。\n\n攻击 -{merc.get('attack_bonus', 0)}，防御 -{merc.get('defense_bonus', 0)}",
                effects={"npc_id": state.hired_mercenary}
            ))
            state.hired_mercenary = None
            state.mercenary_expire_day = 0
    return events


def check_bounty_expire(state: GameState) -> list[Event]:
    """检查赏金猎人清除效果是否到期"""
    events = []
    if state.bounty_clear_location and state.day >= state.bounty_clear_expire_day:
        events.append(Event(
            type="npc_leave",
            title="清剿效果消失",
            description=f"赵四的清剿效果已经消失，{LOCATIONS.get(state.bounty_clear_location, {}).get('name', '该地点')}的敌对势力重新聚集。"
        ))
        state.bounty_clear_location = None
        state.bounty_clear_expire_day = 0
    return events


def check_herb_garden(state: GameState) -> list[Event]:
    """检查草药园每日产出"""
    events = []
    if state.herb_garden_active:
        _add_item(state.inventory, "herb", "草药", "林小雨草药园产出")
        _add_item(state.inventory, "herb", "草药", "林小雨草药园产出")
        events.append(Event(
            type="shelter",
            title="草药园产出",
            description="林小雨的草药园长势喜人。你收获了2株草药。"
        ))
    return events


# ── 新NPC特殊功能 ─────────────────────────────────────────────────────────

def do_npc_repair(state: GameState, npc_id: str, upgrade_type: str) -> Event:
    """刘瘸子装备升级（仅NPC_006）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_006":
        return Event(type="error", title="无法升级", description="这个NPC不能提供装备升级。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    repair = npc.get("repair", {})
    
    if upgrade_type == "weapon":
        if not state.player.has_weapon:
            return Event(type="error", title="没有武器", description="你还没有装备武器，无法升级。")
        recipe = repair.get("upgrade_weapon", {})
        cost = recipe.get("cost", {})
        bonus = recipe.get("bonus", 5)
        
        for item_id, qty in cost.items():
            if not _has_item(state.inventory, item_id, qty):
                return Event(type="error", title="材料不足",
                             description=f"升级武器需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
        
        for item_id, qty in cost.items():
            _consume_item(state.inventory, item_id, qty)
        
        state.player.attack_power += bonus
        state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 3
        
        return Event(
            type="npc_upgrade",
            title="武器升级完成",
            description=f"刘瘸子改造了你的武器。攻击力 +{bonus}。\n\n\"别小看一个瘸子的手艺。这把刀现在能砍穿钢板。\"",
            effects={"npc_id": npc_id, "attack_bonus": bonus}
        )
    
    elif upgrade_type == "armor":
        if not state.player.has_armor:
            return Event(type="error", title="没有护甲", description="你还没有装备护甲，无法升级。")
        recipe = repair.get("upgrade_armor", {})
        cost = recipe.get("cost", {})
        bonus = recipe.get("bonus", 4)
        
        for item_id, qty in cost.items():
            if not _has_item(state.inventory, item_id, qty):
                return Event(type="error", title="材料不足",
                             description=f"升级护甲需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
        
        for item_id, qty in cost.items():
            _consume_item(state.inventory, item_id, qty)
        
        state.player.defense += bonus
        state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 3
        
        return Event(
            type="npc_upgrade",
            title="护甲升级完成",
            description=f"刘瘸子强化了你的护甲。防御力 +{bonus}。\n\n\"马三打断了我的腿，但我这双手还能干活。\"",
            effects={"npc_id": npc_id, "defense_bonus": bonus}
        )
    
    return Event(type="error", title="未知升级", description="可用升级：weapon, armor")


def do_npc_bounty(state: GameState, npc_id: str, location_id: str) -> Event:
    """赵四清除敌对势力（仅NPC_007）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_007":
        return Event(type="error", title="无法雇佣", description="这个NPC不能执行清剿任务。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    if location_id not in LOCATIONS:
        return Event(type="error", title="未知地点", description="目标地点不存在。")
    
    bounty = npc.get("bounty_hunter", {})
    cost = bounty.get("clear_cost", {})
    
    for item_id, qty in cost.items():
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="物资不足",
                         description=f"清剿任务需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
    
    for item_id, qty in cost.items():
        _consume_item(state.inventory, item_id, qty)
    
    state.bounty_clear_location = location_id
    state.bounty_clear_expire_day = state.day + bounty.get("duration", 5)
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 2
    
    loc_name = LOCATIONS[location_id]["name"]
    
    return Event(
        type="npc_bounty",
        title="清剿任务执行",
        description=f"赵四前往{loc_name}执行清剿任务。\n\n接下来{bounty.get('duration', 5)}天内，该地点遭遇率降低{int(bounty.get('encounter_reduction', 0.5)*100)}%。\n\n\"三天之内，我会让那里的老鼠一只都不剩。\"",
        effects={"npc_id": npc_id, "location": location_id, "duration": bounty.get("duration", 5)}
    )


def do_npc_herb_garden(state: GameState, npc_id: str, action: str) -> Event:
    """林小雨草药园（仅NPC_008）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_008":
        return Event(type="error", title="无法操作", description="这个NPC没有草药园。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    garden = npc.get("herb_garden", {})
    
    if action == "activate":
        if state.herb_garden_active:
            return Event(type="error", title="已激活", description="草药园已经在运作了。")
        
        cost = garden.get("maintenance_cost", {})
        for item_id, qty in cost.items():
            if not _has_item(state.inventory, item_id, qty):
                return Event(type="error", title="物资不足",
                             description=f"激活草药园需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
        
        for item_id, qty in cost.items():
            _consume_item(state.inventory, item_id, qty)
        
        state.herb_garden_active = True
        state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 5
        
        return Event(
            type="npc_garden",
            title="草药园激活",
            description=f"林小雨的草药园已经开始为你工作。每天自动产出{garden.get('daily_herb', 2)}株草药。\n\n\"太好了！我终于有帮手了！你放心，这些草药绝对新鲜。\"",
            effects={"npc_id": npc_id, "daily_herb": garden.get("daily_herb", 2)}
        )
    
    elif action == "deactivate":
        if not state.herb_garden_active:
            return Event(type="error", title="未激活", description="草药园还没有激活。")
        state.herb_garden_active = False
        return Event(
            type="npc_garden",
            title="草药园关闭",
            description="你告诉林小雨暂时不需要草药了。她看起来有点失落。"
        )
    
    return Event(type="error", title="未知操作", description="可用操作：activate, deactivate")


def do_npc_intel(state: GameState, npc_id: str) -> Event:
    """张大力情报（仅NPC_009）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_009":
        return Event(type="error", title="无法获取情报", description="这个NPC没有情报可以提供。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    intel = npc.get("anti_church_intel", {})
    cost = intel.get("intel_cost", {})
    
    for item_id, qty in cost.items():
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="物资不足",
                         description=f"获取情报需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
    
    for item_id, qty in cost.items():
        _consume_item(state.inventory, item_id, qty)
    
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 2
    
    return Event(
        type="npc_intel",
        title="教会情报",
        description=f"张大力告诉你玛丽亚教会的内部情况：\n\n"
                    f"• 教会的物资藏在居民区教堂地下室\n"
                    f"• 玛丽亚每周三会独自去'祈祷'，其实是在清点物资\n"
                    f"• 教会有3个守卫，但周三只有1个值班\n\n"
                    f"效果：居民区遭遇率降低30%，持续3天。\n\n"
                    f"\"那个女人...她骗了我们所有人。我恨她。\"",
        effects={"npc_id": npc_id, "location": "residential", "duration": 3}
    )


def do_npc_scavenge(state: GameState, npc_id: str) -> Event:
    """老王拾荒加成（仅NPC_010）"""
    npc = get_npc(npc_id)
    if not npc or npc_id != "NPC_010":
        return Event(type="error", title="无法拾荒", description="这个NPC不能提供拾荒服务。")
    
    if npc.get("location") != state.current_location:
        return Event(type="error", title="NPC不在这里", description=f"{npc['name']}不在这个地点。")
    
    special = npc.get("special", {})
    cost = special.get("scavenge_cost", {})
    
    for item_id, qty in cost.items():
        if not _has_item(state.inventory, item_id, qty):
            return Event(type="error", title="物资不足",
                         description=f"拾荒需要：{'、'.join(f'{get_item_name(i)}x{q}' for i, q in cost.items())}")
    
    for item_id, qty in cost.items():
        _consume_item(state.inventory, item_id, qty)
    
    # 随机获得稀有物资
    import random
    possible_loot = [
        ("radio_parts", "无线电零件", "从辐射区深处找到的通讯设备零件"),
        ("metal", "稀有金属", "辐射区特有的高强度合金"),
        ("tools", "精密工具", "核爆前遗留的专业工具套装"),
        ("medicine", "军用药品", "密封完好的军用急救包"),
    ]
    
    loot = random.choice(possible_loot)
    _add_item(state.inventory, loot[0], loot[1], loot[2])
    
    state.npc_relationships[npc_id] = state.npc_relationships.get(npc_id, 0) + 1
    
    return Event(
        type="npc_scavenge",
        title="辐射区拾荒",
        description=f"老王带着你深入辐射区，找到了 {loot[1]}！\n\n"
                    f"（{loot[2]}）\n\n"
                    f"老王用手语比划着：这里还有更多...下次再来...",
        effects={"npc_id": npc_id, "item": loot[0]}
    )
