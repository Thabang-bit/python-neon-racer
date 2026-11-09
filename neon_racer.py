
import pygame
import random
import sys

pygame.init()

# WINDOW
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PYTHON NEON RACER")
clock = pygame.time.Clock()

# FONTS
FONT = pygame.font.SysFont("consolas", 24, bold=True)
SMALL_FONT = pygame.font.SysFont("consolas", 15, bold=True)
BIG_FONT = pygame.font.SysFont("consolas", 58, bold=True)

# COLORS
BLACK = (3, 5, 13)
WHITE = (235, 245, 255)
BLUE = (0, 170, 255)
CYAN = (0, 235, 255)
YELLOW = (255, 195, 35)
RED = (255, 65, 55)
ROAD = (13, 18, 29)

# ROAD SETTINGS
ROAD_LEFT = 170
ROAD_RIGHT = 730
LANE_WIDTH = 560 / 3

PLAYER_Y = HEIGHT - 135
CAR_W = 62
CAR_H = 105

# BOOST SETTINGS
BOOST_COLOR = (0, 255, 255)
BOOST_PAD_WIDTH = 75
BOOST_PAD_HEIGHT = 18


def lane_center(lane):
    return ROAD_LEFT + LANE_WIDTH * (lane + 0.5)


# --------------------------------------------------
# DRAW SPORTS CAR
# --------------------------------------------------

def draw_car(surface, x, y, color, player=False):
    x, y = int(x), int(y)

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.ellipse(
        glow, (*color, 65),
        (x - 48, y + 5, 96, 110)
    )

    surface.blit(glow, (0, 0))

    # Wheels
    for wx in [-1, 1]:
        for wy in [22, 72]:
            pygame.draw.rect(
                surface, (2, 3, 9),
                (x + wx * 31 - 4, y + wy, 9, 25),
                border_radius=4
            )

    # Car body
    body = [
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

    pygame.draw.polygon(surface, color, body)
    pygame.draw.polygon(surface, (170, 225, 255), body, 2)

    # Windows
    pygame.draw.polygon(surface, (4, 13, 28), [
        (x - 20, y + 24),
        (x + 20, y + 24),
        (x + 17, y + 47),
        (x - 17, y + 47)
    ])

    pygame.draw.polygon(surface, (5, 17, 34), [
        (x - 17, y + 65),
        (x + 17, y + 65),
        (x + 19, y + 84),
        (x - 19, y + 84)
    ])

    # Racing stripe
    pygame.draw.line(
        surface, WHITE,
        (x, y + 13), (x, y + 96), 2
    )

    # Headlights and rear lights
    for lx in [x - 22, x + 9]:
        pygame.draw.rect(
            surface, CYAN,
            (lx, y + 5, 13, 5),
            border_radius=3
        )

        pygame.draw.rect(
            surface, RED,
            (lx, y + 99, 13, 5),
            border_radius=3
        )

    if player:
        pygame.draw.circle(
            surface, WHITE, (x, y + 55), 3
        )


# --------------------------------------------------
# DRAW NEON BOOST PAD
# --------------------------------------------------

def draw_boost_pad(x, y):
    x, y = int(x), int(y)

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    pygame.draw.rect(
        glow, (0, 255, 255, 45),
        (x - 48, y - 9, 96, 36),
        border_radius=8
    )

    screen.blit(glow, (0, 0))

    pygame.draw.rect(
        screen, (0, 110, 145),
        (x - 37, y, 75, 18),
        border_radius=5
    )

    pygame.draw.rect(
        screen, BOOST_COLOR,
        (x - 37, y, 75, 18),
        2,
        border_radius=5
    )

    for stripe_x in range(x - 25, x + 26, 17):
        pygame.draw.line(
            screen, WHITE,
            (stripe_x, y + 4),
            (stripe_x + 7, y + 14), 3
        )


# --------------------------------------------------
# DRAW NEON HIGHWAY
# --------------------------------------------------

def draw_background(offset):
    screen.fill(BLACK)

    # City buildings
    for i in range(40):
        x = (i * 83) % WIDTH
        building_height = 50 + (i * 31) % 120
        y = 145 - building_height

        pygame.draw.rect(
            screen, (9, 17, 39),
            (x, y, 45, building_height)
        )

        for wy in range(y + 10, 145, 20):
            pygame.draw.rect(
                screen, (0, 90, 150),
                (x + 8, wy, 5, 8)
            )

    # Road
    pygame.draw.polygon(
        screen, ROAD,
        [
            (ROAD_LEFT, 145),
            (ROAD_RIGHT, 145),
            (870, HEIGHT),
            (30, HEIGHT)
        ]
    )

    # Road edges
    pygame.draw.line(
        screen, BLUE,
        (170, 145), (30, HEIGHT), 4
    )

    pygame.draw.line(
        screen, YELLOW,
        (730, 145), (870, HEIGHT), 4
    )

    # Lane markings
    for lane in range(1, 3):
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
                    screen, (100, 190, 255),
                    (int(x1), int(y1)),
                    (int(x2), int(y2)), 4
                )

    # Roadside lights
    for i in range(18):
        y = (i * 45 + int(offset * 2)) % HEIGHT

        pygame.draw.circle(screen, BLUE, (65, y), 3)
        pygame.draw.circle(screen, YELLOW, (835, y), 3)


