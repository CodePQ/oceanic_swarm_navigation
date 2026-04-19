# Configuration for the School of Fish Maze Simulation

# Simulation Settings
WIDTH = 1200
HEIGHT = 800
FPS = 60

# Maze Settings
GRID_SIZE = 25  # Number of cells (width and height)
CELL_SIZE = 30  # Size of each cell in pixels
WALL_THICKNESS = 3

# Colors (Oceanic Theme)
BG_COLOR = (5, 12, 24)            # Deep Ocean Blue
WALL_COLOR = (30, 45, 60)         # Reef Slate
PATH_COLOR = (8, 18, 35)          # Darker water
FISH_COLOR = (0, 220, 255)        # Electric Aquamarine
FOOD_COLOR = (255, 180, 0)        # Glowing Plankton Gold

AGENT_COLORS = [
    (0, 220, 255),  # Aquamarine
    (100, 255, 200), # Seafoam
    (255, 100, 150)  # Coral Pink
]

TEXT_COLOR = (200, 230, 255)

# Boids Parameters
AGENT_COUNT = 60
AGENT_RADIUS = 4
MAX_SPEED = 3.5
MAX_FORCE = 0.18

# Weights for steering behaviors
SEP_WEIGHT = 2.0    # Separation (Keep fish apart)
ALI_WEIGHT = 1.2    # Alignment (Swim together)
COH_WEIGHT = 1.1    # Cohesion (Stay in school)
AROMA_WEIGHT = 2.5  # Aroma / Probability Settings
AROMA_REACH = GRID_SIZE * 1.5 # Increased reach
RANDOM_FACTOR = 0.3           # Lowered base randomness to favor scent
AVOID_WEIGHT = 6.0  # Obstacle Avoidance

# Neighborhood radius for swarm behavior
NEIGHBOR_DIST = 60.0
DESIRED_SEPARATION = 18.0

# Dynamic Maze Settings
DYNAMIC_WALLS = True
WALL_CHANGE_RATE = 0.008  # Chance per frame (approx every ~2 seconds at 60fps)
WALL_CHANGE_COUNT = 1    # How many walls to toggle at once

# Food Depletion Settings
FOOD_MAX_AMOUNT = 100.0
FOOD_CONSUMPTION_RATE = 0.05  # Amount depleted per agent per frame
FOOD_DETECTION_RADIUS = 25.0 # Distance for consumption

