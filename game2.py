from typing import List, Dict, Tuple
import numpy as np
import pygame
import pygame.freetype

pygame.init()
GAME_FONT = pygame.freetype.Font("./assets/fonts/dogicabold.ttf", 18)
DISPLAY_INFO = pygame.display.Info()
WIDTH = DISPLAY_INFO.current_w
HEIGHT = DISPLAY_INFO.current_h
FRAME_LEN_MS = 10


def calculate_slopes(points: List[Tuple[float, float]]) -> list[float]:
    slopes = []
    prev_x, prev_y = points[0]
    for x, y in points:
        if x == prev_x:
            slopes.append(1)
        else:
            slopes.append((y - prev_y) / (x - prev_x))
    return slopes


def calculate_smoothness(points: List[float]) -> float:
    # Use a rolling std
    window_size = 5
    stds = []
    for i in range(len(points) - window_size + 1):
        stds.append(np.std(points[i : i + window_size]))
    # Square to punish extreme changes
    stds = np.square(stds)
    return max(1 - np.average(stds) * 100, 0)


class Player:
    def __init__(self):
        # Position
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

        # Movement
        self.x_vel = 0
        self.y_vel = 0
        self.speed = 0
        self.max_speed = 5
        self.acceleration = 0.1
        self.smoothness = 1

        # Display
        self.width = 10
        self.height = 10
        self.colour = (255, 0, 0)

        # History
        self.history_len = 400
        self.past_positions = [(self.x, self.y) for _ in range(self.history_len)]
        self.past_angles = [1 for _ in range(self.history_len)]
        self.past_colours = [self.colour for _ in range(self.history_len)]

        # Dashing
        self.dash_cd_ms = 500
        self.dash_len_ms = 100
        self.dash_multiplier = 5
        self.dashing = False
        self.dash_remaining_ms = 0
        self.dash_cd_remaining_ms = 0

    def update_velocity(self, keys: Dict):
        if not self.dashing and keys[pygame.K_SPACE] and self.dash_cd_remaining_ms <= 0:
            self.dashing = True
            self.dash_remaining_ms = self.dash_len_ms
            self.x_vel *= self.dash_multiplier
            self.y_vel *= self.dash_multiplier
            return
        elif self.dashing:
            if self.dash_remaining_ms <= 0:
                self.x_vel /= self.dash_multiplier
                self.y_vel /= self.dash_multiplier
                self.dashing = False
                self.dash_remaining_ms = 0
                self.dash_cd_remaining_ms = self.dash_cd_ms
            else:
                self.dash_remaining_ms -= FRAME_LEN_MS
            return
        else:
            self.dash_cd_remaining_ms -= FRAME_LEN_MS

        braking = keys[pygame.K_LSHIFT]

        if keys[pygame.K_d]:
            self.x_vel = min(self.x_vel + self.acceleration, self.max_speed)
        elif braking and self.x_vel > 0:
            self.x_vel -= self.acceleration * 2

        if keys[pygame.K_a]:
            self.x_vel = max(self.x_vel - self.acceleration, -self.max_speed)
        elif braking and self.x_vel < 0:
            self.x_vel += self.acceleration * 2

        if keys[pygame.K_w]:
            self.y_vel = max(self.y_vel - self.acceleration, -self.max_speed)
        elif braking and self.y_vel < 0:
            self.y_vel += self.acceleration * 2

        if keys[pygame.K_s]:
            self.y_vel = min(self.y_vel + self.acceleration, self.max_speed)
        elif braking and self.y_vel > 0:
            self.y_vel -= self.acceleration * 2

        # Deccelerate when not pressing keys
        decceleration = self.acceleration / 2
        if not (keys[pygame.K_d] or keys[pygame.K_a]):
            if self.x_vel > 0:
                self.x_vel -= min(decceleration, self.x_vel)
            if self.x_vel < 0:
                self.x_vel += min(decceleration, abs(self.x_vel))
        if not (keys[pygame.K_w] or keys[pygame.K_s]):
            if self.y_vel > 0:
                self.y_vel -= min(decceleration, self.y_vel)
            if self.y_vel < 0:
                self.y_vel += min(decceleration, abs(self.y_vel))

    def update_speed(self):
        self.speed = np.sqrt(self.x_vel**2 + self.y_vel**2)

    def update_position(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def update_colour(self):
        r = max(255 - 127 * self.speed / self.max_speed, 0)
        g = 0
        b = min(128 * self.speed / self.max_speed, 255)
        self.colour = (r, g, b)

    def update_smoothness(self):
        prev_x = self.past_positions[1][0]
        prev_y = self.past_positions[1][1]
        if self.x == prev_x:
            self.past_angles = [1] + self.past_angles[:-1]
        else:
            slope = (self.y - prev_y) / (self.x - prev_x)
            self.past_angles = [abs(np.arctan(slope))] + self.past_angles[:-1]
        self.smoothness = calculate_smoothness(self.past_angles)

    def update_history(self):
        self.past_positions = [(self.x, self.y)] + self.past_positions[:-1]
        self.past_colours = [self.colour] + self.past_colours[:-1]

    def update(self, keys):
        self.update_velocity(keys)
        self.update_speed()
        self.update_position()
        self.update_colour()
        self.update_history()
        self.update_smoothness()

    def draw(self, window: pygame.Surface):
        # Draw trail
        for i, (colour, (x, y)) in enumerate(
            zip(self.past_colours, self.past_positions)
        ):
            modifier = (self.history_len - i % self.history_len) / self.history_len
            pygame.draw.rect(
                window, colour, (x, y, self.width * modifier, self.height * modifier), 1
            )

        pygame.draw.rect(window, self.colour, (self.x, self.y, self.width, self.height))


def main():
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Red Square")
    print(pygame.display.Info())

    player = Player()
    while True:
        pygame.time.delay(FRAME_LEN_MS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            exit()

        player.update(keys)

        window.fill((0, 0, 0))
        player.draw(window)

        # speed_text = f"Speed: {round(player.speed, 1)}"
        # velocity_text = f"Velocity: {round(player.x_vel, 1), round(player.y_vel, 1)}"
        # GAME_FONT.render_to(window, (10, 10), velocity_text, (250, 250, 250))
        # GAME_FONT.render_to(window, (10, 30), speed_text, (250, 250, 250))
        GAME_FONT.render_to(
            window,
            (WIDTH // 2 - 90, 60),
            str(round(player.smoothness, 2)),
            (250, 250, 250),
            size=60,
        )

        pygame.display.update()


if __name__ == "__main__":
    main()
