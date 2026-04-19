import pygame
import random
import math
from config import *

class Agent:
    def __init__(self, x, y, color, swarm_id):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.acc = pygame.Vector2(0, 0)
        self.color = color
        self.swarm_id = swarm_id
        self.max_speed = MAX_SPEED * random.uniform(0.8, 1.2)
        self.max_force = MAX_FORCE * random.uniform(0.8, 1.2)
        self.neighbor_dist = NEIGHBOR_DIST * random.uniform(0.8, 1.2)
        
        # Performance metrics
        self.path_distance = 0
        self.start_pos = pygame.Vector2(x, y)

    def apply_force(self, force):
        self.acc += force

    def update(self):
        prev_pos = pygame.Vector2(self.pos)
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        self.pos += self.vel
        self.acc *= 0
        
        self.path_distance += self.pos.distance_to(prev_pos)

    def behaviors(self, agents, flow_field, dist_field, maze, weights):
        sep_w = weights.get('sep', SEP_WEIGHT)
        ali_w = weights.get('ali', ALI_WEIGHT)
        coh_w = weights.get('coh', COH_WEIGHT)

        sep = self.separate(agents)
        ali = self.align(agents)
        coh = self.cohesion(agents)
        
        # Aroma-based Following
        grid_x = int(self.pos.x // CELL_SIZE)
        grid_y = int(self.pos.y // CELL_SIZE)
        
        aroma_steer = pygame.Vector2(0, 0)
        noise_steer = pygame.Vector2(0, 0)
        
        if 0 <= grid_x < len(flow_field[0]) and 0 <= grid_y < len(flow_field):
            dist = dist_field[grid_y][grid_x]
            
            # Probabilistic Choice among neighbors
            neighbors = maze.get_neighbors(grid_x, grid_y)
            target_dir = pygame.Vector2(0, 0)
            
            if neighbors:
                # Calculate weights based on aroma (Boltzmann-like distribution)
                # Lower distance = Higher weight
                # Temperature (2.0) controls randomness: lower = more deterministic
                neighbor_weights = []
                for nx, ny in neighbors:
                    d = dist_field[ny][nx]
                    if d == float('inf'):
                        neighbor_weights.append(0.001)
                    else:
                        neighbor_weights.append(math.exp(-d / 2.0))
                
                # Pick a neighbor based on weights
                total_w = sum(neighbor_weights)
                if total_w > 0:
                    probs = [w / total_w for w in neighbor_weights]
                    target_idx = random.choices(range(len(neighbors)), weights=probs)[0]
                    target_neighbor = neighbors[target_idx]
                    target_dir = pygame.Vector2(target_neighbor[0] - grid_x, target_neighbor[1] - grid_y)
            
            if target_dir.length() == 0:
                target_dir = flow_field[grid_y][grid_x]
            else:
                target_dir = target_dir.normalize()

            # Aroma strength increases as distance decreases
            max_dist = GRID_SIZE * 1.414 
            normalized_dist = min(dist / max_dist, 1.0)
            
            aroma_weight = AROMA_WEIGHT * (1.0 - normalized_dist * 0.7)
            noise_weight = RANDOM_FACTOR * normalized_dist * 2.0
            
            if target_dir.length() > 0:
                desired = target_dir * self.max_speed
                aroma_steer = (desired - self.vel)
                if aroma_steer.length() > self.max_force:
                    aroma_steer.scale_to_length(self.max_force)
            
            angle = random.uniform(0, 2 * math.pi)
            noise_steer = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.max_force
            
            aroma_steer *= aroma_weight
            noise_steer *= noise_weight

        avoid = self.avoid_walls(maze)

        self.apply_force(sep * sep_w)
        self.apply_force(ali * ali_w)
        self.apply_force(coh * coh_w)
        self.apply_force(aroma_steer)
        self.apply_force(noise_steer)
        self.apply_force(avoid * AVOID_WEIGHT)

    def seek(self, target):
        desired = target - self.pos
        if desired.length() > 0:
            desired = desired.normalize() * self.max_speed
            steer = desired - self.vel
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
            return steer
        return pygame.Vector2(0, 0)

    def separate(self, agents):
        steer = pygame.Vector2(0, 0)
        count = 0
        for other in agents:
            d = self.pos.distance_to(other.pos)
            if 0 < d < DESIRED_SEPARATION:
                diff = self.pos - other.pos
                diff = diff.normalize() / d
                steer += diff
                count += 1
        if count > 0:
            steer /= count
        if steer.length() > 0:
            steer = steer.normalize() * self.max_speed
            steer -= self.vel
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
        return steer

    def align(self, agents):
        sum_vel = pygame.Vector2(0, 0)
        count = 0
        for other in agents:
            d = self.pos.distance_to(other.pos)
            if 0 < d < NEIGHBOR_DIST:
                sum_vel += other.vel
                count += 1
        if count > 0:
            sum_vel /= count
            sum_vel = sum_vel.normalize() * self.max_speed
            steer = sum_vel - self.vel
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
            return steer
        return pygame.Vector2(0, 0)

    def cohesion(self, agents):
        sum_pos = pygame.Vector2(0, 0)
        count = 0
        for other in agents:
            d = self.pos.distance_to(other.pos)
            if 0 < d < NEIGHBOR_DIST:
                sum_pos += other.pos
                count += 1
        if count > 0:
            sum_pos /= count
            return self.seek(sum_pos)
        return pygame.Vector2(0, 0)

    def avoid_walls(self, maze):
        steer = pygame.Vector2(0, 0)
        grid_x = int(self.pos.x // CELL_SIZE)
        grid_y = int(self.pos.y // CELL_SIZE)
        
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            walls = maze.grid[grid_y][grid_x]
            cell_left = grid_x * CELL_SIZE
            cell_top = grid_y * CELL_SIZE
            cell_right = (grid_x + 1) * CELL_SIZE
            cell_bottom = (grid_y + 1) * CELL_SIZE
            
            margin = 8
            # Stronger avoidance when very close to walls
            if walls[0] and self.pos.y < cell_top + margin: # Top
                steer += pygame.Vector2(0, 1)
            if walls[1] and self.pos.x > cell_right - margin: # Right
                steer += pygame.Vector2(-1, 0)
            if walls[2] and self.pos.y > cell_bottom - margin: # Bottom
                steer += pygame.Vector2(0, -1)
            if walls[3] and self.pos.x < cell_left + margin: # Left
                steer += pygame.Vector2(1, 0)
                
        if steer.length() > 0:
            steer = steer.normalize() * self.max_speed
            steer -= self.vel
            if steer.length() > self.max_force:
                steer.scale_to_length(self.max_force)
        return steer

    def draw(self, screen):
        # Draw agent as a fish shape pointing in velocity direction
        if self.vel.length() > 0:
            angle = math.atan2(self.vel.y, self.vel.x)
        else:
            angle = 0
            
        # Teardrop body
        body_points = [
            self.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * AGENT_RADIUS * 2.5,  # Nose
            self.pos + pygame.Vector2(math.cos(angle + 2.2), math.sin(angle + 2.2)) * AGENT_RADIUS, # Middle top
            self.pos + pygame.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * AGENT_RADIUS * 0.5, # Tail start
            self.pos + pygame.Vector2(math.cos(angle - 2.2), math.sin(angle - 2.2)) * AGENT_RADIUS  # Middle bottom
        ]
        
        # Tail (wiggles slightly)
        wiggle = math.sin(pygame.time.get_ticks() * 0.01 + self.pos.x) * 0.5
        tail_angle = angle + math.pi + wiggle
        tail_points = [
            self.pos + pygame.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * AGENT_RADIUS * 0.5,
            self.pos + pygame.Vector2(math.cos(tail_angle + 0.5), math.sin(tail_angle + 0.5)) * AGENT_RADIUS * 1.5,
            self.pos + pygame.Vector2(math.cos(tail_angle - 0.5), math.sin(tail_angle - 0.5)) * AGENT_RADIUS * 1.5
        ]
        
        pygame.draw.polygon(screen, self.color, body_points)
        pygame.draw.polygon(screen, self.color, tail_points)
        
        # Eye
        eye_pos = self.pos + pygame.Vector2(math.cos(angle + 0.4), math.sin(angle + 0.4)) * AGENT_RADIUS * 1.5
        pygame.draw.circle(screen, (255, 255, 255), (int(eye_pos.x), int(eye_pos.y)), 1)
        
        # Glow
        surf = pygame.Surface((AGENT_RADIUS*8, AGENT_RADIUS*8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, 40), (AGENT_RADIUS*4, AGENT_RADIUS*4), AGENT_RADIUS*4)
        screen.blit(surf, (self.pos.x - AGENT_RADIUS*4, self.pos.y - AGENT_RADIUS*4))