# --------------------------------------------------
# HUD
# --------------------------------------------------

def draw_hud(score, speed, boost_active, boost_time):
    title = FONT.render(
        "PYTHON NEON RACER", True, WHITE
    )

    screen.blit(title, (25, 20))

    screen.blit(
        FONT.render("NEON", True, CYAN),
        (title.get_width() + 31, 20)
    )

    screen.blit(
        FONT.render(f"SCORE: {score}", True, WHITE),
        (WIDTH - 205, 20)
    )

    screen.blit(
        FONT.render(f"SPEED: {int(speed * 20)}", True, WHITE),
        (WIDTH - 205, 52)
    )

    label = "BOOST ACTIVE" if boost_active else "BOOST: SPACE"
    color = YELLOW if boost_active else CYAN

    screen.blit(
        SMALL_FONT.render(label, True, color),
        (25, 60)
    )

    # Boost meter
    pygame.draw.rect(
        screen, (35, 45, 60),
        (25, 88, 125, 9),
        border_radius=4
    )

    if boost_active:
        fill = int(125 * boost_time / 2)

        pygame.draw.rect(
            screen, CYAN,
            (25, 88, fill, 9),
            border_radius=4
        )


# --------------------------------------------------
# RESET GAME
# --------------------------------------------------

def reset_game():
    return {
        "lane": 1,
        "traffic": [],
        "boost_pads": [],
        "score": 0,
        "speed": 6.0,
        "road_offset": 0,
        "spawn_timer": 0,
        "boost_spawn_timer": 0,
        "boost_timer": 0,
        "game_over": False
    }


game = reset_game()
running = True


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------

