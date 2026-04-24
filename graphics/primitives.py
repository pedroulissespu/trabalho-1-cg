import math


# =====================================================
# Set Pixel (com verificação de limites)
# =====================================================
def set_pixel(surface, x, y, color):
    x, y = int(x), int(y)
    if 0 <= x < surface.get_width() and 0 <= y < surface.get_height():
        surface.set_at((x, y), color)


# =====================================================
# Bresenham - Rasterização de Reta
# =====================================================
def draw_line(surface, x0, y0, x1, y1, color):
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = abs(y1 - y0)
    ystep = 1 if y0 < y1 else -1
    d = 2 * dy - dx
    y = y0

    for x in range(x0, x1 + 1):
        if steep:
            set_pixel(surface, y, x, color)
        else:
            set_pixel(surface, x, y, color)
        if d > 0:
            y += ystep
            d -= 2 * dx
        d += 2 * dy


# =====================================================
# Bresenham - Circunferência
# =====================================================
def _circle_points(surface, cx, cy, x, y, color):
    set_pixel(surface, cx + x, cy + y, color)
    set_pixel(surface, cx - x, cy + y, color)
    set_pixel(surface, cx + x, cy - y, color)
    set_pixel(surface, cx - x, cy - y, color)
    set_pixel(surface, cx + y, cy + x, color)
    set_pixel(surface, cx - y, cy + x, color)
    set_pixel(surface, cx + y, cy - x, color)
    set_pixel(surface, cx - y, cy - x, color)


def draw_circle(surface, cx, cy, r, color):
    cx, cy, r = int(cx), int(cy), int(r)
    x = 0
    y = r
    d = 3 - 2 * r
    _circle_points(surface, cx, cy, x, y, color)
    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d += 4 * (x - y) + 10
        else:
            d += 4 * x + 6
        _circle_points(surface, cx, cy, x, y, color)


def draw_filled_circle(surface, cx, cy, r, color):
    """Círculo preenchido usando scanlines internas."""
    cx, cy, r = int(cx), int(cy), int(r)
    x = 0
    y = r
    d = 3 - 2 * r

    def _hline(x1, x2, yy):
        for xx in range(x1, x2 + 1):
            set_pixel(surface, xx, yy, color)

    def _fill_points(cx, cy, x, y):
        _hline(cx - x, cx + x, cy + y)
        _hline(cx - x, cx + x, cy - y)
        _hline(cx - y, cx + y, cy + x)
        _hline(cx - y, cx + y, cy - x)

    _fill_points(cx, cy, x, y)
    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d += 4 * (x - y) + 10
        else:
            d += 4 * x + 6
        _fill_points(cx, cy, x, y)


# =====================================================
# Bresenham - Elipse
# =====================================================
def draw_ellipse(surface, cx, cy, rx, ry, color):
    cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
    if rx == 0 or ry == 0:
        return

    x = 0
    y = ry
    rx2 = rx * rx
    ry2 = ry * ry
    px = 0
    py = 2 * rx2 * y

    # Região 1
    d1 = ry2 - rx2 * ry + 0.25 * rx2
    while px < py:
        set_pixel(surface, cx + x, cy + y, color)
        set_pixel(surface, cx - x, cy + y, color)
        set_pixel(surface, cx + x, cy - y, color)
        set_pixel(surface, cx - x, cy - y, color)
        x += 1
        px += 2 * ry2
        if d1 < 0:
            d1 += ry2 + px
        else:
            y -= 1
            py -= 2 * rx2
            d1 += ry2 + px - py

    # Região 2
    d2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        set_pixel(surface, cx + x, cy + y, color)
        set_pixel(surface, cx - x, cy + y, color)
        set_pixel(surface, cx + x, cy - y, color)
        set_pixel(surface, cx - x, cy - y, color)
        y -= 1
        py -= 2 * rx2
        if d2 > 0:
            d2 += rx2 - py
        else:
            x += 1
            px += 2 * ry2
            d2 += rx2 - py + px


def draw_filled_ellipse(surface, cx, cy, rx, ry, color):
    cx, cy, rx, ry = int(cx), int(cy), int(rx), int(ry)
    if rx == 0 or ry == 0:
        return
    for dy in range(-ry, ry + 1):
        val = 1.0 - (dy * dy) / (ry * ry)
        if val < 0:
            continue
        half_w = int(rx * math.sqrt(val))
        for dx in range(-half_w, half_w + 1):
            set_pixel(surface, cx + dx, cy + dy, color)


# =====================================================
# Desenho de polígono (contorno)
# =====================================================
def draw_polygon(surface, points, color):
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        draw_line(surface, x0, y0, x1, y1, color)
