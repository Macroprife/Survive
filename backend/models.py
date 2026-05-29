from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ActionType(str, Enum):
    EXPLORE = "explore"
    REST = "rest"
    CRAFT = "craft"
    CHECK_INVENTORY = "check_inventory"
    USE_ITEM = "use_item"
    MOVE = "move"
    ATTACK = "attack"
    DEFEND = "defend"
    FLEE = "flee"


class LocationName(str, Enum):
    SHELTER = "shelter"
    SUPERMARKET = "supermarket"
    HOSPITAL = "hospital"
    POLICE_STATION = "police_station"
    RESIDENTIAL = "residential"
    RADIO_TOWER = "radio_tower"


class Item(BaseModel):
    id: str
    name: str
    description: str
    quantity: int = 1
    usable: bool = False
    craftable: bool = False


class Player(BaseModel):
    hp: int = 100
    hunger: int = 100
    thirst: int = 100
    energy: int = 100
    sanity: int = 100
    attack_power: int = 10
    defense: int = 5
    has_weapon: bool = False
    has_armor: bool = False


class Event(BaseModel):
    type: str
    title: str
    description: str
    effects: dict = {}
    choices: list[dict] = []
    resolved: bool = True


class Location(BaseModel):
    id: str
    name: str
    description: str
    danger_level: str
    loot_table: list[dict]
    encounter_rate: float


class GameState(BaseModel):
    game_id: str
    day: int = 1
    player: Player = Field(default_factory=Player)
    current_location: str = "shelter"
    inventory: list[Item] = []
    explored_locations: list[str] = ["shelter"]
    events_log: list[Event] = []
    game_over: bool = False
    game_over_reason: str = ""
    survival_score: int = 0
    pending_event: Optional[Event] = None
    tower_siege_wave: int = 0
    ending_reached: bool = False


class Action(BaseModel):
    action_type: ActionType
    target: Optional[str] = None
    item_id: Optional[str] = None
    choice: Optional[str] = None


class SaveData(BaseModel):
    save_id: str
    save_name: str
    game_state: GameState
    saved_at: str
