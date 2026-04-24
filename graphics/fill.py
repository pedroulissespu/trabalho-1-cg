from .primitives import set_pixel


# =====================================================
# Scanline Fill (polígonos)
# =====================================================
def scanline_fill(surface, points, color):
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(points)

    for y in range(y_min, y_max + 1):
        intersections = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if y0 == y1:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            if y < y0 or y >= y1:
                continue
            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersections.append(x)

        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            x_start = int(intersections[i])
            x_end = int(intersections[i + 1])
            for x in range(x_start, x_end + 1):
                set_pixel(surface, x, y, color)


# =====================================================
# Scanline Fill com gradiente por vértice
# =====================================================
def scanline_fill_gradient(surface, points, colors):
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(points)

    for y in range(y_min, y_max + 1):
        intersections = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            c0 = colors[i]
            c1 = colors[(i + 1) % n]

            if y0 == y1:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                c0, c1 = c1, c0
            if y < y0 or y >= y1:
                continue

            t = (y - y0) / (y1 - y0)
            x = x0 + t * (x1 - x0)
            r = c0[0] + t * (c1[0] - c0[0])
            g = c0[1] + t * (c1[1] - c0[1])
            b = c0[2] + t * (c1[2] - c0[2])
            intersections.append((x, r, g, b))

        intersections.sort(key=lambda v: v[0])
        for i in range(0, len(intersections) - 1, 2):
            xa, ra, ga, ba = intersections[i]
            xb, rb, gb, bb = intersections[i + 1]
            x_start = int(xa)
            x_end = int(xb)
            span = x_end - x_start if x_end != x_start else 1
            for x in range(x_start, x_end + 1):
                t = (x - x_start) / span
                cr = int(ra + t * (rb - ra))
                cg = int(ga + t * (gb - ga))
                cb = int(ba + t * (bb - ba))
                cr = max(0, min(255, cr))
                cg = max(0, min(255, cg))
                cb = max(0, min(255, cb))
                set_pixel(surface, x, y, (cr, cg, cb))


# =====================================================
# Scanline Fill com textura
# =====================================================
def scanline_fill_texture(surface, points, tex_coords, texture_pixels, tex_w, tex_h):
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(points)

    for y in range(y_min, y_max + 1):
        intersections = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            u0, v0 = tex_coords[i]
            u1, v1 = tex_coords[(i + 1) % n]

            if y0 == y1:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                u0, v0, u1, v1 = u1, v1, u0, v0
            if y < y0 or y >= y1:
                continue

            t = (y - y0) / (y1 - y0)
            x = x0 + t * (x1 - x0)
            u = u0 + t * (u1 - u0)
            v = v0 + t * (v1 - v0)
            intersections.append((x, u, v))

        intersections.sort(key=lambda val: val[0])
        for i in range(0, len(intersections) - 1, 2):
            xa, ua, va = intersections[i]
            xb, ub, vb = intersections[i + 1]
            x_start = int(xa)
            x_end = int(xb)
            span = x_end - x_start if x_end != x_start else 1
            for x in range(x_start, x_end + 1):
                t = (x - x_start) / span
                u = ua + t * (ub - ua)
                v = va + t * (vb - va)
                tx = int(u * (tex_w - 1)) % tex_w
                ty = int(v * (tex_h - 1)) % tex_h
                color = texture_pixels[ty][tx]
                set_pixel(surface, x, y, color)


def scanline_fill_texture_alpha(surface, points, tex_coords, texture_pixels, tex_w, tex_h):
    """Igual a scanline_fill_texture, mas pula pixels com alpha < 128."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(points)

    for y in range(y_min, y_max + 1):
        intersections = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            u0, v0 = tex_coords[i]
            u1, v1 = tex_coords[(i + 1) % n]

            if y0 == y1:
                continue
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
                u0, v0, u1, v1 = u1, v1, u0, v0
            if y < y0 or y >= y1:
                continue

            t = (y - y0) / (y1 - y0)
            x = x0 + t * (x1 - x0)
            u = u0 + t * (u1 - u0)
            v = v0 + t * (v1 - v0)
            intersections.append((x, u, v))

        intersections.sort(key=lambda val: val[0])
        for i in range(0, len(intersections) - 1, 2):
            xa, ua, va = intersections[i]
            xb, ub, vb = intersections[i + 1]
            x_start = int(xa)
            x_end = int(xb)
            span = x_end - x_start if x_end != x_start else 1
            for x in range(x_start, x_end + 1):
                t = (x - x_start) / span
                u = ua + t * (ub - ua)
                v = va + t * (vb - va)
                tx = int(u * (tex_w - 1)) % tex_w
                ty = int(v * (tex_h - 1)) % tex_h
                color = texture_pixels[ty][tx]
                if len(color) >= 4 and color[3] < 128:
                    continue
                set_pixel(surface, x, y, (color[0], color[1], color[2]))


# =====================================================
# Flood Fill (iterativo, 4-conectado)
# =====================================================
def flood_fill(surface, x, y, fill_color, boundary_color=None):
    x, y = int(x), int(y)
    w = surface.get_width()
    h = surface.get_height()
    if not (0 <= x < w and 0 <= y < h):
        return

    original_color = surface.get_at((x, y))[:3]
    if boundary_color is None:
        if original_color == fill_color[:3]:
            return
    else:
        if original_color == fill_color[:3] or original_color == boundary_color[:3]:
            return

    stack = [(x, y)]
    visited = set()

    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in visited:
            continue
        if not (0 <= cx < w and 0 <= cy < h):
            continue

        current = surface.get_at((cx, cy))[:3]

        if boundary_color is None:
            if current != original_color:
                continue
        else:
            if current == boundary_color[:3] or current == fill_color[:3]:
                continue

        visited.add((cx, cy))
        surface.set_at((cx, cy), fill_color)

        stack.append((cx + 1, cy))
        stack.append((cx - 1, cy))
        stack.append((cx, cy + 1))
        stack.append((cx, cy - 1))
