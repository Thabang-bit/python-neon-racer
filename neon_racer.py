import pygame
import random
import math
import sys

# --------------------------------------------------
# PYTHON NEON RACER
# Controls: LEFT / RIGHT or A / D, SPACE = boost
#          R = restart after a crash, ESC = quit
# --------------------------------------------------

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PYTHON NEON RACER")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("monospace", 24, bold=True)
SMALL_FONT = pygame.font.SysFont("monospace", 15, bold=True)
BIG_FONT = pygame.font.SysFont("monospace", 58, bold=True)

BLACK = (3, 5, 13)
WHITE = (235, 245, 255)
BLUE = (0, 170, 255)
CYAN = (0, 235, 255)
YELLOW = (255, 195, 35)
RED = (255, 65, 55)
ROAD = (13, 18, 29)

LANE_COUNT = 3
ROAD_LEFT = 170
ROAD_RIGHT = 730
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_WIDTH = ROAD_WIDTH / LANE_COUNT
PLAYER_Y = HEIGHT - 135
CAR_W, CAR_H = 62, 105


def lane_center(lane):
    return ROAD_LEFT + LANE_WIDTH * (lane + 0.5)


def draw_glow_line(surface, color, start, end, width=3):
    # Several transparent-looking wider lines create a neon glow.
    for extra, alpha in [(12, 22), (7, 45), (3, 90)]:
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(
            glow, (*color, alpha), start, end, width + extra
        )
        surface.blit(glow, (0, 0))
    pygame.draw.line(surface, color, start, end, width)


