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

BOOST_COLOR = (0, 255, 255)
BOOST_PAD_WIDTH = 75
BOOST_PAD_HEIGHT = 18


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
    x, y = int(x), int(y)

    # Neon glow underneath the car
    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.ellipse(
        glow,
        (*color, 65),
        (x - 48, y + 5, 96, 110)
    )

    surface.blit(glow, (0, 0))

    # Racing wheels
    wheel_color = (2, 3, 9)

    for wx in [-1, 1]:
        for wy in [22, 72]:
            pygame.draw.rect(
                surface,
                wheel_color,
                (x + wx * 31 - 4, y + wy, 9, 25),
                border_radius=4
            )

    # Main aerodynamic sports car body
    pygame.draw.polygon(
        surface,
        color,
        [
            (x, y),
            (x + 23, y + 13),
            (x + 29, y + 38),
            (x + 30, y + 79),
            (x + 21, y + 101),
            (x, y + 108),
            (x - 21, y + 101),
            (x - 30, y + 79),
            (x - 29, y + 38),
            (x - 23, y + 13)
        ]
    )

    # Neon body outline
    pygame.draw.polygon(
        surface,
        (170, 225, 255),
        [
            (x, y),
            (x + 23, y + 13),
            (x + 29, y + 38),
            (x + 30, y + 79),
            (x + 21, y + 101),
            (x, y + 108),
            (x - 21, y + 101),
            (x - 30, y + 79),
            (x - 29, y + 38),
            (x - 23, y + 13)
        ],
        2
    )

    # Front windshield
    pygame.draw.polygon(
        surface,
        (4, 13, 28),
        [
            (x - 20, y + 24),
            (x + 20, y + 24),
            (x + 17, y + 47),
            (x - 17, y + 47)
        ]
    )

    # Rear windshield
    pygame.draw.polygon(
        surface,
        (5, 17, 34),
        [
            (x - 17, y + 65),
            (x + 17, y + 65),
            (x + 19, y + 84),
            (x - 19, y + 84)
        ]
    )

    # Central racing stripe
    pygame.draw.line(
        surface,
        (190, 230, 255),
        (x, y + 13),
        (x, y + 96),
        2
    )

    # Blue headlights
    pygame.draw.rect(
        surface,
        CYAN,
        (x - 22, y + 5, 13, 5),
        border_radius=3
    )

    pygame.draw.rect(
        surface,
        CYAN,
        (x + 9, y + 5, 13, 5),
        border_radius=3
    )

    # Red rear lights
    pygame.draw.rect(
        surface,
        RED,
        (x - 22, y + 99, 13, 5),
        border_radius=3
    )

    pygame.draw.rect(
        surface,
        RED,
        (x + 9, y + 99, 13, 5),
        border_radius=3
    )

    # Player car indicator
    if player:
        pygame.draw.circle(
            surface,
            WHITE,
            (x, y + 55),
            3
        )




def draw_background(offset):
    screen.fill((3, 4, 15))

    # Futuristic city buildings
    for i in range(40):
        x = (i * 83) % WIDTH
        building_height = 50 + (i * 31) % 120
        y = 145 - building_height

        pygame.draw.rect(
            screen,
            (9, 17, 39),
            (x, y, 45, building_height)
        )

        # Neon building windows
        for wy in range(y + 10, 145, 20):
            pygame.draw.rect(
                screen,
                (0, 90, 150),
                (x + 8, wy, 5, 8)
            )

    # Dark futuristic highway
    pygame.draw.polygon(
        screen,
        (12, 16, 29),
        [
            (170, 145),
            (730, 145),
            (870, HEIGHT),
            (30, HEIGHT)
        ]
    )

    # Glowing road barriers
    for width, alpha in [(15, 25), (8, 60), (3, 255)]:
        glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        pygame.draw.line(
            glow,
            (0, 160, 255, alpha),
            (170, 145),
            (30, HEIGHT),
            width
        )

        pygame.draw.line(
            glow,
            (255, 190, 20, alpha),
            (730, 145),
            (870, HEIGHT),
            width
        )

        screen.blit(glow, (0, 0))

    # Animated lane markings
    for lane in range(1, 3):
        top_x = 170 + (560 / 3) * lane
        bottom_x = 30 + (840 / 3) * lane

        for i in range(12):
            y1 = 150 + i * 55 + (offset % 55)
            y2 = y1 + 28

            if y1 < HEIGHT:
                p1 = (y1 - 145) / (HEIGHT - 145)
                p2 = (y2 - 145) / (HEIGHT - 145)

                x1 = 170 + (bottom_x - 170) * p1
                x2 = 170 + (bottom_x - 170) * p2

                pygame.draw.line(
                    screen,
                    (100, 190, 255),
                    (int(x1), int(y1)),
                    (int(x2), int(y2)),
                    4
                )

    # Neon road lights
    for i in range(18):
        y = (i * 45 + int(offset * 2)) % HEIGHT

        pygame.draw.circle(
            screen,
            (0, 160, 255),
            (65, y),
            3
        )

        pygame.draw.circle(
            screen,
            (255, 190, 30),
            (835, y),
            3
        )


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
