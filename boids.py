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
        self.radius = AGENT_RADIUS * random.uniform(0.7, 1.3)
        self.wiggle_phase = random.uniform(0, math.pi * 2)
        
        # Performance metrics
        self.path_distance = 0
        self.start_pos = pygame.Vector2(x, y)

    def apply_force(self, force):
        self.acc += force

    def update(self, maze):
        prev_pos = pygame.Vector2(self.pos)
        self.vel += self.acc
        if self.vel.length() > self.max_speed:
            self.vel.scale_to_length(self.max_speed)
        
        next_pos = self.pos + self.vel
        
        # Hard collision check against current cell walls to prevent phasing
        grid_x = int(self.pos.x // CELL_SIZE)
        grid_y = int(self.pos.y // CELL_SIZE)
        
        if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
            walls = maze.grid[grid_y][grid_x]
            cell_left = grid_x * CELL_SIZE
            cell_top = grid_y * CELL_SIZE
            cell_right = (grid_x + 1) * CELL_SIZE
            cell_bottom = (grid_y + 1) * CELL_SIZE
            
            radius = AGENT_RADIUS
            margin = 1  # small bounce margin
            
            if walls[0] and next_pos.y - radius < cell_top:
                next_pos.y = cell_top + radius + margin
                self.vel.y *= -0.5
            if walls[2] and next_pos.y + radius > cell_bottom:
                next_pos.y = cell_bottom - radius - margin
                self.vel.y *= -0.5
            if walls[3] and next_pos.x - radius < cell_left:
                next_pos.x = cell_left + radius + margin
                self.vel.x *= -0.5
            if walls[1] and next_pos.x + radius > cell_right:
                next_pos.x = cell_right - radius - margin
                self.vel.x *= -0.5

        # Absolute fail-safe boundary clamp
        max_coord = GRID_SIZE * CELL_SIZE - radius
        if next_pos.x < radius:
            next_pos.x = radius
            self.vel.x *= -0.5
        elif next_pos.x > max_coord:
            next_pos.x = max_coord
            self.vel.x *= -0.5
            
        if next_pos.y < radius:
            next_pos.y = radius
            self.vel.y *= -0.5
        elif next_pos.y > max_coord:
            next_pos.y = max_coord
            self.vel.y *= -0.5

        self.pos = next_pos
        self.acc *= 0
        
        speed = self.vel.length()
        self.wiggle_phase += speed * 0.15
        
        self.path_distance += self.pos.distance_to(prev_pos)

    def behaviors(self, agents, flow_field, dist_field, maze):
        sep, ali, coh = self.flock(agents)
        
        # Aroma-based Following
        grid_x = int(self.pos.x // CELL_SIZE)
        grid_y = int(self.pos.y // CELL_SIZE)
        
        aroma_steer = pygame.Vector2(0, 0)
        noise_steer = pygame.Vector2(0, 0)
        
        if 0 <= grid_x < len(flow_field[0]) and 0 <= grid_y < len(flow_field):
            dist = dist_field[grid_y][grid_x]
            # Aroma strength increases as distance decreases
            # Normalize distance: 0 (at target) to 1 (far away)
            max_dist = GRID_SIZE * 1.414 # Diagonal
            normalized_dist = min(dist / max_dist, 1.0)
            
            # Weighted probability: more directed as you get closer
            aroma_weight = AROMA_WEIGHT * (1.0 - normalized_dist * 0.7)
            noise_weight = RANDOM_FACTOR * normalized_dist * 2.0
            
            # Flow field direction
            target_dir = flow_field[grid_y][grid_x]
            if target_dir.length() > 0:
                desired = target_dir * self.max_speed
                aroma_steer = (desired - self.vel)
                if aroma_steer.length() > self.max_force:
                    aroma_steer.scale_to_length(self.max_force)
            
            # Random noise (represents "searching" behavior)
            angle = random.uniform(0, 2 * math.pi)
            noise_steer = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.max_force
            
            aroma_steer *= aroma_weight
            noise_steer *= noise_weight

        avoid = self.avoid_walls(maze)

        self.apply_force(sep * SEP_WEIGHT)
        self.apply_force(ali * ALI_WEIGHT)
        self.apply_force(coh * COH_WEIGHT)
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

    def flock(self, agents):
        sep_steer = pygame.Vector2(0, 0)
        ali_steer = pygame.Vector2(0, 0)
        coh_steer = pygame.Vector2(0, 0)
        
        sep_count = 0
        ali_coh_count = 0
        
        for other in agents:
            if other is self:
                continue
                
            d = self.pos.distance_to(other.pos)
            
            if 0 < d < self.neighbor_dist:
                # Alignment
                ali_steer += other.vel
                # Cohesion
                coh_steer += other.pos
                ali_coh_count += 1
                
                # Separation
                if d < DESIRED_SEPARATION:
                    diff = self.pos - other.pos
                    if d > 0.001:  # Safeguard against NaN/Infinity from near-zero distance
                        diff = diff.normalize() / d
                        sep_steer += diff
                        sep_count += 1

        # Finalize separation
        if sep_count > 0:
            sep_steer /= sep_count
            if sep_steer.length() > 0:
                sep_steer = sep_steer.normalize() * self.max_speed
                sep_steer -= self.vel
                if sep_steer.length() > self.max_force:
                    sep_steer.scale_to_length(self.max_force)
                    
        # Finalize alignment and cohesion
        if ali_coh_count > 0:
            # Alignment
            ali_steer /= ali_coh_count
            if ali_steer.length() > 0:
                ali_steer = ali_steer.normalize() * self.max_speed
                ali_steer -= self.vel
                if ali_steer.length() > self.max_force:
                    ali_steer.scale_to_length(self.max_force)
                
            # Cohesion
            coh_steer /= ali_coh_count
            coh_steer = self.seek(coh_steer)
            
        return sep_steer, ali_steer, coh_steer

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
            
        # Teardrop body (sleeker)
        body_points = [
            self.pos + pygame.Vector2(math.cos(angle), math.sin(angle)) * self.radius * 3.0,  # Nose
            self.pos + pygame.Vector2(math.cos(angle + 1.8), math.sin(angle + 1.8)) * self.radius * 1.2, # Middle top
            self.pos + pygame.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * self.radius * 0.2, # Tail start
            self.pos + pygame.Vector2(math.cos(angle - 1.8), math.sin(angle - 1.8)) * self.radius * 1.2  # Middle bottom
        ]
        
        # Pectoral Fins (swept back, smaller)
        fin_angle_offset = 2.0 + math.sin(self.wiggle_phase * 0.5) * 0.15
        left_fin = [
            self.pos + pygame.Vector2(math.cos(angle - 1.2), math.sin(angle - 1.2)) * self.radius * 0.8,
            self.pos + pygame.Vector2(math.cos(angle - fin_angle_offset), math.sin(angle - fin_angle_offset)) * self.radius * 1.5,
            self.pos + pygame.Vector2(math.cos(angle - 2.5), math.sin(angle - 2.5)) * self.radius * 0.5
        ]
        right_fin = [
            self.pos + pygame.Vector2(math.cos(angle + 1.2), math.sin(angle + 1.2)) * self.radius * 0.8,
            self.pos + pygame.Vector2(math.cos(angle + fin_angle_offset), math.sin(angle + fin_angle_offset)) * self.radius * 1.5,
            self.pos + pygame.Vector2(math.cos(angle + 2.5), math.sin(angle + 2.5)) * self.radius * 0.5
        ]
        
        # Tail (wiggles dynamically based on speed)
        wiggle = math.sin(self.wiggle_phase) * 0.4
        tail_angle = angle + math.pi + wiggle
        tail_points = [
            self.pos + pygame.Vector2(math.cos(angle + math.pi), math.sin(angle + math.pi)) * self.radius * 0.2,
            self.pos + pygame.Vector2(math.cos(tail_angle + 0.4), math.sin(tail_angle + 0.4)) * self.radius * 2.0,
            self.pos + pygame.Vector2(math.cos(tail_angle - 0.4), math.sin(tail_angle - 0.4)) * self.radius * 2.0
        ]
        
        # Draw fins underneath body
        pygame.draw.polygon(screen, self.color, left_fin)
        pygame.draw.polygon(screen, self.color, right_fin)
        pygame.draw.polygon(screen, self.color, body_points)
        pygame.draw.polygon(screen, self.color, tail_points)
        
        # Eye
        eye_pos = self.pos + pygame.Vector2(math.cos(angle + 0.4), math.sin(angle + 0.4)) * self.radius * 1.5
        pygame.draw.circle(screen, (255, 255, 255), (int(eye_pos.x), int(eye_pos.y)), max(1, int(self.radius * 0.3)))
        
        # Glow
        surf = pygame.Surface((self.radius*8, self.radius*8), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, 40), (self.radius*4, self.radius*4), self.radius*4)
        screen.blit(surf, (self.pos.x - self.radius*4, self.pos.y - self.radius*4))

