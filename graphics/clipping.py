from .primitives import draw_line


# =====================================================
# Cohen-Sutherland (Recorte de linhas)
# =====================================================
INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


def _region_code(x, y, xmin, ymin, xmax, ymax):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= TOP
    elif y > ymax:
        code |= BOTTOM
    return code


def cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax):
    c0 = _region_code(x0, y0, xmin, ymin, xmax, ymax)
    c1 = _region_code(x1, y1, xmin, ymin, xmax, ymax)

    for _ in range(20):
        if (c0 | c1) == 0:
            return x0, y0, x1, y1
        if (c0 & c1) != 0:
            return None

        cout = c0 if c0 != 0 else c1
        dx = x1 - x0
        dy = y1 - y0

        if cout & TOP:
            x = x0 + dx * (ymin - y0) / dy if dy != 0 else x0
            y = ymin
        elif cout & BOTTOM:
            x = x0 + dx * (ymax - y0) / dy if dy != 0 else x0
            y = ymax
        elif cout & RIGHT:
            y = y0 + dy * (xmax - x0) / dx if dx != 0 else y0
            x = xmax
        elif cout & LEFT:
            y = y0 + dy * (xmin - x0) / dx if dx != 0 else y0
            x = xmin

        if cout == c0:
            x0, y0 = x, y
            c0 = _region_code(x0, y0, xmin, ymin, xmax, ymax)
        else:
            x1, y1 = x, y
            c1 = _region_code(x1, y1, xmin, ymin, xmax, ymax)

    return None


def draw_line_clipped(surface, x0, y0, x1, y1, color, xmin, ymin, xmax, ymax):
    result = cohen_sutherland(x0, y0, x1, y1, xmin, ymin, xmax, ymax)
    if result:
        draw_line(surface, *[int(v) for v in result], color)


def draw_polygon_clipped(surface, points, color, clip_rect):
    xmin, ymin, xmax, ymax = clip_rect
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        draw_line_clipped(surface, x0, y0, x1, y1, color, xmin, ymin, xmax, ymax)
