# Project Report: Dynamic Multi-Agent Pathfinding with Swarm Intelligence

## 1. Project Overview
This project simulates multiple swarms of agents navigating a dynamic, perfect maze. The simulation demonstrates the integration of high-level pathfinding (A*) with low-level swarm intelligence (Boids) to achieve efficient, coordinated movement and real-time adaptability to environmental changes.

## 2. Methodology

### 2.1 Maze Generation
The environment is a "perfect maze" generated using **Prim's Algorithm**. 
- **Properties**: Guaranteed connectivity between any two points and zero loops.
- **Dynamic Updates**: The maze supports real-time modification. Closing or opening an internal wall triggers an immediate recalculation of the swarm's flow fields, ensuring real-time adaptation. The outer boundary of the maze is strictly protected to prevent structural breakdown.

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

## 3. Advanced Features

### 3.1 Dynamic Environment & Topology Safeguards
To fulfill project requirements, the maze acts as a "living reef":
- **Runtime Wall Shifting**: Internal maze walls automatically open or close at random intervals, fundamentally changing the available paths.
- **Topological Constraints**: To prevent any part of the maze from becoming permanently walled off, every dynamic wall toggle is instantly verified via a temporary A* sweep. If the toggle results in an unreachable node (distance = infinity), the toggle is reverted, mathematically guaranteeing the maze remains a single connected component.
- **Bioluminescent Highlights**: When a wall successfully toggles, a subtle, fading aquamarine glow appears to give clear visual feedback of the environmental change.

### 3.2 Foraging Loop & UI Integration
A continuous simulation loop was implemented:
- **Synchronized Depletion**: The target (glowing plankton) acts as a consumable resource. It only begins depleting once the *entire* swarm has reached the target cell.
- **Dynamic Visuals**: As the food depletes, its physical size, glowing aura, and pulsing animation scale down linearly.
- **Automated Rerouting**: Once fully consumed, a new food source spawns at a random location anywhere in the maze, immediately recalculating the global flow fields and forcing the swarm to navigate to the new destination.
- **Real-Time HUD**: A sleek UI panel tracks time elapsed, dynamic reef status, average distance to food, swarm cohesion, and the precise percentage of food remaining.

### 3.3 Agent Variability & Organic Behavior
Unlike a uniform swarm, this simulation implements **Individual Agent Traits** to mimic schooling fish:
- **Organic Aesthetics**: Agents are rendered as sleek minnows with swept-back pectoral fins. Their sizes are slightly randomized, and colors are drawn from a multi-colored oceanic palette.
- **Kinematic Animation**: Agent tail wiggling and fin flapping are procedurally animated. The frequency of the animation is tied directly to the agent's velocity, simulating realistic, burst-and-coast propulsion.
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
- **Algorithmic Optimization**: Consolidating separation, alignment, and cohesion calculations into a single spatial loop reduced distance calculation overhead by 66% (from O(3N²) to O(N²)).
- **Physics Stability**: Extreme convergence at the target caused infinite separation forces due to near-zero distances. Implementing mathematical limiters and absolute spatial bounds resolved this, keeping the swarm contained and stable under intense grouping pressure.

## 5. Conclusion
The hybrid Boids-Flow-Field approach successfully balances pathfinding reliability with the emergent, fluid behavior characteristic of swarm intelligence. The system is robust to maze changes and provides a visually engaging representation of collective problem-solving.
