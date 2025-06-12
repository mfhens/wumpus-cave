# Project Context

# Project: Wumpus World Simulation
This is a Python project to simulate the Wumpus World environment from "Artificial Intelligence: A Modern Approach."

1. Performance measures: Rewards or Punishments

Agent gets gold and return back safe = +1000 points
Agent dies (pit or Wumpus)= -1000 points
Each move of the agent = -1 point
Agent uses the arrow = -10 points

2. Environment: A setting where everything will take place.

A cave with 16(4x4) rooms.
The cave contains the following features:
- one Wumpus
- three pits
- one pile of gold

Rooms adjacent (not diagonally) to the Wumpus are stinking.
Rooms adjacent (not diagonally) to the pit are breezy.
Room with gold glitters.

Agent's initial position - Room[1, 1]

Location of Wumpus, gold and 3 pits can be anywhere except in Room[1, 1]. Determine location of the features randomly. There can only be one feature on each square.

1. Actuators: Devices that allow agent to perform following actions in the environment.

Move direction north, east, west, south: Move to next room.
Shoot north, east, west, south: Kill Wumpus with arrow. The arrow flies in the direction the agent named.
Grab: Take treasure.
Release: Drop treasure.

1. Sensors: Devices help the agent in sensing following from the environment.

Breeze: Detected near a pit.
Stench: Detected near the Wumpus.
Glitter: Detected when treasure is in the room.
Scream: Triggered when Wumpus is killed.
Bump: Occurs when hitting a wall.

Use the perceptions from the environment (stench, breeze, glitter, scream, bump) to make deductions about the position of the features.
Implement a search and backtracking algorithm for the actions of the agent
Balance risk and reward when chosing an action


## Game Context
- The game takes place in a 4x4 grid-based cave.
- The cave contains one Wumpus, three pits, and one pile of gold.
- The agent starts in the top-left corner (Room[1, 1]) and must navigate the cave to grab the gold and escape safely.

## Agent Behavior
- The agent can move (north, east, south, west), shoot an arrow, grab gold, or climb out.
- The agent perceives its surroundings using sensors (breeze, stench, glitter, bump, scream).
- The agent uses A* search and inference to decide actions, balancing risk and reward.

## Visualization
- Use `pygame` to render the game grid and symbols for perceptions and features:
  - Breeze: Blue circle
  - Stench: Green rectangle
  - Glitter: Yellow polygon
  - Pit: Black circle
  - Wumpus: Purple circle
  - Gold: Yellow diamond
  - Agent: Red circle
- Include a legend explaining the symbols and a score display.

## Data Models
- Use `pydantic` to define models for `Position`, `Perception`, `GameState`, etc.

## Modular Design
- Implement the game using classes:
  - `WumpusEnvironment`: Manages the cave grid and features.
  - `EnhancedAgent`: Handles the agent's logic and decision-making.
  - `WumpusGame`: Manages the game loop and visualization.
- Break functionality into small, reusable methods.

## Performance Metrics
- Track the agent's score based on actions and outcomes:
  - +1000 for escaping with gold
  - -1000 for dying
  - -1 for each move
  - -10 for shooting the arrow

## Example Outputs
- A visual representation of the cave grid with symbols for perceptions and features.
- Messages indicating the agent's status (e.g., "You escaped with the gold!" or "You were eaten by the Wumpus!").

## The Golden Rule  
When unsure about implementation details, ALWAYS ask the developer.  

## Anchor comments  

Add specially formatted comments throughout the codebase, where appropriate, for yourself as inline knowledge that can be easily `grep`ped for.  

### Guidelines:  

- Use `AIDEV-NOTE:`, `AIDEV-TODO:`, or `AIDEV-QUESTION:` (all-caps prefix) for comments aimed at AI and developers.  
- Keep them concise (≤ 120 chars).  
- **Important:** Before scanning files, always first try to **locate existing anchors** `AIDEV-*` in relevant subdirectories.  
- **Update relevant anchors** when modifying associated code.  
- **Do not remove `AIDEV-NOTE`s** without explicit human instruction. 

## What AI Must NEVER Do  

1. **Never modify test files** - Tests encode human intent  
2. **Never change API contracts** - Breaks real applications  
3. **Never alter migration files** - Data loss risk  
4. **Never commit secrets** - Use environment variables  
5. **Never assume business logic** - Always ask  
6. **Never remove AIDEV- comments** - They're there for a reason  

Remember: We optimize for maintainability over cleverness.  
When in doubt, choose the boring solution. 