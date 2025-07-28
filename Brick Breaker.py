import pygame
from pygame.locals import * # type: ignore
import os

pygame.init()
pygame.mixer.init()

# Window setup
WIDTH, HEIGHT = 500, 500
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Brickstroy')

font = pygame.font.SysFont('Arial', 24)

# Colors
ORANGE = (255, 100, 10)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Constants
ROWS, COLUMNS = 6, 6
FPS = 60
LIVES = 3

class Ball():
    def __init__(self, x, y):
        self.radius = 10
        self.reset(x, y)
        self.max_speed = 6

    def reset(self, x, y):
        self.x = x - self.radius
        self.y = y - 50
        self.rect = Rect(self.x, self.y, self.radius * 2, self.radius * 2)
        self.x_speed = 4
        self.y_speed = -4
        self.active = False

    def move(self, base, blocks):
        self.rect.x += self.x_speed
        self.rect.y += self.y_speed
        thresh = 5

        # wall bounce
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.x_speed *= -1
        if self.rect.top < 0:
            self.y_speed *= -1
        if self.rect.bottom > HEIGHT:
            return -1  # lost life

        # base bounce
        if self.rect.colliderect(base.rect):
            if abs(self.rect.bottom - base.rect.top) < thresh:
                self.y_speed *= -1
                self.x_speed += base.direction
                self.x_speed = max(-self.max_speed, min(self.x_speed, self.max_speed))

        # brick collision
        for row in blocks:
            for b in row:
                rect, hp = b
                if rect.width == 0:
                    continue
                if self.rect.colliderect(rect):
                    if abs(self.rect.bottom - rect.top) < thresh and self.y_speed > 0:
                        self.y_speed *= -1
                    elif abs(self.rect.top - rect.bottom) < thresh and self.y_speed < 0:
                        self.y_speed *= -1
                    elif abs(self.rect.right - rect.left) < thresh:
                        self.x_speed *= -1
                    elif abs(self.rect.left - rect.right) < thresh:
                        self.x_speed *= -1

                    if hp > 1:
                        b[1] -= 1
                    else:
                        rect.width = 0
                    return 10  # points
        return 0

    def draw(self):
        pygame.draw.circle(window, BLUE, self.rect.center, self.radius)
        pygame.draw.circle(window, WHITE, self.rect.center, self.radius, 1)


class Block():
    def __init__(self):
        self.width = WIDTH // COLUMNS
        self.height = 40
        self.bricks = []

    def make(self):
        self.bricks = []
        for row in range(ROWS):
            brick_row = []
            for col in range(COLUMNS):
                x, y = col * self.width, row * self.height
                rect = pygame.Rect(x, y, self.width, self.height)
                power = 3 if row < 2 else 2 if row < 4 else 1
                brick_row.append([rect, power])
            self.bricks.append(brick_row)

    def draw(self):
        for row in self.bricks:
            for rect, hp in row:
                if rect.width == 0:
                    continue
                color = ORANGE if hp == 3 else WHITE if hp == 2 else GREEN
                pygame.draw.rect(window, color, rect)
                pygame.draw.rect(window, BLACK, rect, 1)

    def is_empty(self):
        return all(b[0].width == 0 for r in self.bricks for b in r)


class Paddle():
    def __init__(self):
        self.width = WIDTH // 6
        self.height = 15
        self.reset()

    def reset(self):
        self.rect = Rect(WIDTH // 2 - self.width // 2, HEIGHT - 40, self.width, self.height)
        self.speed = 8
        self.direction = 0

    def move(self):
        self.direction = 0
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):
        pygame.draw.rect(window, BLUE, self.rect)
        pygame.draw.rect(window, WHITE, self.rect, 1)


def draw_text(text, size, color, x, y):
    f = pygame.font.SysFont('Arial', size)
    img = f.render(text, True, color)
    window.blit(img, (x, y))


def main():
    clock = pygame.time.Clock()
    running = True
    lives, level, score = LIVES, 1, 0

    paddle = Paddle()
    ball = Ball(paddle.rect.centerx, paddle.rect.top)
    block = Block()
    block.make()

    while running:
        clock.tick(FPS)
        window.fill(BLACK)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and not ball.active:
                ball.active = True
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False

        if ball.active:
            paddle.move()
            result = ball.move(paddle, block.bricks)
            if result == -1:
                lives -= 1
                ball.reset(paddle.rect.centerx, paddle.rect.top)
                paddle.reset()
                if lives == 0:
                    draw_text("Game Over", 40, RED, 170, HEIGHT // 2)
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    lives, level, score = LIVES, 1, 0
                    block.make()
            elif result > 0:
                score += result

        if block.is_empty():
            if WIN_SOUND: WIN_SOUND.play()
            level += 1
            ball.max_speed += 1
            block.make()
            ball.reset(paddle.rect.centerx, paddle.rect.top)
            paddle.reset()
            ball.active = False

        # Drawing
        block.draw()
        paddle.draw()
        ball.draw()
        draw_text(f"Score: {score}", 20, WHITE, 10, 10)
        draw_text(f"Lives: {lives}", 20, WHITE, WIDTH - 100, 10)
        draw_text(f"Level: {level}", 20, WHITE, WIDTH // 2 - 40, 10)

        if not ball.active and lives > 0:
            draw_text("Click to Start", 24, WHITE, 160, HEIGHT // 2 + 100)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
