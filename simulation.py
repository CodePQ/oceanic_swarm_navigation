import pygame
import sys
import random
import time
from config import *
from maze_gen import Maze
from pathfinding import Pathfinding
from boids import Agent
import math

class Slider:
    def __init__(self, x, y, w, h, label, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.val = initial_val
        self.handle_rect = pygame.Rect(x + (initial_val - min_val) / (max_val - min_val) * w - 5, y - 5, 10, h + 10)
        self.dragging = False
        self.color = (100, 140, 180)
        self.active_color = FISH_COLOR

    def draw(self, screen, font):
        # Label and Value
        txt = font.render(f"{self.label}: {self.val:.1f}", True, (200, 230, 255))
        screen.blit(txt, (self.rect.x, self.rect.y - 25))
        
        # Track
        pygame.draw.rect(screen, (30, 45, 60), self.rect, border_radius=3)
        
        # Handle
        color = self.active_color if self.dragging else self.color
        pygame.draw.rect(screen, color, self.handle_rect, border_radius=5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.w))
                self.handle_rect.centerx = new_x
                pct = (new_x - self.rect.x) / self.rect.w
                self.val = self.min_val + pct * (self.max_val - self.min_val)

class Food:
    def __init__(self, x, y):
        self.grid_pos = (x, y)
        self.pos = pygame.Vector2(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2)
        self.color = FOOD_COLOR
        self.pulse = 0
        self.amount = FOOD_MAX_AMOUNT

    def draw(self, screen, offset):
        self.pulse += 0.05
        # Scale based on amount
        amount_pct = self.amount / FOOD_MAX_AMOUNT
        radius = max(2, int(8 * amount_pct))
        pulse_val = (math.sin(self.pulse) + 1) * 5 * amount_pct
        
        tx, ty = self.pos.x + offset.x, self.pos.y + offset.y
        
        # Outer glow
        for r in range(3):
            alpha = int((100 // (r + 1)) * amount_pct)
            if alpha <= 0: continue
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (20, 20), radius + r * 5 + pulse_val)
            screen.blit(surf, (tx - 20, ty - 20))
            
        pygame.draw.circle(screen, self.color, (int(tx), int(ty)), radius)
        if amount_pct > 0.2:
            pygame.draw.circle(screen, (255, 255, 255), (int(tx), int(ty)), radius + 2, 2)

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
        
        # UI Sliders
        self.sliders = [
            Slider(40, 300, 200, 10, "Separation", 0, 10, SEP_WEIGHT),
            Slider(40, 370, 200, 10, "Alignment", 0, 5, ALI_WEIGHT),
            Slider(40, 440, 200, 10, "Cohesion", 0, 5, COH_WEIGHT)
        ]
        
        self.reset()

    def reset(self):
        self.maze = Maze(GRID_SIZE)
        self.pf = Pathfinding(self.maze)
        
        # Single school of fish
        self.target_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.food = Food(*self.target_pos)
        self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)
        
        self.agents = []
        for _ in range(AGENT_COUNT):
            # Start fish in the top-left corner
            start_x = random.randint(0, 2) * CELL_SIZE + CELL_SIZE // 2
            start_y = random.randint(0, 2) * CELL_SIZE + CELL_SIZE // 2
            self.agents.append(Agent(start_x, start_y, FISH_COLOR, 0))
            
        self.start_time = time.time()
        self.metrics = {"avg_dist_to_food": 0.0, "time_elapsed": 0.0, "aroma_strength": "Low", "cohesion": 0.0}

    def update(self):
        # Dynamic Wall Changing (Perfect Maze Preservation)
        if DYNAMIC_WALLS and random.random() < WALL_CHANGE_RATE:
            for _ in range(WALL_CHANGE_COUNT):
                self.maze.dynamic_swap()
            
            # Re-calculate aroma field for the new maze layout
            self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)

        # Update agents
        weights = {
            'sep': self.sliders[0].val,
            'ali': self.sliders[1].val,
            'coh': self.sliders[2].val
        }
        
        for agent in self.agents:
            agent.behaviors(self.agents, self.flow_field, self.dist_field, self.maze, weights)
            agent.update()
            
            # Food Consumption
            dist_to_food = agent.pos.distance_to(self.food.pos)
            if dist_to_food < FOOD_DETECTION_RADIUS:
                self.food.amount -= FOOD_CONSUMPTION_RATE
        
        # Food Relocation
        if self.food.amount <= 0:
            self.relocate_food()

        # Metrics
        self.metrics["time_elapsed"] = round(time.time() - self.start_time, 1)
        self.metrics["food_source"] = f"{int(self.food.amount)}%"
        self.metrics["dynamic_reef"] = "Active" if DYNAMIC_WALLS else "Static"
        
        total_dist = 0
        total_vel = pygame.Vector2(0, 0)
        center = pygame.Vector2(0, 0)
        
        for a in self.agents:
            grid_x, grid_y = int(a.pos.x // CELL_SIZE), int(a.pos.y // CELL_SIZE)
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                total_dist += self.dist_field[grid_y][grid_x]
            total_vel += a.vel
            center += a.pos
            
        avg_dist = total_dist / len(self.agents)
        self.metrics["avg_dist_to_food"] = round(avg_dist, 1)
        self.metrics["aroma_strength"] = "High" if avg_dist < 10 else ("Medium" if avg_dist < 20 else "Low")
        
        # Simple cohesion metric: average distance from center of school
        center /= len(self.agents)
        avg_coh_dist = sum(a.pos.distance_to(center) for a in self.agents) / len(self.agents)
        self.metrics["cohesion"] = round(max(0, 100 - avg_coh_dist), 1)

    def relocate_food(self):
        # Pick a new random reachable location
        reachable = False
        while not reachable:
            rx = random.randint(0, GRID_SIZE - 1)
            ry = random.randint(0, GRID_SIZE - 1)
            # Ensure it's not too close to current or start (0,0)
            if (rx, ry) != self.target_pos and (rx + ry) > 5:
                # Check if reachable (dist_field[ry][rx] != inf from (0,0))? 
                # Actually aroma is generated FROM target, so we need to check if (0,0) is reachable from there.
                # Simplest: just pick and re-calc. If it's isolated, it might be a boring sim, 
                # but perfect maze (Prim's) ensures everything is connected.
                self.target_pos = (rx, ry)
                self.food = Food(*self.target_pos)
                self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)
                reachable = True


    def draw(self):
        self.screen.fill(BG_COLOR)
        
        offset_x, offset_y = self.offset_x, self.offset_y
        
        # Draw background water gradient/shimmer (optional but premium)
        
        # Draw Aroma Gradient
        max_path_dist = GRID_SIZE * 2.5 # Increased visibility reach
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                dist = self.dist_field[y][x]
                if dist != float('inf'):
                    # Aroma intensity decreases with distance
                    intensity = max(0, 1.0 - (dist / max_path_dist))
                    if intensity > 0:
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        # Faint glowing gold/yellow - Alpha falloff is slower now
                        alpha = int(intensity * 70)
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
        s = pygame.Surface((280, 200), pygame.SRCALPHA)
        pygame.draw.rect(s, (10, 30, 50, 200), (0, 0, 280, 200), border_radius=15)
        self.screen.blit(s, (20, 20))
        pygame.draw.rect(self.screen, WALL_COLOR, (20, 20, 280, 200), 2, border_radius=15)

        title = self.large_font.render("School Status", True, FISH_COLOR)
        self.screen.blit(title, (40, 35))
        
        y_off = 80
        for key, val in self.metrics.items():
            label = key.replace('_', ' ').title()
            txt = self.font.render(f"{label}: {val}", True, TEXT_COLOR)
            self.screen.blit(txt, (40, y_off))
            y_off += 30

        # Draw Sliders
        for slider in self.sliders:
            slider.draw(self.screen, self.font)

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
                self.maze.grid[grid_y][grid_x][random.randint(0,3)] = not self.maze.grid[grid_y][grid_x][random.randint(0,3)]
                # Re-calculate aroma
                self.flow_field, self.dist_field = self.pf.generate_aroma_field(self.target_pos)
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
                    # Check sliders first
                    slider_clicked = False
                    for slider in self.sliders:
                        if slider.handle_rect.collidepoint(event.pos):
                            slider.handle_event(event)
                            slider_clicked = True
                    
                    if not slider_clicked:
                        self.handle_click(event.pos, event.button)
                else:
                    for slider in self.sliders:
                        slider.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = Simulation()
    sim.run()

