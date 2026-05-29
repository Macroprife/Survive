"""Tests for the wasteland-survive game engine."""
import pytest
from backend.game_engine import (
    create_new_game, do_explore, do_combat_action, do_siege_combat,
    do_craft, do_rest, use_item, check_win_condition, _day_scale,
    _count_item, _consume_item, _add_item, _has_item, _clamp,
    apply_daily_consumption, ITEM_REGISTRY, LOCATIONS,
)
from backend.models import GameState, Event


# ── Helpers ─────────────────────────────────────────────────────────────────
def _make_state(**kwargs) -> GameState:
    state = create_new_game()
    for k, v in kwargs.items():
        setattr(state, k, v)
    return state


def _add_items(state: GameState, item_id: str, qty: int = 1):
    _add_item(state.inventory, item_id, item_id, f"test {item_id}", qty)


def _force_combat(state: GameState, enemy_hp: int = 10):
    """Set up a pending combat event for testing."""
    state.pending_event = Event(
        type="combat", title="测试战斗",
        description="test combat",
        effects={"enemy": "测试敌人", "enemy_hp": enemy_hp},
        resolved=False,
    )


# ── Item Registry ───────────────────────────────────────────────────────────
class TestItemRegistry:
    def test_all_items_have_name(self):
        for item_id, meta in ITEM_REGISTRY.items():
            assert "name" in meta, f"{item_id} missing 'name'"
            assert "usable" in meta, f"{item_id} missing 'usable'"
            assert "effect" in meta, f"{item_id} missing 'effect'"

    def test_get_item_name_from_registry(self):
        from backend.game_engine import get_item_name
        assert get_item_name("food") == "食物"
        assert get_item_name("radio_parts") == "无线电零件"
        assert get_item_name("nonexistent") == "nonexistent"


# ── Utility Functions ───────────────────────────────────────────────────────
class TestUtilities:
    def test_clamp(self):
        assert _clamp(50) == 50
        assert _clamp(-10) == 0
        assert _clamp(150) == 100
        assert _clamp(50, lo=10, hi=90) == 50

    def test_add_and_count_item(self):
        state = create_new_game()
        _add_item(state.inventory, "food", "食物", "test")
        assert _count_item(state.inventory, "food") == 3  # 2 initial + 1

    def test_consume_item(self):
        state = create_new_game()
        initial = _count_item(state.inventory, "food")
        _consume_item(state.inventory, "food")
        assert _count_item(state.inventory, "food") == initial - 1

    def test_consume_item_removes_at_zero(self):
        state = create_new_game()
        _consume_item(state.inventory, "food", 2)  # consume all
        assert not _has_item(state.inventory, "food")

    def test_has_item(self):
        state = create_new_game()
        assert _has_item(state.inventory, "food")
        assert not _has_item(state.inventory, "weapon")
        assert _has_item(state.inventory, "food", 2)
        assert not _has_item(state.inventory, "food", 3)

    def test_day_scale(self):
        state = create_new_game()
        assert _day_scale(state) == pytest.approx(1.03)
        state.day = 17
        assert _day_scale(state) == pytest.approx(1.5)  # caps at 1.5
        state.day = 50
        assert _day_scale(state) == pytest.approx(1.5)  # stays capped


# ── Game Creation ───────────────────────────────────────────────────────────
class TestCreateGame:
    def test_initial_state(self):
        state = create_new_game()
        assert state.day == 1
        assert state.player.hp == 100
        assert state.player.hunger == 100
        assert len(state.inventory) == 2  # food + water
        assert state.game_over is False
        assert state.tower_siege_wave == 0

    def test_game_id_length(self):
        state = create_new_game()
        assert len(state.game_id) == 8


# ── Use Item ────────────────────────────────────────────────────────────────
class TestUseItem:
    def test_use_food(self):
        state = create_new_game()
        state.player.hunger = 50
        evt = use_item(state, "food")
        assert state.player.hunger == 85  # 50 + 35
        assert evt.type == "use"
        assert _count_item(state.inventory, "food") == 1  # had 2, consumed 1

    def test_use_water(self):
        state = create_new_game()
        state.player.thirst = 30
        evt = use_item(state, "water")
        assert state.player.thirst == 70
        assert evt.type == "use"

    def test_use_medicine(self):
        state = create_new_game()
        state.player.hp = 60
        _add_items(state, "medicine")
        evt = use_item(state, "medicine")
        assert state.player.hp == 90
        assert evt.type == "use"

    def test_use_armor_consumes(self):
        state = create_new_game()
        _add_items(state, "armor")
        use_item(state, "armor")
        assert state.player.has_armor
        assert state.player.defense == 12
        assert not _has_item(state.inventory, "armor")

    def test_use_missing_item(self):
        state = create_new_game()
        evt = use_item(state, "weapon")
        assert evt.type == "error"


# ── Rest ────────────────────────────────────────────────────────────────────
class TestRest:
    def test_rest_recovers(self):
        state = create_new_game()
        state.player.energy = 30
        state.player.hp = 80
        do_rest(state)
        # rest +40, daily consumption -10 = net +30
        assert state.player.energy == 60
        # rest +5, daily consumption hunger==85 no extra hp loss
        assert state.player.hp == 85
        assert state.day == 2

    def test_rest_can_kill_from_hunger(self):
        state = create_new_game()
        state.player.hunger = 1
        state.player.hp = 5
        # hunger -> 0 -> hp -10, hp goes to 0
        do_rest(state)
        assert state.game_over


