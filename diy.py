import pygame
import numpy as np

WIDTH = 300
HEIGHT = 300

SHOW_FIELD = True


def magnetic_field_dipole(
    pos: np.ndarray, dipole_moment: np.ndarray, magnet_center: np.ndarray
):
    r = pos - magnet_center
    r_mag = np.linalg.norm(r, axis=-1, keepdims=True)

    # Avoid singularity
    r_mag = np.maximum(r_mag, 0.01)

    r_hat = r / r_mag
    m_dot_r = np.sum(dipole_moment * r_hat, axis=-1, keepdims=True)

    B = (1 / r_mag**3) * (3 * m_dot_r * r_hat - dipole_moment)
    return B

def magnetic_field_dipole_single_pos(
    pos: np.ndarray, dipole_moment: np.ndarray, magnet_center: np.ndarray
):
    r = pos - magnet_center
    r_mag = np.linalg.norm(r, axis=-1, keepdims=True)

    # Avoid singularity
    r_mag = np.maximum(r_mag, 0.01)

    r_hat = r / r_mag
    m_dot_r = np.sum(dipole_moment * r_hat, axis=-1, keepdims=True)

    B = (1 / r_mag**3) * (3 * m_dot_r * r_hat - dipole_moment)
    return np.sum(B, axis=-2)


def mag_field(pos: np.ndarray):
    B = np.zeros(pos.shape, dtype=np.float32)

    for x in np.linspace(-0.9, 0.9, 25):
        for r in np.linspace(0, 2 * np.pi, 8, endpoint=False):
            y = np.cos(r) * 0.5
            z = np.sin(r) * 0.5

            B += magnetic_field_dipole(pos, np.array([1.0, 0, 0]), np.array([x, y, z]))
    
    return B

def mag_field_pos(pos: np.ndarray):
    

def screen_to_world(x, y):
    return (x / WIDTH * 2 - 1), -(y / WIDTH * 2 - 1)


def world_to_screen(x, y):
    """Convert world coordinates to screen coordinates"""
    screen_x = (x + 1.0) / 2.0 * WIDTH
    screen_y = (-y + 1.0) / 2.0 * WIDTH  # Flip Y for screen coords
    return int(screen_x), int(screen_y)


def world_rect(x, y, w, h):
    sx, sy = world_to_screen(x, y)
    sw = int(w * WIDTH / 2)
    sh = int(h * WIDTH / 2)
    return sx, sy, sw, sh


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Magnets :)")
    screen.fill(0)
    background = None
    B = None

    if SHOW_FIELD:
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill(0)

        screen_x = np.linspace(-1, 1, WIDTH, endpoint=False)
        screen_y = np.linspace(-1, 1, HEIGHT, endpoint=False)
        sx, sy = np.meshgrid(screen_x, screen_y)
        pos = np.stack([sx, sy, np.zeros_like(sx)], axis=-1)

        B = mag_field(pos)

        for sx in range(0, WIDTH):
            for sy in range(0, HEIGHT):
                r, g, b = np.clip(np.abs(B[sy,sx]), 0, 255)

                background.set_at((sx, sy), (int(r), int(g), int(b)))

    p = np.array([-0.5, 0.0, 0.0])
    q = 0.1
    v = np.array([0.5, 0.0, 0.0])
    dt = 0.0001

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(0x000000)

        pygame.draw.circle(screen, 0x00FF00, world_to_screen(p[0], p[1]), 3)

        B_pos = mag_field(p)

        F = q * np.cross(v, B_pos)

        p += v * dt
        v += F * dt

        pygame.display.update()


if __name__ == "__main__":
    main()
