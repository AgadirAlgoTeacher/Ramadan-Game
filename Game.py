import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
ORANGE = (255, 165, 0)

class Car:
    def __init__(self, x, y, color=RED):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 20
        self.color = color
        self.angle = 0
        self.speed = 0
        self.max_speed = 8
        self.acceleration = 0.3
        self.deceleration = 0.2
        self.turn_speed = 4
        
    def update(self, keys):
        # Handle input
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -self.max_speed // 2)
        else:
            # Natural deceleration
            if self.speed > 0:
                self.speed = max(0, self.speed - self.deceleration)
            elif self.speed < 0:
                self.speed = min(0, self.speed + self.deceleration)
        
        # Turn only when moving
        if abs(self.speed) > 0.5:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle -= self.turn_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle += self.turn_speed
        
        # Update position
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y += self.speed * math.sin(rad)
        
        # Keep car on screen
        self.x = max(self.width // 2, min(SCREEN_WIDTH - self.width // 2, self.x))
        self.y = max(self.height // 2, min(SCREEN_HEIGHT - self.height // 2, self.y))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                          self.width, self.height)
    
    def draw(self, screen):
        # Create a surface for the car
        car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, self.color, (0, 0, self.width, self.height))
        pygame.draw.rect(car_surface, BLACK, (0, 0, self.width, self.height), 2)
        
        # Add some details
        pygame.draw.rect(car_surface, DARK_GRAY, (5, 3, self.width - 10, 4))
        pygame.draw.rect(car_surface, DARK_GRAY, (5, self.height - 7, self.width - 10, 4))
        
        # Rotate the car
        rotated_car = pygame.transform.rotate(car_surface, -self.angle)
        rect = rotated_car.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car, rect)

class Obstacle:
    def __init__(self, x, y, width=30, height=30):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = ORANGE
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.get_rect())
        pygame.draw.rect(screen, BLACK, self.get_rect(), 2)

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.color = GREEN
        self.collected = False
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, self.color, 
                             (self.x + self.width // 2, self.y + self.height // 2), 
                             self.width // 2)
            pygame.draw.circle(screen, BLACK, 
                             (self.x + self.width // 2, self.y + self.height // 2), 
                             self.width // 2, 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2D Car Racing Game")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player_car = Car(100, SCREEN_HEIGHT // 2)
        self.obstacles = []
        self.power_ups = []
        
        # Game state
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.power_up_timer = 0
        self.boost_timer = 0
        
        # Generate initial obstacles and power-ups
        self.generate_obstacles()
        self.generate_power_ups()
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def generate_obstacles(self):
        self.obstacles = []
        for i in range(15):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            # Make sure obstacles don't spawn too close to starting position
            if abs(x - 100) > 80 or abs(y - SCREEN_HEIGHT // 2) > 80:
                self.obstacles.append(Obstacle(x, y))
    
    def generate_power_ups(self):
        self.power_ups = []
        for i in range(5):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            # Make sure power-ups don't spawn too close to starting position
            if abs(x - 100) > 80 or abs(y - SCREEN_HEIGHT // 2) > 80:
                self.power_ups.append(PowerUp(x, y))
    
    def check_collisions(self):
        player_rect = self.player_car.get_rect()
        
        # Check obstacle collisions
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                self.game_over = True
                return
        
        # Check power-up collisions
        for power_up in self.power_ups:
            if not power_up.collected and player_rect.colliderect(power_up.get_rect()):
                power_up.collected = True
                self.score += 100
                self.boost_timer = 180  # 3 seconds at 60 FPS
    
    def update(self):
        if self.game_over:
            return
            
        keys = pygame.key.get_pressed()
        
        # Apply boost if active
        if self.boost_timer > 0:
            self.player_car.max_speed = 12
            self.boost_timer -= 1
        else:
            self.player_car.max_speed = 8
        
        self.player_car.update(keys)
        self.check_collisions()
        
        # Update score based on movement
        if self.player_car.speed > 0:
            self.distance += self.player_car.speed * 0.1
            self.score += int(self.player_car.speed * 0.5)
        
        # Regenerate obstacles and power-ups periodically
        self.power_up_timer += 1
        if self.power_up_timer > 600:  # Every 10 seconds
            self.generate_obstacles()
            self.generate_power_ups()
            self.power_up_timer = 0
    
    def draw_track(self):
        # Draw grass background
        self.screen.fill(GREEN)
        
        # Draw road
        road_width = 400
        road_x = (SCREEN_WIDTH - road_width) // 2
        pygame.draw.rect(self.screen, GRAY, (road_x, 0, road_width, SCREEN_HEIGHT))
        
        # Draw road lines
        line_width = 4
        for y in range(0, SCREEN_HEIGHT, 40):
            pygame.draw.rect(self.screen, WHITE, 
                           (SCREEN_WIDTH // 2 - line_width // 2, y, line_width, 20))
        
        # Draw road borders
        pygame.draw.rect(self.screen, WHITE, (road_x, 0, 4, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, WHITE, (road_x + road_width - 4, 0, 4, SCREEN_HEIGHT))
    
    def draw_ui(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))
        
        # Distance
        distance_text = self.font.render(f"Distance: {int(self.distance)}", True, BLACK)
        self.screen.blit(distance_text, (10, 50))
        
        # Speed
        speed_text = self.font.render(f"Speed: {int(self.player_car.speed)}", True, BLACK)
        self.screen.blit(speed_text, (10, 90))
        
        # Boost indicator
        if self.boost_timer > 0:
            boost_text = self.font.render("BOOST!", True, YELLOW)
            self.screen.blit(boost_text, (SCREEN_WIDTH - 120, 10))
        
        # Controls
        controls = [
            "Controls:",
            "Arrow Keys or WASD to move",
            "Collect green power-ups for boost",
            "Avoid orange obstacles"
        ]
        
        for i, text in enumerate(controls):
            color = BLACK if i == 0 else DARK_GRAY
            control_text = self.small_font.render(text, True, color)
            self.screen.blit(control_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 100 + i * 20))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(final_score_text, score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw(self):
        self.draw_track()
        
        # Draw game objects
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        for power_up in self.power_ups:
            power_up.draw(self.screen)
        
        self.player_car.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
    
    def restart(self):
        self.__init__()
    
    def run(self):
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and self.game_over:
                        self.restart()
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