# ── Daily Consumption ───────────────────────────────────────────────────────
class TestDailyConsumption:
    def test_hunger_drain(self):
        state = create_new_game()
        events = apply_daily_consumption(state)
        assert state.player.hunger == 85  # 100 - 15

    def test_zero_hunger_damages_hp(self):
        state = create_new_game()
        state.player.hunger = 10
        apply_daily_consumption(state)
        assert state.player.hunger == 0
        assert state.player.hp == 90  # 100 - 10


# ── Combat ──────────────────────────────────────────────────────────────────
class TestCombat:
    def test_attack_kills_enemy(self):
        state = create_new_game()
        _force_combat(state, enemy_hp=1)
        evt = do_combat_action(state, "attack")
        assert evt.type == "combat_end"
        assert state.pending_event is None

    def test_attack_continues(self):
        state = create_new_game()
        _force_combat(state, enemy_hp=999)
        evt = do_combat_action(state, "attack")
        assert evt.type == "combat"
        assert evt.resolved is False

    def test_defend_reduces_damage(self):
        state = create_new_game()
        _force_combat(state, enemy_hp=50)
        evt = do_combat_action(state, "defend")
        assert evt.type == "combat"
        assert state.player.energy == 95  # -5

    def test_flee_success(self):
        state = create_new_game()
        _force_combat(state)
        import random
        random.seed(42)  # deterministic
        evt = do_combat_action(state, "flee")
        # Either flee or take damage
        assert evt.type in ("flee", "combat")


# ── Crafting ────────────────────────────────────────────────────────────────
class TestCrafting:
    def test_craft_medicine(self):
        state = create_new_game()
        _add_items(state, "herb", 2)
        _add_items(state, "water", 2)
        evt = do_craft(state, "medicine")
        assert evt.type == "craft"
        assert _has_item(state.inventory, "medicine")

    def test_craft_weapon_sets_attributes(self):
        state = create_new_game()
        _add_items(state, "metal", 3)
        _add_items(state, "wood", 2)
        evt = do_craft(state, "weapon")
        assert evt.type == "craft"
        assert state.player.has_weapon
        assert state.player.attack_power == 18

    def test_craft_missing_ingredients(self):
        state = create_new_game()
        evt = do_craft(state, "weapon")
        assert evt.type == "error"

    def test_craft_unknown_recipe(self):
        state = create_new_game()
        evt = do_craft(state, "nonexistent")
        assert evt.type == "error"


# ── Victory Condition ───────────────────────────────────────────────────────
class TestVictoryCondition:
    def test_need_tower_and_siege_and_parts(self):
        state = create_new_game()
        _add_items(state, "radio_parts", 3)
        # No tower, no siege -> no win
        assert not check_win_condition(state)

        state.current_location = "radio_tower"
        # At tower but no siege -> no win
        assert not check_win_condition(state)

        state.tower_siege_wave = 4
        # All conditions met -> win
        assert check_win_condition(state)
        assert state.game_over
        assert state.ending_reached

    def test_win_consumes_parts(self):
        state = create_new_game()
        _add_items(state, "radio_parts", 3)
        state.current_location = "radio_tower"
        state.tower_siege_wave = 4
        check_win_condition(state)
        assert _count_item(state.inventory, "radio_parts") == 0

    def test_no_double_win(self):
        state = create_new_game()
        _add_items(state, "radio_parts", 3)
        state.current_location = "radio_tower"
        state.tower_siege_wave = 4
        check_win_condition(state)
        assert state.game_over
        # Second call should be no-op
        assert not check_win_condition(state)


# ── Tower Siege ─────────────────────────────────────────────────────────────
class TestTowerSiege:
    def test_siege_combat_wave_progression(self):
        state = create_new_game()
        _add_items(state, "radio_parts", 3)
        state.current_location = "radio_tower"
        state.tower_siege_wave = 1

        # Wave 1: easy enemy
        state.pending_event = Event(
            type="combat", title="wave1", description="",
            effects={"enemy": "test", "enemy_hp": 1}, resolved=False)
        evts = do_siege_combat(state, "attack")
        assert state.tower_siege_wave == 2
        assert any(e.type == "combat_end" for e in evts)

    def test_siege_flee_resets_wave(self):
        state = create_new_game()
        state.tower_siege_wave = 2
        _force_combat(state)
        evts = do_siege_combat(state, "flee")
        assert state.tower_siege_wave == 0
        assert any(e.type == "flee" for e in evts)

    def test_siege_wave3_victory(self):
        state = create_new_game()
        _add_items(state, "radio_parts", 3)
        state.current_location = "radio_tower"
        state.tower_siege_wave = 3

        state.pending_event = Event(
            type="combat", title="wave3", description="",
            effects={"enemy": "boss", "enemy_hp": 1}, resolved=False)
        evts = do_siege_combat(state, "attack")
        assert state.tower_siege_wave == 4
        assert state.game_over
        assert state.ending_reached
        assert any(e.type == "victory" for e in evts)


# ── Explore ─────────────────────────────────────────────────────────────────
class TestExplore:
    def test_explore_requires_energy(self):
        state = create_new_game()
        state.player.energy = 5
        evts = do_explore(state)
        assert evts[0].type == "error"

    def test_explore_advances_day(self):
        state = create_new_game()
        import random
        random.seed(1)  # deterministic
        do_explore(state)
        assert state.day == 2

    def test_explore_radio_tower_triggers_siege(self):
        state = create_new_game()
        _add_items(state, "radio_parts", 3)
        state.current_location = "radio_tower"
        state.player.energy = 100
        evts = do_explore(state, "radio_tower")
        assert state.tower_siege_wave == 1
        assert state.pending_event is not None
        assert state.pending_event.type == "combat"
        # Should have narrative + combat events
        types = [e.type for e in evts]
        assert "narrative" in types
        assert "combat" in types
