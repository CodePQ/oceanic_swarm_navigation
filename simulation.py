import pygame
import sys
import random
import time
from config import *
from maze_gen import Maze
from pathfinding import Pathfinding
from boids import Agent
import math
class Food:
    def __init__(self, x, y):
        self.grid_pos = (x, y)
        self.pos = pygame.Vector2(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
        self.color = FOOD_COLOR
        self.pulse = 0
        self.amount = 100.0
        self.max_amount = 100.0

    def draw(self, screen, offset):
        if self.amount <= 0:
            return
            
        self.pulse += 0.05
        pulse_val = (math.sin(self.pulse) + 1) * 5
        tx, ty = self.pos.x + offset.x, self.pos.y + offset.y
        
        # Scale visuals based on remaining amount
        scale = max(0.1, self.amount / self.max_amount)
        base_radius = 8 * scale
        
        # Outer glow
        for r in range(3):
            alpha = int(100 // (r + 1) * scale)
            surf_size = 60 # Keep surface size fixed to avoid clipping
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            current_r = int(10 * scale + r * 5 * scale + pulse_val * scale)
            pygame.draw.circle(surf, (*self.color, alpha), (surf_size//2, surf_size//2), current_r)
            screen.blit(surf, (tx - surf_size//2, ty - surf_size//2))
            
        pygame.draw.circle(screen, self.color, (int(tx), int(ty)), max(2, int(base_radius)))
        pygame.draw.circle(screen, (255, 255, 255), (int(tx), int(ty)), max(3, int(base_radius + 2)), 2)

class WallHighlight:
    def __init__(self, x, y, direction, duration=60):
        self.x = x
        self.y = y
        self.direction = direction
        self.life = duration
        self.max_life = duration

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Oceanic Swarm Navigation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Outfit", 20)
        self.large_font = pygame.font.SysFont("Outfit", 30, bold=True)
        
        self.offset_x = 380  # Shifted right to avoid HUD overlap
        self.offset_y = (HEIGHT - GRID_SIZE * CELL_SIZE) // 2
        
        self.wall_highlights = []
        self.reset()

    def reset(self):
        self.maze = Maze(GRID_SIZE)
        self.pf = Pathfinding(self.maze)
        
        # Single school of fish
        self.target_pos = (random.randint(GRID_SIZE // 2, GRID_SIZE - 1), 
                           random.randint(GRID_SIZE // 2, GRID_SIZE - 1))
        self.food = Food(*self.target_pos)
        self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)
        
        self.agents = []
        for _ in range(AGENT_COUNT):
            # Start fish in the top-left corner
            start_x = random.randint(0, 2) * CELL_SIZE + CELL_SIZE // 2
            start_y = random.randint(0, 2) * CELL_SIZE + CELL_SIZE // 2
            fish_color = random.choice(AGENT_COLORS)
            self.agents.append(Agent(start_x, start_y, fish_color, 0))
            
        self.start_time = time.time()
        self.metrics = {
            "food_left": "100%",
            "time_elapsed": 0.0,
            "avg_dist_to_food": 0.0, 
            "aroma_strength": "Low", 
            "cohesion": 0.0
        }

    def update(self):
        # Dynamic Wall Changing
        if DYNAMIC_WALLS and random.random() < WALL_CHANGE_RATE:
            for _ in range(WALL_CHANGE_COUNT):
                rx = random.randint(0, GRID_SIZE - 1)
                ry = random.randint(0, GRID_SIZE - 1)
                rd = random.randint(0, 3)
                
                if self.maze.toggle_wall(rx, ry, rd):
                    # Check if this toggle broke connectivity to the food
                    temp_flow, temp_dist = self.pf.generate_aroma_field(self.target_pos)
                    
                    # Check if any cell is completely unreachable
                    is_safe = True
                    for row in temp_dist:
                        if float('inf') in row:
                            is_safe = False
                            break
                            
                    if is_safe:
                        self.wall_highlights.append(WallHighlight(rx, ry, rd))
                        self.flow_field, self.dist_field = temp_flow, temp_dist
                    else:
                        # Revert the toggle to keep the maze connected
                        self.maze.toggle_wall(rx, ry, rd)

        # Update Highlights
        for h in self.wall_highlights[:]:
            h.life -= 1
            if h.life <= 0:
                self.wall_highlights.remove(h)

        # Update agents
        for agent in self.agents:
            agent.behaviors(self.agents, self.flow_field, self.dist_field, self.maze)
            agent.update(self.maze)
        
        # Metrics and Food Depletion
        self.metrics["time_elapsed"] = round(time.time() - self.start_time, 1)
        self.metrics["dynamic_reef"] = "Active" if DYNAMIC_WALLS else "Static"
        
        total_dist = 0
        total_vel = pygame.Vector2(0, 0)
        center = pygame.Vector2(0, 0)
        eating_fish_count = 0
        
        for a in self.agents:
            grid_x, grid_y = int(a.pos.x // CELL_SIZE), int(a.pos.y // CELL_SIZE)
            
            # Check if eating
            if grid_x == self.target_pos[0] and grid_y == self.target_pos[1]:
                eating_fish_count += 1
                
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                total_dist += self.dist_field[grid_y][grid_x]
            total_vel += a.vel
            center += a.pos
            
        # Deplete food
        if eating_fish_count == len(self.agents):
            self.food.amount -= 0.5 # Depletion rate
            if self.food.amount <= 0:
                # Spawn new food anywhere in the maze
                self.target_pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
                self.food = Food(*self.target_pos)
                self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)
                
        self.metrics["food_left"] = f"{int(max(0, self.food.amount / self.food.max_amount * 100))}%"
            
        avg_dist = total_dist / len(self.agents)
        self.metrics["avg_dist_to_food"] = round(avg_dist, 1)
        self.metrics["aroma_strength"] = "High" if avg_dist < 10 else ("Medium" if avg_dist < 20 else "Low")
        
        # Simple cohesion metric: average distance from center of school
        center /= len(self.agents)
        avg_coh_dist = sum(a.pos.distance_to(center) for a in self.agents) / len(self.agents)
        self.metrics["cohesion"] = round(max(0, 100 - avg_coh_dist), 1)


    def draw(self):
        self.screen.fill(BG_COLOR)
        
        offset_x, offset_y = self.offset_x, self.offset_y
        
        # Draw background water gradient/shimmer (optional but premium)
        
        # Draw Aroma Gradient
        max_path_dist = GRID_SIZE * 1.5 # Heuristic for max path distance
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                dist = self.dist_field[y][x]
                if dist != float('inf'):
                    # Aroma intensity decreases with distance
                    intensity = max(0, 1.0 - (dist / max_path_dist))
                    if intensity > 0:
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        # Faint glowing gold/yellow
                        alpha = int(intensity * 60)
                        pygame.draw.rect(s, (*FOOD_COLOR, alpha), (0, 0, CELL_SIZE, CELL_SIZE))
                        self.screen.blit(s, (offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE))

        # Draw Maze Walls
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                walls = self.maze.grid[y][x]
                x1, y1 = offset_x + x * CELL_SIZE, offset_y + y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                if walls[0]: pygame.draw.line(self.screen, WALL_COLOR, (x1, y1), (x2, y1), WALL_THICKNESS) # Top
                if walls[1]: pygame.draw.line(self.screen, WALL_COLOR, (x2, y1), (x2, y2), WALL_THICKNESS) # Right
                if walls[2]: pygame.draw.line(self.screen, WALL_COLOR, (x1, y2), (x2, y2), WALL_THICKNESS) # Bottom
                if walls[3]: pygame.draw.line(self.screen, WALL_COLOR, (x1, y1), (x1, y2), WALL_THICKNESS) # Left

        # Draw Wall Highlights (Glowing Effect)
        for h in self.wall_highlights:
            x1, y1 = offset_x + h.x * CELL_SIZE, offset_y + h.y * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            
            alpha = int((h.life / h.max_life) * 200)
            color = (*FISH_COLOR, alpha)
            
            s = pygame.Surface((CELL_SIZE + 10, CELL_SIZE + 10), pygame.SRCALPHA)
            line_thickness = WALL_THICKNESS + 4
            
            # Determine line coordinates relative to surface
            lx1, ly1, lx2, ly2 = 5, 5, 5, 5
            if h.direction == 0: lx2 = lx1 + CELL_SIZE # Top
            elif h.direction == 1: lx1 = lx2 = lx1 + CELL_SIZE; ly2 = ly1 + CELL_SIZE # Right
            elif h.direction == 2: ly1 = ly2 = ly1 + CELL_SIZE; lx2 = lx1 + CELL_SIZE # Bottom
            elif h.direction == 3: ly2 = ly1 + CELL_SIZE # Left
            
            pygame.draw.line(s, color, (lx1, ly1), (lx2, ly2), line_thickness)
            # Add a second, thinner, brighter line in the middle
            pygame.draw.line(s, (255, 255, 255, alpha), (lx1, ly1), (lx2, ly2), 2)
            
            self.screen.blit(s, (x1 - 5, y1 - 5))


        # Draw Food
        self.food.draw(self.screen, pygame.Vector2(offset_x, offset_y))

        # Draw Fish
        for agent in self.agents:
            orig_pos = pygame.Vector2(agent.pos)
            agent.pos += pygame.Vector2(offset_x, offset_y)
            agent.draw(self.screen)
            agent.pos = orig_pos

        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        # Panel
        s = pygame.Surface((280, 240), pygame.SRCALPHA)
        pygame.draw.rect(s, (10, 30, 50, 200), (0, 0, 280, 240), border_radius=15)
        self.screen.blit(s, (20, 20))
        pygame.draw.rect(self.screen, WALL_COLOR, (20, 20, 280, 240), 2, border_radius=15)

        title = self.large_font.render("School Status", True, FISH_COLOR)
        self.screen.blit(title, (40, 35))
        
        y_off = 80
        for key, val in self.metrics.items():
            label = key.replace('_', ' ').title()
            txt = self.font.render(f"{label}: {val}", True, TEXT_COLOR)
            self.screen.blit(txt, (40, y_off))
            y_off += 30

        controls = [
            "R: New Reef (Reset Maze)",
            "L-Click: Displace Coral (Toggle Wall)",
            "R-Click: Drop Food (Move Target)"
        ]
        y_off = HEIGHT - 100
        for ctrl in controls:
            txt = self.font.render(ctrl, True, (100, 140, 180))
            self.screen.blit(txt, (20, y_off))
            y_off += 25

    def handle_click(self, pos, button):
        offset_x, offset_y = self.offset_x, self.offset_y
        
        grid_x = (pos[0] - offset_x) // CELL_SIZE
        grid_y = (pos[1] - offset_y) // CELL_SIZE
        
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            if button == 1: # Toggle wall logic
                direction = random.randint(0, 3)
                if self.maze.toggle_wall(grid_x, grid_y, direction):
                    temp_flow, temp_dist = self.pf.generate_aroma_field(self.target_pos)
                    
                    # Ensure manual toggle doesn't break connectivity
                    is_safe = True
                    for row in temp_dist:
                        if float('inf') in row:
                            is_safe = False
                            break
                            
                    if is_safe:
                        self.wall_highlights.append(WallHighlight(grid_x, grid_y, direction))
                        self.flow_field, self.dist_field = temp_flow, temp_dist
                    else:
                        # Revert the toggle
                        self.maze.toggle_wall(grid_x, grid_y, direction)
                        
            elif button == 3: # Move food
                self.target_pos = (grid_x, grid_y)
                self.food = Food(*self.target_pos)
                self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos, event.button)

            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()

