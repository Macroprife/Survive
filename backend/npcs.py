"""
NPC数据 - 废土幸存者档案
"""

NPC_REGISTRY = {
    "NPC_001": {
        "id": "NPC_001",
        "name": "\"秤砣\"马三",
        "type": "幸存者",
        "faction": "黑市商人 / 地下交易网络",
        "personality": "极度贪婪、多疑偏执、囤积癖。睡觉时必须枕着三把锁的铁箱才能合眼。",
        "background_summary": "核爆前废品回收站老板，灾难后建立地下交易网络，控制着三个营地的物资供应。",
        "location": "supermarket",  # 出没地点
        "dialogue": {
            "idle_muttering": [
                "（盯着物资清单喃喃自语）不够...还不够...",
                "（突然惊醒四顾）谁？！谁在外面？！...妈的，又是风..."
            ],
            "first_meet": "停下。再往前走一步，我保证你的膝盖会比你的脑子先着地。",
            "trade_success": "识货。在这世道，识货的人才能活得久。",
            "trade_fail": "浪费我时间。你知道我一分钟值多少物资吗？滚。",
            "on_injured": "我的货...谁也别想抢我的货..."
        },
        "trade_table": {
            "buy": {  # 他卖给玩家的
                "food": {"price": 15, "stock": 3},
                "water": {"price": 20, "stock": 2},
                "medicine": {"price": 50, "stock": 1},
            },
            "sell": {  # 他从玩家这收购的
                "metal": {"price": 8},
                "cloth": {"price": 5},
                "herb": {"price": 10},
            }
        },
        "quest": {
            "id": "quest_masan_debt",
            "title": "马三的债",
            "description": "马三说有个叫老陈的医生欠他三罐罐头，让我去帮他还债。老陈在医院附近。",
            "reward": {"item": "medicine", "quantity": 2},
            "target_npc": "NPC_003"
        }
    },
    "NPC_002": {
        "id": "NPC_002",
        "name": "\"断指\"安娜",
        "type": "幸存者",
        "faction": "前特种部队 / 现雇佣兵",
        "personality": "冷酷、情感麻木、严重的PTSD。会在睡梦中徒手掐死靠近的人。",
        "background_summary": "核爆时执行绝密任务的特种兵，亲眼看着战友一个个死去，现在靠接雇佣活计为生。",
        "location": "police_station",
        "dialogue": {
            "idle_muttering": [
                "（擦拭匕首）小王...你说的对，该痛快的...",
                "（突然警觉地握紧刀柄）三点钟方向...不对，是风声..."
            ],
            "first_meet": "你站的位置，正好是我的匕首能刺穿你喉咙的距离。退后两步。",
            "trade_success": "交易完成。别跟上来。",
            "trade_fail": "上一个想跟我讨价还价的人，现在正在喂辐射鼠。",
            "on_injured": "好...好...小王，我来找你了..."
        },
        "trade_table": {
            "buy": {
                "weapon": {"price": 40, "stock": 1},
                "bandage": {"price": 15, "stock": 2},
            },
            "sell": {
                "food": {"price": 5},
                "water": {"price": 5},
            }
        },
        "mercenary": {
            "hire_cost": {"food": 3, "water": 1},
            "attack_bonus": 15,
            "defense_bonus": 8,
            "duration": 3  # 有效天数
        }
    },
    "NPC_003": {
        "id": "NPC_003",
        "name": "\"漂白水\"老陈",
        "type": "幸存者",
        "faction": "前医院药剂师 / 地下医疗站负责人",
        "personality": "强迫症、洁癖、对死亡有着病态的恐惧。每小时必须洗手七次。",
        "background_summary": "核爆前的药剂师，灾难后被迫成为'医生'，在地下室建立了唯一的医疗站。",
        "location": "hospital",
        "dialogue": {
            "idle_muttering": [
                "（反复洗手）一次...两次...三次...不对，再来一次...",
                "（翻看《药典》）在哪里...那个配方一定在这里..."
            ],
            "first_meet": "洗手了吗？没洗就别碰我的东西。你是来看病的？",
            "trade_success": "成交。记住，这些药要按时吃。",
            "trade_fail": "我知道你付不起...但我也不能白送。",
            "on_injured": "不...我不能死...我还有那么多病人..."
        },
        "trade_table": {
            "buy": {
                "medicine": {"price": 30, "stock": 3},
                "bandage": {"price": 10, "stock": 5},
            },
            "sell": {
                "herb": {"price": 8},
                "alcohol": {"price": 12},
            }
        },
        "healing": {
            "cost": {"food": 1, "water": 1},
            "hp_restore": 50,
            "description": "老陈可以帮你治疗严重伤势，但需要一些物资作为报酬。"
        }
    },
    "NPC_004": {
        "id": "NPC_004",
        "name": "\"圣母\"玛丽亚",
        "type": "幸存者",
        "faction": "末日教会 / 邪教领袖",
        "personality": "偏执、控制欲极强、表面慈爱实则冷酷。会用温柔的语气说出最残忍的话。",
        "background_summary": "核爆前的心理咨询师，灾难后建立末日教会，自称'圣母'，信徒超过两百人。",
        "location": "residential",
        "dialogue": {
            "idle_muttering": [
                "（闭眼祈祷）主啊，您的旨意我已明了...",
                "（翻看《末日启示录》）还差多少人来着？"
            ],
            "first_meet": "孩子，你看起来很疲惫。来，让我为你祈祷。",
            "trade_success": "愿神保佑你。这不是交易，这是'祝福'。",
            "trade_fail": "我理解你的困境。但'奉献'是神圣的。",
            "on_injured": "主啊...这是您给我的试炼吗？"
        },
        "trade_table": {
            "buy": {
                "food": {"price": 8, "stock": 5},  # 教会物资多但贵
                "water": {"price": 10, "stock": 3},
            },
            "sell": {
                "cloth": {"price": 3},
                "wood": {"price": 3},
            }
        },
        "blessing": {
            "cost": 20,  # 需要20点理智值
            "sanity_restore": 30,
            "description": "玛丽亚的'祝福'可以恢复理智，但代价是你的独立思考能力。"
        }
    },
    "NPC_005": {
        "id": "NPC_005",
        "name": "\"辐射者\"阿光",
        "type": "变异怪 / 伪装者",
        "faction": "无（被所有势力排斥的边缘人）",
        "personality": "极度自卑、压抑的愤怒、渴望被接纳。会在被歧视时突然爆发暴力。",
        "background_summary": "核爆前的程序员，重度辐射导致身体变异，现在是被所有人排斥的'怪物'。",
        "location": "radio_tower",  # 住在辐射区边缘
        "dialogue": {
            "idle_muttering": [
                "（对着水坑里的倒影）你看你...你还是人吗？...",
                "（抱着奶瓶轻轻摇晃）小薇...爸爸在这..."
            ],
            "first_meet": "别开枪...我不是怪物...至少...我不认为自己是...",
            "trade_success": "谢谢...很久没有人愿意和我说话了...",
            "trade_fail": "我明白了...我这样的人...不配拥有任何东西...",
            "on_injured": "也好...让我死了吧...这样就不用再看自己这张脸了..."
        },
        "trade_table": {
            "buy": {
                "radio_parts": {"price": 25, "stock": 2},  # 他在辐射区能找到零件
                "metal": {"price": 5, "stock": 5},
            },
            "sell": {
                "food": {"price": 3},  # 他不在乎价格，只想有人理他
                "water": {"price": 3},
            }
        },
        "special": {
            "can_enter_radiation": True,  # 他可以带玩家进入辐射区
            "radiation_guide_cost": {"food": 2, "water": 2},
            "description": "阿光可以在辐射区自由行动，他可以带你进入危险区域寻找稀有物资。"
        }
    },
    "NPC_006": {
        "id": "NPC_006",
        "name": "\"铁嘴\"刘瘸子",
        "type": "幸存者",
        "faction": "前废品回收站合伙人 / 现修理匠",
        "personality": "记仇、嘴硬心软、对机械有近乎病态的执着。左腿瘸了，用一根钢管当拐杖，走路时发出有节奏的金属敲击声。对马三恨之入骨，但又不得不依赖他的物资网络生存。会把每一个来找他修东西的人都当成马三的探子来盘问。",
        "background_summary": "核爆前与马三合伙经营废品回收站，核爆后第三天被马三偷走藏匿物资并打断左腿，现在在居民区废墟开修理铺为生。",
        "location": "residential",
        "dialogue": {
            "idle_muttering": [
                "（敲打着一根金属管）马三...总有一天我要把你的秤砣塞进你嘴里...",
                "（检查一个收音机零件）这频率...要是能调到军用频段就好了..."
            ],
            "first_meet": "你身上有马三的味道。...别否认，我能闻出来。他派你来干什么？监视我？",
            "trade_success": "成交。但记住，我修过的东西比你见过的人都多。别小看一个瘸子。",
            "trade_fail": "嫌贵？你知道我这条腿值多少物资吗？滚去找马三吧，他会'便宜'卖给你。",
            "on_injured": "这条腿...这条该死的腿...马三，我做鬼也不会放过你..."
        },
        "trade_table": {
            "buy": {
                "tools": {"price": 20, "stock": 2},
                "torch": {"price": 15, "stock": 3},
                "weapon": {"price": 35, "stock": 1}
            },
            "sell": {
                "metal": {"price": 10},
                "cloth": {"price": 4}
            }
        },
        "repair": {
            "description": "刘瘸子可以帮你修理和改造装备，提升武器攻击力或护甲防御力。",
            "upgrade_weapon": {"cost": {"metal": 3, "tools": 1}, "bonus": 5},
            "upgrade_armor": {"cost": {"metal": 2, "cloth": 2}, "bonus": 4}
        }
    },
    "NPC_007": {
        "id": "NPC_007",
        "name": "\"幽灵\"赵四",
        "type": "幸存者",
        "faction": "前特种部队狙击手 / 现赏金猎人",
        "personality": "冷血、话少、杀人从不失手。左眼有一道从额头到下巴的疤痕，据说是被弹片划的。对安娜有一种扭曲的执念——既恨她当年的'背叛'，又暗自佩服她的生存能力。会用狙击镜观察目标整整三天才扣扳机。",
        "background_summary": "核爆时是'夜莺'小队的狙击手，与安娜是战友。核爆当天他选择抛弃伤员独自逃走，与安娜决裂。现在是废土上最危险的赏金猎人。",
        "location": "radio_tower",
        "dialogue": {
            "idle_muttering": [
                "（擦拭瞄准镜）安娜...你还活着...有意思...",
                "（检查弹匣）一发...两发...够杀三个人了。"
            ],
            "first_meet": "（用狙击镜看着你）...你不是我的目标。但如果你挡路，我会破例。",
            "trade_success": "成交。别问这些东西从哪来的。问了你会睡不着觉。",
            "trade_fail": "（冷笑）你知道我的报价为什么不能还吗？因为还价的人，我见过太多了——都是死人。",
            "on_injured": "有意思...很久没人能伤到我了...你叫什么名字？我想记住是谁..."
        },
        "trade_table": {
            "buy": {
                "weapon": {"price": 30, "stock": 2},
                "bandage": {"price": 8, "stock": 5},
                "medicine": {"price": 40, "stock": 1}
            },
            "sell": {
                "food": {"price": 6},
                "metal": {"price": 12}
            }
        },
        "bounty_hunter": {
            "description": "赵四可以帮你清除特定地点的敌对势力，大幅降低该地点的遭遇率。",
            "clear_cost": {"food": 5, "water": 3},
            "encounter_reduction": 0.5,
            "duration": 5
        }
    },
    "NPC_008": {
        "id": "NPC_008",
        "name": "\"小白鸽\"林小雨",
        "type": "幸存者",
        "faction": "前实习护士 / 现草药师",
        "personality": "温柔但固执、对草药有近乎迷信的信仰、害怕血腥场面。右手腕有一道浅浅的疤痕——核爆时被碎玻璃划的，老陈亲手缝的针。会把所有伤员都当成自己的病人来照顾，即使对方是敌人。",
        "background_summary": "核爆时是老陈手下的实习护士，亲眼见证了老陈的第一次'手术'。核爆后独自在医院废墟附近开辟了一片草药园，靠种植和售卖草药为生。",
        "location": "hospital",
        "dialogue": {
            "idle_muttering": [
                "（浇水）快长...快长...老陈师傅说这种草药能治辐射病...",
                "（翻看笔记）三号草药配酒精...不对，是配水...老陈师傅怎么写的来着？"
            ],
            "first_meet": "你受伤了吗？来，让我看看...哦，你没事就好。我是林小雨，以前在这里实习的护士。",
            "trade_success": "成交。记住，草药要新鲜的时候用，放久了效果会打折扣的。",
            "trade_fail": "对不起...但这些草药是我花了三个月才种出来的...我不能贱卖...",
            "on_injured": "老陈师傅...救我...我还不想死...我还没学会你教我的那个配方..."
        },
        "trade_table": {
            "buy": {
                "herb": {"price": 8, "stock": 8},
                "medicine": {"price": 25, "stock": 2},
                "bandage": {"price": 8, "stock": 4}
            },
            "sell": {
                "food": {"price": 4},
                "water": {"price": 4}
            }
        },
        "herb_garden": {
            "description": "林小雨的草药园可以定期为你提供草药，但需要你帮她照料。",
            "daily_herb": 2,
            "maintenance_cost": {"water": 1}
        }
    },
    "NPC_009": {
        "id": "NPC_009",
        "name": "\"迷途者\"张大力",
        "type": "幸存者",
        "faction": "前末日教会信徒 / 现反教会活动者",
        "personality": "愤怒、偏执、对宗教有PTSD。身上刻满了十字架的疤痕——都是他自己用刀刻的，每次'忏悔'就刻一道。会突然陷入宗教狂热的回忆，然后又突然清醒过来咒骂玛丽亚。",
        "background_summary": "曾是玛丽亚最虔诚的信徒，为教会贡献了所有物资。发现玛丽亚的真面目后叛逃，被阿光在辐射区收留。现在是废土上最激进的反教会活动者。",
        "location": "supermarket",
        "dialogue": {
            "idle_muttering": [
                "（抓挠手臂上的十字架疤痕）神不存在...神不存在...她骗了我们所有人...",
                "（突然停下）等等...我刚才在祈祷？不！我不祈祷！我再也不祈祷了！"
            ],
            "first_meet": "你是她的信徒吗？！你是不是玛丽亚派来抓我的？！...（冷静下来）不...你看起来不像...对不起，我太紧张了。",
            "trade_success": "成交。这些物资都是我从教会偷出来的。算是他们欠我的。",
            "trade_fail": "你要价太高了...你知道我在教会损失了多少吗？我把我所有的东西都给了那个女人...",
            "on_injured": "玛丽亚...你看到了吗...这就是你说的'神的旨意'吗...骗子..."
        },
        "trade_table": {
            "buy": {
                "food": {"price": 6, "stock": 4},
                "water": {"price": 8, "stock": 3},
                "cloth": {"price": 4, "stock": 3}
            },
            "sell": {
                "herb": {"price": 6},
                "wood": {"price": 4}
            }
        },
        "anti_church_intel": {
            "description": "张大力掌握了玛丽亚教会的内部情报，可以告诉你教会的弱点和隐藏物资位置。",
            "intel_cost": {"food": 3},
            "effect": "降低居民区遭遇率30%，持续3天"
        }
    },
    "NPC_010": {
        "id": "NPC_010",
        "name": "\"双头\"老王",
        "type": "变异怪 / 伪装者",
        "faction": "无（阿光的变异者同伴）",
        "personality": "沉默寡言、极度自卑、但对阿光有着近乎疯狂的忠诚。变异导致他的脖子上长出了一个肉瘤，看起来像是两个头，因此得名'双头'。会用手语和阿光交流，偶尔发出沙哑的低吼。",
        "background_summary": "核爆前是建筑工人，重度辐射导致身体变异。在辐射区被阿光救下后，两人成为最亲密的伙伴。现在与阿光一起住在辐射区边缘的废弃工厂里。",
        "location": "radio_tower",
        "dialogue": {
            "idle_muttering": [
                "（用手语比划，然后发出低吼）阿光...饿...",
                "（盯着水坑里的倒影，用手指着脖子上的肉瘤）...丑...太丑了..."
            ],
            "first_meet": "（警惕地看着你，然后看向阿光，似乎在等阿光的判断）...阿光认识你？...那就好。",
            "trade_success": "（点点头，把物资推给你，然后转身离开）...嗯。",
            "trade_fail": "（摇摇头，发出不满的低吼）...不。",
            "on_injured": "（发出痛苦的嚎叫，然后用手语比划）阿光...帮我...告诉阿光..."
        },
        "trade_table": {
            "buy": {
                "metal": {"price": 3, "stock": 10},
                "radio_parts": {"price": 20, "stock": 1},
                "tools": {"price": 12, "stock": 2}
            },
            "sell": {
                "food": {"price": 2},
                "water": {"price": 2}
            }
        },
        "special": {
            "description": "老王是辐射区最熟练的拾荒者，他可以帮你找到普通幸存者找不到的稀有物资。",
            "scavenge_bonus": True,
            "scavenge_cost": {"food": 1, "water": 1}
        }
    }
}


def get_npc(npc_id: str) -> dict | None:
    """获取NPC数据"""
    return NPC_REGISTRY.get(npc_id)


def get_npcs_by_location(location: str) -> list[dict]:
    """获取某个地点的所有NPC"""
    return [npc for npc in NPC_REGISTRY.values() if npc.get("location") == location]


def get_all_npcs() -> dict:
    """获取所有NPC数据"""
    return NPC_REGISTRY
