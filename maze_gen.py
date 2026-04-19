import random
import pygame
from config import *


class Maze:
    def __init__(self, size):
        self.size = size
        # Grid of cells. Each cell has 4 walls: [Top, Right, Bottom, Left]
        # True means wall exists, False means path
        self.grid = [[[True, True, True, True] for _ in range(size)] for _ in range(size)]
        self.generate_prim()

    def generate_prim(self):
        """Generates a perfect maze using Prim's algorithm."""
        start_x, start_y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
        visited = set([(start_x, start_y)])
        
        # Walls list: (x1, y1, x2, y2, direction)
        # direction: 0=Top, 1=Right, 2=Bottom, 3=Left (relative to x1, y1)
        walls = []
        self._add_walls(start_x, start_y, walls, visited)

        while walls:
            w_idx = random.randint(0, len(walls) - 1)
            x1, y1, x2, y2, direction = walls.pop(w_idx)

            if (x2, y2) not in visited:
                # Remove wall between x1,y1 and x2,y2
                self.grid[y1][x1][direction] = False
                opposite = (direction + 2) % 4
                self.grid[y2][x2][opposite] = False

                visited.add((x2, y2))
                self._add_walls(x2, y2, walls, visited)

    def _add_walls(self, x, y, walls, visited):
        directions = [(0, -1, 0), (1, 0, 1), (0, 1, 2), (-1, 0, 3)]
        for dx, dy, d in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size and (nx, ny) not in visited:
                walls.append((x, y, nx, ny, d))

    def toggle_wall(self, x, y, direction):
        """Opens or closes a wall at (x, y) in a specific direction."""
        if not (0 <= x < self.size and 0 <= y < self.size):
            return
        
        current_state = self.grid[y][x][direction]
        new_state = not current_state
        self.grid[y][x][direction] = new_state
        
        # Mirror the change in the neighbor cell
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = directions[direction]
        nx, ny = x + dx, y + dy
        
        if 0 <= nx < self.size and 0 <= ny < self.size:
            opposite = (direction + 2) % 4
            self.grid[ny][nx][opposite] = new_state

    def is_walkable(self, x1, y1, x2, y2):
        """Checks if there is a path between two adjacent cells."""
        if x1 == x2:
            if y1 > y2: # Up
                return not self.grid[y1][x1][0]
            else: # Down
                return not self.grid[y1][x1][2]
        elif y1 == y2:
            if x1 > x2: # Left
                return not self.grid[y1][x1][3]
            else: # Right
                return not self.grid[y1][x1][1]
        return False

    def get_neighbors(self, x, y):
        """Returns reachable neighbors of a cell."""
        neighbors = []
        # Top
        if y > 0 and not self.grid[y][x][0]:
            neighbors.append((x, y - 1))
        # Right
        if x < self.size - 1 and not self.grid[y][x][1]:
            neighbors.append((x + 1, y))
        # Bottom
        if y < self.size - 1 and not self.grid[y][x][2]:
            neighbors.append((x, y + 1))
        # Left
        if x > 0 and not self.grid[y][x][3]:
            neighbors.append((x - 1, y))
        return neighbors

    def find_path(self, start, goal):
        """Simple BFS to find a path between two cells in the current maze."""
        queue = [(start, [start])]
        visited = {start}
        while queue:
            (x, y), path = queue.pop(0)
            if (x, y) == goal:
                return path
            for nx, nx_y in self.get_neighbors(x, y):
                if (nx, nx_y) not in visited:
                    visited.add((nx, nx_y))
                    queue.append(((nx, nx_y), path + [(nx, nx_y)]))
        return None

    def dynamic_swap(self):
        """Swaps one existing wall with one existing path to maintain a perfect maze."""
        # 1. Find all inner walls that can be opened
        inner_walls = []
        for y in range(self.size):
            for x in range(self.size):
                # Only check Right (1) and Bottom (2) to avoid duplicates
                if x < self.size - 1 and self.grid[y][x][1]:
                    inner_walls.append((x, y, 1)) # x, y, direction
                if y < self.size - 1 and self.grid[y][x][2]:
                    inner_walls.append((x, y, 2))
                    
        if not inner_walls:
            return

        # 2. Pick a wall to open
        wx, wy, wd = random.choice(inner_walls)
        # Neighbor cell
        nx, ny = (wx + 1, wy) if wd == 1 else (wx, wy + 1)
        
        # 3. Find the existing path between (wx, wy) and (nx, ny)
        # This path + the new opening will form a cycle
        path = self.find_path((wx, wy), (nx, ny))
        if not path or len(path) < 2:
            return
            
        # 4. Pick a random edge on this path to CLOSE
        # The path has len(path) cells, so len(path)-1 edges
        p_idx = random.randint(0, len(path) - 2)
        c1 = path[p_idx]
        c2 = path[p_idx+1]
        
        # Determine the direction from c1 to c2
        if c2[0] > c1[0]: cd = 1 # Right
        elif c2[0] < c1[0]: cd = 3 # Left
        elif c2[1] > c1[1]: cd = 2 # Bottom
        else: cd = 0 # Top
        
        # 5. Perform the swap
        # Open the wall
        self.toggle_wall(wx, wy, wd)
        # Close the path
        self.toggle_wall(c1[0], c1[1], cd)
