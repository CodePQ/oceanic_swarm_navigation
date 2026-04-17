import heapq
import pygame
from config import GRID_SIZE

class Pathfinding:
    def __init__(self, maze):
        self.maze = maze

    def a_star(self, start, goal):
        """Standard A* algorithm to find the shortest path in the maze."""
        frontend = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontend:
            _, current = heapq.heappop(frontend)

            if current == goal:
                break

            for next_cell in self.maze.get_neighbors(*current):
                new_cost = cost_so_far[current] + 1
                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    priority = new_cost + self.heuristic(next_cell, goal)
                    heapq.heappush(frontend, (priority, next_cell))
                    came_from[next_cell] = current

        # Reconstruct path
        if goal not in came_from:
            return []
            
        path = []
        curr = goal
        while curr:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()
        return path

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def generate_aroma_field(self, goal):
        """Generates a flow field (vector grid) and a distance map for aroma intensity."""
        # Use BFS to create a distance map from the goal to all cells
        dist_field = [[float('inf')] * self.maze.size for _ in range(self.maze.size)]
        dist_field[goal[1]][goal[0]] = 0
        queue = [goal]
        
        while queue:
            current = queue.pop(0)
            cx, cy = current
            
            for nx, ny in self.maze.get_neighbors(cx, cy):
                if dist_field[ny][nx] == float('inf'):
                    dist_field[ny][nx] = dist_field[cy][cx] + 1
                    queue.append((nx, ny))
                    
        # Create vector field from distance map
        flow_field = [[pygame.Vector2(0, 0) for _ in range(self.maze.size)] for _ in range(self.maze.size)]
        for y in range(self.maze.size):
            for x in range(self.maze.size):
                if dist_field[y][x] == float('inf'):
                    continue
                
                # Check neighbors and point towards the one with the smallest distance
                min_dist = dist_field[y][x]
                best_neighbor = None
                
                for nx, ny in self.maze.get_neighbors(x, y):
                    if dist_field[ny][nx] < min_dist:
                        min_dist = dist_field[ny][nx]
                        best_neighbor = (nx, ny)
                
                if best_neighbor:
                    dir_vec = pygame.Vector2(best_neighbor[0] - x, best_neighbor[1] - y)
                    if dir_vec.length() > 0:
                        flow_field[y][x] = dir_vec.normalize()
                        
        return flow_field, dist_field