while running:

    dt = min(clock.tick(60) / 1000, 0.04)

    # EVENTS
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if game["game_over"] and event.key == pygame.K_r:
                game = reset_game()

            if not game["game_over"]:

                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    game["lane"] = max(0, game["lane"] - 1)

                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    game["lane"] = min(2, game["lane"] + 1)

                if event.key == pygame.K_SPACE:
                    if game["boost_timer"] <= 0:
                        game["boost_timer"] = 2.0

    # GAME UPDATE
    if not game["game_over"]:

        game["boost_timer"] = max(
            0, game["boost_timer"] - dt
        )

        boost_active = game["boost_timer"] > 0

        current_speed = game["speed"]

        if boost_active:
            current_speed *= 1.65

        game["road_offset"] += current_speed * 75 * dt

        game["score"] += int(current_speed * dt * 3)

        game["speed"] = min(
            10, game["speed"] + 0.035 * dt
        )

        # Traffic spawning
        game["spawn_timer"] += dt

        spawn_delay = max(
            0.48, 1.15 - game["score"] / 18000
        )

        if game["spawn_timer"] >= spawn_delay:

            game["spawn_timer"] = 0

            game["traffic"].append({
                "lane": random.randrange(3),
                "y": -CAR_H,
                "color": random.choice([
                    (255, 65, 45),
                    (255, 170, 30),
                    (190, 60, 255),
                    (40, 220, 150)
                ])
            })

        # Boost pad spawning
        game["boost_spawn_timer"] += dt

        if game["boost_spawn_timer"] >= 4:

            game["boost_spawn_timer"] = 0

            game["boost_pads"].append({
                "lane": random.randrange(3),
                "y": -30
            })

        # Player collision rectangle
        player_x = lane_center(game["lane"])

        player_rect = pygame.Rect(
            player_x - CAR_W // 2 + 8,
            PLAYER_Y + 12,
            CAR_W - 16,
            CAR_H - 22
        )

        # Traffic movement and collisions
        for car in game["traffic"][:]:

            car["y"] += current_speed * 75 * dt

            traffic_rect = pygame.Rect(
                lane_center(car["lane"]) - CAR_W // 2 + 8,
                int(car["y"] + 12),
                CAR_W - 16,
                CAR_H - 22
            )

            if player_rect.colliderect(traffic_rect):
                game["game_over"] = True

            if car["y"] > HEIGHT + 20:
                game["traffic"].remove(car)
                game["score"] += 25

        # Boost pad movement and collection
        for pad in game["boost_pads"][:]:

            pad["y"] += current_speed * 75 * dt

            pad_x = lane_center(pad["lane"])

            pad_rect = pygame.Rect(
                pad_x - BOOST_PAD_WIDTH // 2,
                int(pad["y"]),
                BOOST_PAD_WIDTH,
                BOOST_PAD_HEIGHT
            )

            if player_rect.colliderect(pad_rect):

                game["boost_timer"] = 2.0
                game["score"] += 100

                game["boost_pads"].remove(pad)

            elif pad["y"] > HEIGHT:
                game["boost_pads"].remove(pad)

    # DRAW SCENE
    draw_background(game["road_offset"])

    for pad in game["boost_pads"]:
        draw_boost_pad(
            lane_center(pad["lane"]),
            pad["y"]
        )

    for car in game["traffic"]:
        draw_car(
            screen,
            lane_center(car["lane"]),
            car["y"],
            car["color"]
        )

    if not game["game_over"]:
        draw_car(
            screen,
            lane_center(game["lane"]),
            PLAYER_Y,
            BLUE,
            player=True
        )

    boost_active = (
        game["boost_timer"] > 0
        and not game["game_over"]
    )

    displayed_speed = game["speed"] * (
        1.65 if boost_active else 1
    )

    draw_hud(
        game["score"],
        displayed_speed,
        boost_active,
        game["boost_timer"]
    )

    # GAME OVER SCREEN
    if game["game_over"]:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT), pygame.SRCALPHA
        )

        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        game_over_text = BIG_FONT.render(
            "GAME OVER", True, RED
        )

        score_text = FONT.render(
            f"FINAL SCORE: {game['score']}",
            True, WHITE
        )

        restart_text = FONT.render(
            "PRESS R TO RACE AGAIN",
            True, CYAN
        )

        quit_text = SMALL_FONT.render(
            "PRESS ESC TO QUIT",
            True, WHITE
        )

        screen.blit(
            game_over_text,
            game_over_text.get_rect(
                center=(WIDTH // 2, 285)
            )
        )

        screen.blit(
            score_text,
            score_text.get_rect(
                center=(WIDTH // 2, 365)
            )
        )

        screen.blit(
            restart_text,
            restart_text.get_rect(
                center=(WIDTH // 2, 425)
            )
        )

        screen.blit(
            quit_text,
            quit_text.get_rect(
                center=(WIDTH // 2, 465)
            )
        )

    pygame.display.flip()


pygame.quit()
sys.exit()
