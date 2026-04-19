# Project Report: Dynamic Multi-Agent Pathfinding with Swarm Intelligence

## 1. Project Overview
This project simulates multiple swarms of agents navigating a dynamic, perfect maze. The simulation demonstrates the integration of high-level pathfinding (A*) with low-level swarm intelligence (Boids) to achieve efficient, coordinated movement and real-time adaptability to environmental changes.

## 2. Methodology

### 2.1 Maze Generation & Preservation
The environment is a "perfect maze" generated using **Prim's Algorithm**. 
- **Properties**: Guaranteed connectivity between any two points and zero loops (a spanning tree on the grid graph).
- **Dynamic preservation (Coordinated Swaps)**: To maintain "perfection" during real-time updates, the simulation uses a **coordinated swap algorithm**. When a wall is selected to be opened (removed), it creates a temporary cycle. The system instantly performs a search to identify that cycle and closes (adds) a different wall on it. This keeps the maze connected and loop-free without requiring a full recalculation.

### 2.2 Swarm Intelligence (Boids)
Each agent operates based on Craig Reynolds' original three rules, plus extensions for maze navigation:
1.  **Separation**: Prevents agents from colliding or clumping, ensuring smooth flow through narrow corridors.
2.  **Alignment**: Agents within a swarm synchronize their direction, creating localized "flocks" that move as a unit.
3.  **Cohesion**: Agents gravitate toward the center of their swarm, maintaining group integrity.
4.  **Flow Following**: Instead of seeking a global point, boids follow a **Vector Flow Field** derived from A*. This guides them around corners and through the maze's topological complexity.
5.  **Obstacle Avoidance**: Agents experience repulsive forces from walls to keep them centered in pathways.

### 2.3 Probabilistic Aroma Navigation
To solve the maze, we move beyond deterministic path following to a **Stochastic Aroma Gradient**:
- **BFS Distance Field**: A global Breadth-First Search calculates the exact distance from the food source to every cell.
- **Boltzmann Selection**: Instead of a "hard" rule to point at the best neighbor, agents evaluate all reachable neighbors and assign a probability $P(i) = \frac{e^{-d_i/T}}{\sum e^{-d_j/T}}$.
- **Behavioral Result**: This creates "Smell-based" navigation where fish occasionally take sub-optimal turns but generally follow the scent trail. It prevents the school from looking like a rigid computer algorithm and allows for natural "exploration" before the group consensus pulls them back to the source.

### 2.4 Ecological Mechanics (Food Depletion)
The simulation introduces a resource-constrained environment:
- **Consumption**: Agents within reach of the food source deplete its "amount" every frame.
- **Migration**: Once a source is exhausted, the food relocates to a new random corridor. This triggers a school-wide state transition as the aroma field resets and the school must navigate through the shifting reef to find the next deposit.

## 3. Advanced Features (Optional Extensions)

### 3.1 Real-Time Parameter Tuning (Interactive HUD)
The simulation features a sidebar with **Interactive Sliders** that modify the Boids physics in real-time:
- **Separation Weight**: Crucial for navigating narrow 1-cell corridors. Increasing this prevents stacking and clumping in bottlenecks.
- **Alignment/Cohesion Weights**: Adjusting these allows the user to transition the group from a loose "swarm" to a highly synchronized "school."

## 4. Implementation Details
- **Language**: Python
- **Graphics Engine**: Pygame
- **Modules**:
    - `maze_gen.py`: Prim's algorithm implementation.
    - `pathfinding.py`: A* and Flow Field logic.
    - `boids.py`: Agent steering behaviors and physics.
    - `config.py`: Centralized parameter management for easy tuning.
    - `simulation.py`: Main loop and user interaction.

## 4. Results & Analysis

### Metrics
- **Path Cost**: Calculated as the total distance traveled by all agents.
- **Time Elapsed**: Time taken for the majority of the swarm to reach the target.
- **Adaptability**: Measured by the latency between a maze change and the swarm's rerouting.

### Findings
- **Stochastic Pathfinding Benefits**: The probabilistic selection significantly reduces "locking" behavior seen in deterministic flow fields, where agents would previously jitter at symmetrical junctions.
- **The "Consensus" Effect**: High cohesion weights allow the school to "correct" individual mistakes. Even if a probabilistic roll leads a single fish down a wrong path, the collective pull of its neighbors (Cohesion) usually brings it back unless the majority also "smells" a shortcut.
- **Corridor Throughput**: A specific balance (Separation: 3.5, Cohesion: 1.2) was found to be optimal for the 25x25 maze, maintaining school aesthetics while preventing corridor clogging.

## 5. Conclusion
The hybrid Boids-Flow-Field approach successfully balances pathfinding reliability with the emergent, fluid behavior characteristic of swarm intelligence. The system is robust to maze changes and provides a visually engaging representation of collective problem-solving.
