from typing import List, Dict
import numpy as np
import pygame
import pygame.freetype

WIDTH = 900
HEIGHT = 600


class Player():

    def __init__(self):
        # Start at centre
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.x_vel = 0
        self.y_vel = 0
        self.width = 6
        self.height = 6
        self.colour = (255, 0, 0)
        self.walking_speed = 3
        self.max_speed = 10
        self.acceleration = 0.1

        self.braking = False
        self.sliding = False
        
        # Images
        self.right = pygame.image.load('./assets/images/right.png')
        self.right_fast = pygame.image.load('./assets/images/right_fast2.png')
        self.left = pygame.image.load('./assets/images/left.png')
        self.left_fast = pygame.image.load('./assets/images/left_fast2.png')
        self.image = self.right

    def update_velocity(self, keys: Dict):

        self.braking = keys[pygame.K_LCTRL]
        self.sliding = keys[pygame.K_LSHIFT]

        if self.sliding:
            speed_delta = np.sin((self.max_speed - self.walking_speed) / self.max_speed * np.pi) ** 2 * self.acceleration
            if keys[pygame.K_d]:
                self.x_vel += speed_delta
            if keys[pygame.K_a]:
                self.x_vel -= speed_delta
            if keys[pygame.K_w]:
                self.y_vel -= speed_delta
            if keys[pygame.K_s]:
                self.y_vel += speed_delta
        else:
            if keys[pygame.K_d]:
                self.x_vel = self.walking_speed
            elif keys[pygame.K_a]:
                self.x_vel = -self.walking_speed
            if keys[pygame.K_w]:
                self.y_vel = -self.walking_speed
            elif keys[pygame.K_s]:
                self.y_vel = self.walking_speed
        
        # Deccelerate when not pressing keys
        if self.sliding:
            decceleration = self.acceleration / 2
        else:
            decceleration = self.acceleration * 2.5
        if not (keys[pygame.K_d] or keys[pygame.K_a]):
            if self.x_vel > 0:
                self.x_vel -= min(decceleration, self.x_vel)
            elif self.x_vel < 0:
                self.x_vel += min(decceleration, abs(self.x_vel))
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            if self.y_vel > 0:
                self.y_vel -= min(decceleration, self.y_vel)
            elif self.y_vel < 0:
                self.y_vel += min(decceleration, abs(self.y_vel))

    def update_position(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def update_image(self):
        if self.x_vel >= 0:
            if self.sliding:
                self.image = self.right_fast
            else:
                self.image = self.right
        else:
            if self.sliding:
                self.image = self.left_fast
            else:
                self.image = self.left

    def update(self, keys):
        self.update_velocity(keys)
        self.update_position()
        self.update_image()

    def draw(self, window: pygame.Surface):
        pygame.draw.rect(window, self.colour, (WIDTH // 2, HEIGHT // 2, self.width, self.height))
        

def main():
    pygame.init()
    game_font = pygame.freetype.Font('./assets/fonts/dogicabold.ttf', 18)
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Scrolling")
    background = pygame.image.load("./assets/images/midjourney_background_upscaled.png")

    player = Player()
    while True:
        pygame.time.delay(10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()
        player.update(keys)
        
        window.blit(background, (-player.x, -player.y))
        window.blit(player.image, (WIDTH // 2, HEIGHT // 2))
        speed_text = f"Speed: {round(np.sqrt(player.x_vel ** 2 + player.y_vel ** 2), 1)}"
        velocity_text = f"Velocity: {round(player.x_vel, 1), round(player.y_vel, 1)}"
        game_font.render_to(window, (10, 10), velocity_text, (250, 250, 250))
        game_font.render_to(window, (10, 30), speed_text, (250, 250, 250))
        pygame.display.update()


if __name__ == "__main__":
    main()