def draw_car(surface, x, y, color, player=False):
    """Draw a simple sports car from a top-down view."""
    x, y = int(x), int(y)

    # Glow underneath the car
    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # cspell:ignore SRCALPHA
    pygame.draw.ellipse(
        glow, (*color, 65),
        (x - CAR_W // 2 - 12, y + 8, CAR_W + 24, CAR_H - 5)
    )
    surface.blit(glow, (0, 0))  # cspell:ignore blit

    # Wheels
    wheel_color = (5, 7, 12)
    for wheel_x in (x - CAR_W // 2 - 4, x + CAR_W // 2 - 3):
        pygame.draw.rect(surface, wheel_color,
                         (wheel_x, y + 18, 8, 25), border_radius=3)
        pygame.draw.rect(surface, wheel_color,
                         (wheel_x, y + 65, 8, 25), border_radius=3)

    # Main body
    body = pygame.Rect(x - CAR_W // 2, y, CAR_W, CAR_H)
    pygame.draw.rect(surface, color, body, border_radius=17)
    pygame.draw.rect(surface, (175, 225, 255), body, 2, border_radius=17)

    # Front hood and windshield
    pygame.draw.polygon(surface, tuple(min(255, c + 35) for c in color), [
        (x - 23, y + 12), (x + 23, y + 12),
        (x + 19, y + 39), (x - 19, y + 39)
    ])
    pygame.draw.rect(surface, (4, 13, 27),
                     (x - 20, y + 42, 40, 29), border_radius=7)
    pygame.draw.rect(surface, (10, 25, 42),
                     (x - 17, y + 75, 34, 12), border_radius=5)

    # Lights
    pygame.draw.rect(surface, CYAN, (x - 23, y + 4, 14, 5), border_radius=2)
    pygame.draw.rect(surface, CYAN, (x + 9, y + 4, 14, 5), border_radius=2)
    pygame.draw.rect(surface, RED, (x - 23, y + 94, 14, 5), border_radius=2)
    pygame.draw.rect(surface, RED, (x + 9, y + 94, 14, 5), border_radius=2)

    if player:
        pygame.draw.line(surface, WHITE, (x, y + 15), (x, y + 30), 2)


def draw_background(offset):
    screen.fill(BLACK)

    # Distant city lights
    for i in range(34):
        x = (i * 83 + 19) % WIDTH
        h = 35 + (i * 29) % 125
        y = 90 + (i * 17) % 90
        color = (12, 35, 60) if i % 2 else (48, 34, 13)
        pygame.draw.rect(screen, color, (x, y, 24, h))
        for wy in range(y + 8, y + h - 5, 17):
            pygame.draw.rect(screen, (20, 105, 165), (x + 6, wy, 4, 6))

    # Road
    pygame.draw.polygon(screen, ROAD, [
        (ROAD_LEFT, 145), (ROAD_RIGHT, 145),
        (WIDTH - 30, HEIGHT), (30, HEIGHT)
    ])

    # Road edge neon strips
    draw_glow_line(screen, BLUE, (ROAD_LEFT, 145), (30, HEIGHT), 4)
    draw_glow_line(screen, YELLOW, (ROAD_RIGHT, 145), (WIDTH - 30, HEIGHT), 4)

    # Perspective lane markings
    for lane_line in (1, 2):
        top_x = ROAD_LEFT + ROAD_WIDTH * lane_line / 3
        bottom_x = 30 + (WIDTH - 60) * lane_line / 3
        for segment in range(12):
            y1 = 155 + segment * 55 + (offset % 55)
            y2 = y1 + 29
            if y1 < HEIGHT:
                progress1 = (y1 - 145) / (HEIGHT - 145)
                progress2 = (y2 - 145) / (HEIGHT - 145)
                x1 = ROAD_LEFT + (bottom_x - ROAD_LEFT) * progress1
                x2 = ROAD_LEFT + (bottom_x - ROAD_LEFT) * progress2
                pygame.draw.line(screen, (210, 235, 255),
                                 (int(x1), int(y1)), (int(x2), int(y2)), 5)

    # Road texture streaks
    for i in range(25):
        x = 190 + (i * 47) % 520
        y = (i * 67 + int(offset * 2)) % HEIGHT
        pygame.draw.line(screen, (24, 34, 48),
                         (x, y), (x - 8, min(HEIGHT, y + 32)), 2)


def draw_hud(score, speed, boost_active):
    title = FONT.render("PYTHON NEON RACER", True, WHITE)
    screen.blit(title, (25, 20))

    neon_title = FONT.render("NEON", True, CYAN)
    screen.blit(neon_title, (title.get_width() + 31, 20))

    score_text = FONT.render(f"SCORE: {score}", True, WHITE)
    speed_text = FONT.render(f"SPEED: {int(speed * 20)}", True, WHITE)
    screen.blit(score_text, (WIDTH - 205, 20))
    screen.blit(speed_text, (WIDTH - 205, 52))

    hint = SMALL_FONT.render("DODGE  /  BOOST  /  SURVIVE", True, (180, 205, 225))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 65))

    boost_label = "BOOST: ON" if boost_active else "BOOST: READY"
    boost_color = YELLOW if boost_active else CYAN
    boost_text = SMALL_FONT.render(boost_label, True, boost_color)
    screen.blit(boost_text, (25, 60))


def reset_game():
    return {
        "lane": 1,
        "traffic": [],
        "score": 0,
        "speed": 6.0,
        "road_offset": 0.0,
        "spawn_timer": 0,
        "boost_timer": 0,
        "game_over": False,
    }


game = reset_game()
running = True

while running:
    dt = clock.tick(60) / 1000
    dt = min(dt, 0.04)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if game["game_over"] and event.key == pygame.K_r:
                game = reset_game()
            if not game["game_over"]:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    game["lane"] = max(0, game["lane"] - 1)
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    game["lane"] = min(2, game["lane"] + 1)
                if event.key == pygame.K_SPACE and game["boost_timer"] <= 0:
                    game["boost_timer"] = 1.5

    boost_active = game["boost_timer"] > 0 and not game["game_over"]

    if not game["game_over"]:
        if game["boost_timer"] > 0:
            game["boost_timer"] -= dt

        current_speed = game["speed"] * (1.65 if boost_active else 1)
        game["road_offset"] += current_speed * 75 * dt
        game["score"] += int(current_speed * dt * 3)

        # Gradually increase the normal speed.
        game["speed"] = min(10, game["speed"] + 0.035 * dt)

        # Spawn traffic in random lanes.
        game["spawn_timer"] += dt
        spawn_delay = max(0.48, 1.15 - game["score"] / 18000)
        if game["spawn_timer"] >= spawn_delay:
            game["spawn_timer"] = 0
            lane = random.randrange(LANE_COUNT)
            colors = [(255, 65, 45), (255, 170, 30),
                      (190, 60, 255), (40, 220, 150)]
            game["traffic"].append({
                "lane": lane,
                "y": -CAR_H - random.randint(0, 100),
                "color": random.choice(colors)
            })

        player_x = lane_center(game["lane"])
        player_rect = pygame.Rect(
            player_x - CAR_W // 2 + 8,
            PLAYER_Y + 12,
            CAR_W - 16,
            CAR_H - 22
        )

        for car in game["traffic"][:]:
            car["y"] += current_speed * 75 * dt
            traffic_rect = pygame.Rect(
                lane_center(car["lane"]) - CAR_W // 2 + 8,
                car["y"] + 12,
                CAR_W - 16,
                CAR_H - 22
            )

            if (player_rect.left < traffic_rect.right

                and player_rect.right > traffic_rect.left
                and player_rect.top < traffic_rect.bottom
                and player_rect.bottom > traffic_rect.top):
                game["game_over"] = True

            if car["y"] > HEIGHT + 20:
                game["traffic"].remove(car)
                game["score"] += 25

    # Draw the scene.
    draw_background(game["road_offset"])

    for car in game["traffic"]:
        draw_car(screen, lane_center(car["lane"]), car["y"], car["color"])

    if not game["game_over"]:
        draw_car(screen, lane_center(game["lane"]), PLAYER_Y, BLUE, player=True)

    draw_hud(game["score"], game["speed"] * (1.65 if boost_active else 1),
             boost_active)

    if game["game_over"]:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        game_over_text = BIG_FONT.render("GAME OVER", True, RED)
        score_result = FONT.render(f"FINAL SCORE: {game['score']}", True, WHITE)
        restart_text = FONT.render("PRESS R TO RACE AGAIN", True, CYAN)
        quit_text = SMALL_FONT.render("PRESS ESC TO QUIT", True, (190, 205, 220))

        screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 285)))
        screen.blit(score_result, score_result.get_rect(center=(WIDTH // 2, 365)))
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, 425)))
        screen.blit(quit_text, quit_text.get_rect(center=(WIDTH // 2, 465)))

    pygame.display.flip()

pygame.quit()
sys.exit()
