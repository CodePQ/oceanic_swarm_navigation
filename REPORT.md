# Project Report: Dynamic Multi-Agent Pathfinding with Swarm Intelligence

## 1. Project Overview
This project simulates multiple swarms of agents navigating a dynamic, perfect maze. The simulation demonstrates the integration of high-level pathfinding (A*) with low-level swarm intelligence (Boids) to achieve efficient, coordinated movement and real-time adaptability to environmental changes.

## 2. Methodology

### 2.1 Maze Generation
The environment is a "perfect maze" generated using **Prim's Algorithm**. 
- **Properties**: Guaranteed connectivity between any two points and zero loops.
- **Dynamic Updates**: The maze supports real-time modification. Closing or opening a wall triggers an immediate recalculation of the swarm's navigation fields.

### 2.2 Swarm Intelligence (Boids)
Each agent operates based on Craig Reynolds' original three rules, plus extensions for maze navigation:
1.  **Separation**: Prevents agents from colliding or clumping, ensuring smooth flow through narrow corridors.
2.  **Alignment**: Agents within a swarm synchronize their direction, creating localized "flocks" that move as a unit.
3.  **Cohesion**: Agents gravitate toward the center of their swarm, maintaining group integrity.
4.  **Flow Following**: Instead of seeking a global point, boids follow a **Vector Flow Field** derived from A*. This guides them around corners and through the maze's topological complexity.
5.  **Obstacle Avoidance**: Agents experience repulsive forces from walls to keep them centered in pathways.

### 2.3 Pathfinding & Flow Fields
To solve the maze, we use a hybrid approach:
- **A* Algorithm**: Used to determine the shortest path distance from every cell to the target.
- **Flow Field Generation**: The distance map is converted into a vector grid. Each cell in the grid points toward the neighbor cell that is closer to the target. Agents simply "steer" in the direction the current cell indicates.

## 3. Advanced Features (Optional Extensions)

### 3.1 Random Environmental Events
The simulation includes a **Dynamic Hazard System**. 
- **Spawning**: Hazards (red glowing zones) appear randomly in the maze.
- **Behavior**: Agents detect these hazards and experience a strong repulsive force, prioritizing safety even if it means deviating from the optimal path.
- **Impact**: This demonstrates the swarm's ability to handle temporary obstacles without global path recalculation.

### 3.2 Agent Variability & Constraints
Unlike a uniform swarm, this simulation implements **Individual Agent Traits**:
- **Speed & Force**: Each agent has unique maximum speed and steering force parameters (±20% variance).
- **Social Neighborhoods**: Agents have different sensing radii, leading to more organic, heterogeneous flocking patterns.

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
- **Cohesion vs. Throughput**: High cohesion improves group appearance but can cause bottlenecks in narrow 1-cell paths. Lowering cohesion slightly improves overall swarm velocity in dense mazes.
- **Dynamic Rerouting**: Using Flow Fields allows 100% of agents to adapt to new paths instantly, as they only need to look at the vector of their current cell.
- **Separation Priority**: High separation weight is critical to prevent "stacking," which occurs when agents overlap perfectly and become functionally a single agent.

## 5. Conclusion
The hybrid Boids-Flow-Field approach successfully balances pathfinding reliability with the emergent, fluid behavior characteristic of swarm intelligence. The system is robust to maze changes and provides a visually engaging representation of collective problem-solving.
