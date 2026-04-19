# 🌊 Oceanic Swarm Navigation

A high-fidelity "School of Fish" simulation that combines **Swarm Intelligence (Boids)** with **Dynamic Pathfinding** in a living, shifting reef.

![Simulation Preview](https://via.placeholder.com/800x400/050c18/00dcff?text=Oceanic+Swarm+Navigation+Simulation)

## 🌟 Overview

This project explores collective behavior in complex environments. A school of fish navigates through a bioluminescent reef (maze) to reach a food source. The agents don't just "calculate" a path; they sense an **Aroma Gradient** and interact with each other using biomimetic steering behaviors to maintain group cohesion while avoiding obstacles.

### Key Concepts
- **Boids (Swarm Intelligence):** Separation, Alignment, and Cohesion ensure the fish move as a unified school.
- **Probabilistic Aroma Pathfinding:** Instead of simple A*, agents use a **Boltzmann-weighted probability** system to sense scents (BFS distances) and choose their next move, creating natural, lifelike navigation.
- **Perfect Dynamic Reef:** A shifting maze that maintains 100% connectivity and zero loops at all times using a coordinated wall-swapping algorithm.
- **Ecological Integration:** Food deposits deplete as they are consumed and relocate, driving the swarm to explore new corners of the reef.

---

## 🚀 Features

### 🐟 Biomimetic Agent Behavior
- **Stochastic Decision Making:** Fish don't take "perfect" paths; they occasionally explore less-optimal corridors based on weighted probability, allowing the school to "search" by smell.
- **Interactive Tuning:** Real-time sliders allow you to adjust swarm physics (Separation, Alignment, Cohesion) on the fly to see how it affects collective navigation.
- **Bioluminescent Visuals:** Fish glow and leave shimmering trails, while the food source pulses and shrinks as it is consumed.

### 🍱 Dynamic Navigation System
- **Aroma Field:** An extended BFS-based distance gradient that "scents" the water, guiding the school to food even from across the map.
- **Perfect-Preserving Updates:** When the reef shifts, walls are opened and closed in a coordinated "swap" to ensure the maze properties remain intact and no fish are ever trapped.
- **Relocation Ecology:** Once a food source is exhausted, the aroma field instantly recalculates for a new deposit, triggering a school-wide migration.

### ⚓ Premium Visualization
- **Deep-Sea Aesthetic:** A curated palette with deep ocean blues and electric seafoam fish.
- **Interactive HUD:** Sidebar metrics track school cohesion, average distance to food, and current food supply (%).

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
| **Mouse Sliders** | **Tune Physics:** Adjust Separation, Alignment, and Cohesion in real-time |
| **Left Click** | **Displace Coral:** Toggle a reef wall (coordinated swap) |
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