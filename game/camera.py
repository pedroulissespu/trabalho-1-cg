from .config import SCREEN_W, SCREEN_H


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0
        self.target_zoom = 1.0

    def update(self, target_x, target_y):
        self.x += (target_x - SCREEN_W / 2 - self.x) * 0.1
        self.y += (target_y - SCREEN_H / 2 - self.y) * 0.1
        self.zoom += (self.target_zoom - self.zoom) * 0.05

    def world_to_screen(self, wx, wy):
        sx = (wx - self.x) * self.zoom
        sy = (wy - self.y) * self.zoom
        return sx, sy

    def screen_to_world(self, sx, sy):
        wx = sx / self.zoom + self.x
        wy = sy / self.zoom + self.y
        return wx, wy

    def get_clip_rect(self):
        x0, y0 = self.screen_to_world(0, 0)
        x1, y1 = self.screen_to_world(SCREEN_W, SCREEN_H)
        return (x0, y0, x1, y1)
