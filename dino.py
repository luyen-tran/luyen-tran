#!/usr/bin/env python3
"""
ASCII Dino - mo phong Chrome Dino game chay trong terminal.
Dieu khien: phim SPACE / mui ten LEN de nhay, Q de thoat.
"""

import sys
import os
import time
import random
import termios
import tty
import select

# ----- ASCII sprites -----
# Dino dung/chay (2 frame doi chan), cao 4 dong
DINO_RUN = [
    [
        "      __ ",
        "  ___/ o\\",
        "  \\____  \\",
        "    /|  |\\",
    ],
    [
        "      __ ",
        "  ___/ o\\",
        "  \\____  \\",
        "    |\\  /|",
    ],
]

# Dino khi nhay (chan duoi)
DINO_JUMP = [
    "      __ ",
    "  ___/ o\\",
    "  \\____  \\",
    "    /    \\",
]

# Dino khi crash (mat X)
DINO_DEAD = [
    "      __ ",
    "  ___/ x\\",
    "  \\____  \\",
    "    /|  |\\",
]

CACTUS = [
    "  _  ",
    " | |_",
    "_| | |",
    " |___|",
]

GROUND_Y = 12          # dong mat dat (dinh chan dino khi dung)
DINO_X = 6             # vi tri cot cua dino
WIDTH = 70            # be rong man hinh
GRAVITY = 1.2
JUMP_VELOCITY = -4.6


def draw(buf):
    """Ve buffer ra terminal (di chuyen con tro ve dau, khong clear de do nhay)."""
    sys.stdout.write("\033[H")
    sys.stdout.write("\n".join("".join(row) for row in buf))
    sys.stdout.flush()


def blank_buffer(height):
    return [[" "] * WIDTH for _ in range(height)]


def stamp(buf, sprite, x, top):
    """Dat sprite (list cac dong) vao buffer tai cot x, dong top."""
    for dy, line in enumerate(sprite):
        y = top + dy
        if 0 <= y < len(buf):
            for dx, ch in enumerate(line):
                px = x + dx
                if 0 <= px < WIDTH and ch != " ":
                    buf[y][px] = ch


def main():
    height = GROUND_Y + 2
    dino_y = 0.0          # offset so voi mat dat (am = tren khong)
    velocity = 0.0
    jumping = False
    obstacles = []         # danh sach vi tri x cua cactus
    spawn_timer = 0
    speed = 1.0
    score = 0
    frame = 0
    dead = False

    # Setup terminal non-blocking
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    sys.stdout.write("\033[2J\033[?25l")   # clear + an con tro
    try:
        tty.setcbreak(fd)
        while True:
            # ---- input ----
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                key = sys.stdin.read(1)
                if key in ("q", "Q"):
                    break
                if key in (" ", "\n") and not jumping and not dead:
                    velocity = JUMP_VELOCITY
                    jumping = True
                if (key in (" ", "\n")) and dead:
                    # restart
                    dino_y, velocity, jumping = 0.0, 0.0, False
                    obstacles, spawn_timer, speed, score, dead = [], 0, 1.0, 0, False

            if not dead:
                # ---- physics nhay ----
                if jumping:
                    dino_y += velocity
                    velocity += GRAVITY
                    if dino_y >= 0:
                        dino_y, velocity, jumping = 0.0, 0.0, False

                # ---- spawn cactus ----
                spawn_timer -= 1
                if spawn_timer <= 0:
                    obstacles.append(WIDTH - 6)
                    spawn_timer = random.randint(18, 34)

                # ---- di chuyen cactus + tang toc ----
                step = int(speed) + 1
                obstacles = [x - step for x in obstacles]
                obstacles = [x for x in obstacles if x > -6]
                speed += 0.01
                score += 1

                # ---- va cham ----
                dino_top = GROUND_Y - 4 + int(round(dino_y))
                dino_feet = dino_top + 3
                for ox in obstacles:
                    if DINO_X < ox + 4 and DINO_X + 8 > ox:   # chong lap cot
                        if dino_feet >= GROUND_Y - 1:          # dino dang o mat dat
                            dead = True

            # ---- ve ----
            buf = blank_buffer(height)
            # mat dat
            for x in range(WIDTH):
                buf[GROUND_Y][x] = "_"
            # cactus
            for ox in obstacles:
                stamp(buf, CACTUS, ox, GROUND_Y - 4)
            # dino
            dino_top = GROUND_Y - 4 + int(round(dino_y))
            if dead:
                sprite = DINO_DEAD
            elif jumping:
                sprite = DINO_JUMP
            else:
                sprite = DINO_RUN[(frame // 3) % 2]
            stamp(buf, sprite, DINO_X, dino_top)
            # HUD
            hud = f" SCORE {score:05d}   SPEED {speed:4.1f} "
            for i, ch in enumerate(hud):
                if i < WIDTH:
                    buf[0][i] = ch
            if dead:
                msg = "  GAME OVER - SPACE de choi lai, Q de thoat  "
                start = (WIDTH - len(msg)) // 2
                for i, ch in enumerate(msg):
                    buf[GROUND_Y // 2][start + i] = ch

            draw(buf)
            frame += 1
            time.sleep(0.05)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write("\033[?25h\033[2J\033[H")   # hien con tro + clear
        sys.stdout.flush()


if __name__ == "__main__":
    main()
