from enum import Enum
from pydantic import BaseModel
from typing import List, Tuple, Set, Dict

class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

class Position(BaseModel):
    x: int
    y: int

class Feature(Enum):
    WUMPUS = "W"
    PIT = "P"
    GOLD = "G"
    EMPTY = "."

class Perception(BaseModel):
    breeze: bool = False
    stench: bool = False
    glitter: bool = False
    bump: bool = False
    scream: bool = False

class GameState(BaseModel):
    score: int = 0
    has_arrow: bool = True
    has_gold: bool = False
    agent_pos: Position
    agent_dir: Direction
    known_pits: Set[Tuple[int, int]] = set()
    known_wumpus: Set[Tuple[int, int]] = set()
    visited: Set[Tuple[int, int]] = set()
