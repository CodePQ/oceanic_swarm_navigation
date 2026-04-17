# 🌊 Oceanic Swarm Navigation

A high-fidelity "School of Fish" simulation that combines **Swarm Intelligence (Boids)** with **Dynamic Pathfinding** in a living, shifting reef.

![Simulation Preview](https://via.placeholder.com/800x400/050c18/00dcff?text=Oceanic+Swarm+Navigation+Simulation)

## 🌟 Overview

This project explores collective behavior in complex environments. A school of fish navigates through a bioluminescent reef (maze) to reach a food source. The agents don't just "calculate" a path; they sense an **Aroma Gradient** and interact with each other using biomimetic steering behaviors to maintain group cohesion while avoiding obstacles.

### Key Concepts
- **Boids (Swarm Intelligence):** Separation, Alignment, and Cohesion ensure the fish move as a unified school.
- **Aroma-Based Pathfinding:** A hybrid A* and Flow Field system guides agents through the topological complexity of the maze.
- **Dynamic Reef:** The environment can be modified in real-time by the user or by automated stochastic events.

---

## 🚀 Features

### 🐟 Biomimetic Agent Behavior
- **Individual Traits:** Every fish has unique mass, speed, and sensing radii for organic variety.
- **Steering Behaviors:** Precise obstacle avoidance ensures fish don't get stuck on reef walls.
- **Bioluminescent Visuals:** Fish glow and leave faint shimmering trails as they navigate.

### 🍱 Dynamic Navigation System
- **Aroma Field:** A real-time recalculated distance gradient that "scents" the water, guiding the school to food.
- **Flow Fields:** Efficient vector-based guidance that allows 100+ agents to adapt to new paths instantly.
- **User Interaction:** Displace coral (toggle walls) or drop food anywhere to watch the swarm instantly reroute.

### ⚓ Premium Visualization
- **Deep-Sea Aesthetic:** A curated HSL-tailored color palette with deep ocean blues and electric seafoam.
- **Real-Time Metrics HUD:** Track school cohesion, average distance to food, and "Aroma Strength" in real-time.

---

## 🎮 Getting Started

### Prerequisites
- Python 3.8+
- Pygame

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/CodePQ/oceanic_swarm_navigation.git
   cd oceanic_swarm_navigation
   ```

2. **Install dependencies:**
   ```bash
   pip install pygame
   ```

3. **Run the simulation:**
   ```bash
   python simulation.py
   ```

---

## 🕹️ Controls

| Interaction | Action |
| :--- | :--- |
| **`R` Key** | Generate a New Reef (Reset Maze) |
| **Left Click** | **Displace Coral:** Toggle a reef wall at the cursor position |
| **Right Click** | **Drop Food:** Move the food source to the cursor position |
| **Close Window** | Exit Simulation |

---

## 🛠️ Architecture

The project is structured into modular components for easy extension:

- **`simulation.py`**: The central heartbeat, managing the Pygame loop, HUD rendering, and system events.
- **`boids.py`**: The physics engine for agent steering, flocking logic, and biomimetic visuals.
- **`pathfinding.py`**: Implementation of A* and Grid-to-Vector Flow Field conversion.
- **`maze_gen.py`**: High-performance "Perfect Maze" generation using Prim's Algorithm.
- **`config.py`**: Centralized simulation parameters (weights, colors, physics constants).

---

## 📊 Technical Report
For a deep dive into the methodology, performance analysis, and swarm metrics, refer to the [REPORT.md](file:///c:/Users/codyp/OneDrive/Documents/a_project2/oceanic_swarm_navigation/REPORT.md).

---
*Created for CSCI 470 - Swarm Intelligence*