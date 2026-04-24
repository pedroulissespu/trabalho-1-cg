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
        # x² / rx² + dy² / ry² = 1 => x = rx * sqrt(1 - dy²/ry²)
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
    """
    Preenche polígono com gradiente interpolado por vértice.
    points: lista de (x, y)
    colors: lista de (r, g, b) correspondente a cada vértice
    """
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(points)

    for y in range(y_min, y_max + 1):
        intersections = []  # (x, r, g, b)
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
    """
    Preenche polígono com textura mapeada.
    points: [(x,y), ...]
    tex_coords: [(u,v), ...] coordenadas de textura normalizadas [0,1]
    texture_pixels: array 2D de pixels da textura (acessado por texture_pixels[y][x])
    tex_w, tex_h: dimensões da textura
    """
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(points)

    for y in range(y_min, y_max + 1):
        intersections = []  # (x, u, v)
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


# =====================================================
# Flood Fill (iterativo, 4-conectado)
# =====================================================
def flood_fill(surface, x, y, fill_color, boundary_color=None):
    """
    Se boundary_color for None, faz flood fill clássico (substitui cor original).
    Se boundary_color for dado, faz boundary fill.
    """
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


# =====================================================
# Matrizes 2D Homogêneas
# =====================================================
def identity():
    return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def translation(tx, ty):
    return [[1, 0, tx], [0, 1, ty], [0, 0, 1]]


def scale(sx, sy):
    return [[sx, 0, 0], [0, sy, 0], [0, 0, 1]]


def rotation(theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def mat_mult(a, b):
    r = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                r[i][j] += a[i][k] * b[k][j]
    return r


def apply_transform(m, points):
    result = []
    for x, y in points:
        xn = m[0][0] * x + m[0][1] * y + m[0][2]
        yn = m[1][0] * x + m[1][1] * y + m[1][2]
        result.append((xn, yn))
    return result


def transform_point(m, x, y):
    xn = m[0][0] * x + m[0][1] * y + m[0][2]
    yn = m[1][0] * x + m[1][1] * y + m[1][2]
    return xn, yn


# =====================================================
# Janela -> Viewport
# =====================================================
def window_to_viewport(window, viewport):
    wxmin, wymin, wxmax, wymax = window
    vxmin, vymin, vxmax, vymax = viewport

    sx = (vxmax - vxmin) / (wxmax - wxmin) if wxmax != wxmin else 1
    sy = (vymin - vymax) / (wymax - wymin) if wymax != wymin else 1

    m = identity()
    m = mat_mult(translation(-wxmin, -wymin), m)
    m = mat_mult(scale(sx, sy), m)
    m = mat_mult(translation(vxmin, vymax), m)
    return m


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
    """Retorna None se totalmente fora, ou (x0, y0, x1, y1) recortados."""
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


# =====================================================
# Utilitário: desenhar texto pixel-a-pixel (bitmap font)
# =====================================================
FONT_3x5 = {
    'A': ["111", "101", "111", "101", "101"],
    'B': ["110", "101", "110", "101", "110"],
    'C': ["111", "100", "100", "100", "111"],
    'D': ["110", "101", "101", "101", "110"],
    'E': ["111", "100", "110", "100", "111"],
    'F': ["111", "100", "110", "100", "100"],
    'G': ["111", "100", "101", "101", "111"],
    'H': ["101", "101", "111", "101", "101"],
    'I': ["111", "010", "010", "010", "111"],
    'J': ["001", "001", "001", "101", "111"],
    'K': ["101", "110", "100", "110", "101"],
    'L': ["100", "100", "100", "100", "111"],
    'M': ["101", "111", "111", "101", "101"],
    'N': ["101", "111", "111", "111", "101"],
    'O': ["111", "101", "101", "101", "111"],
    'P': ["111", "101", "111", "100", "100"],
    'Q': ["111", "101", "101", "111", "001"],
    'R': ["111", "101", "111", "110", "101"],
    'S': ["111", "100", "111", "001", "111"],
    'T': ["111", "010", "010", "010", "010"],
    'U': ["101", "101", "101", "101", "111"],
    'V': ["101", "101", "101", "101", "010"],
    'W': ["101", "101", "111", "111", "101"],
    'X': ["101", "101", "010", "101", "101"],
    'Y': ["101", "101", "010", "010", "010"],
    'Z': ["111", "001", "010", "100", "111"],
    '0': ["111", "101", "101", "101", "111"],
    '1': ["010", "110", "010", "010", "111"],
    '2': ["111", "001", "111", "100", "111"],
    '3': ["111", "001", "111", "001", "111"],
    '4': ["101", "101", "111", "001", "001"],
    '5': ["111", "100", "111", "001", "111"],
    '6': ["111", "100", "111", "101", "111"],
    '7': ["111", "001", "001", "001", "001"],
    '8': ["111", "101", "111", "101", "111"],
    '9': ["111", "101", "111", "001", "111"],
    ' ': ["000", "000", "000", "000", "000"],
    ':': ["000", "010", "000", "010", "000"],
    '-': ["000", "000", "111", "000", "000"],
    '.': ["000", "000", "000", "000", "010"],
    '!': ["010", "010", "010", "000", "010"],
    '/': ["001", "001", "010", "100", "100"],
    '+': ["000", "010", "111", "010", "000"],
    '<': ["001", "010", "100", "010", "001"],
    '>': ["100", "010", "001", "010", "100"],
    '(': ["010", "100", "100", "100", "010"],
    ')': ["010", "001", "001", "001", "010"],
    ',': ["000", "000", "000", "010", "100"],
}


def draw_text(surface, text, x, y, color, scale_val=1):
    """Desenha texto usando fonte bitmap 3x5."""
    cursor_x = x
    for ch in text.upper():
        glyph = FONT_3x5.get(ch)
        if glyph is None:
            cursor_x += 4 * scale_val
            continue
        for row_idx, row in enumerate(glyph):
            for col_idx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale_val):
                        for sx in range(scale_val):
                            set_pixel(surface, cursor_x + col_idx * scale_val + sx,
                                      y + row_idx * scale_val + sy, color)
        cursor_x += (len(glyph[0]) + 1) * scale_val


def text_width(text, scale_val=1):
    return len(text) * 4 * scale_val - scale_val


def draw_text_centered(surface, text, cx, cy, color, scale_val=1):
    w = text_width(text, scale_val)
    h = 5 * scale_val
    draw_text(surface, text, cx - w // 2, cy - h // 2, color, scale_val)


# =====================================================
# Utilitário: desenhar retângulo
# =====================================================
def draw_rect(surface, x, y, w, h, color):
    draw_line(surface, x, y, x + w, y, color)
    draw_line(surface, x + w, y, x + w, y + h, color)
    draw_line(surface, x + w, y + h, x, y + h, color)
    draw_line(surface, x, y + h, x, y, color)


def fill_rect(surface, x, y, w, h, color):
    x, y, w, h = int(x), int(y), int(w), int(h)
    if w > 0 and h > 0:
        # Clipa ao tamanho da superfície
        sw, sh = surface.get_width(), surface.get_height()
        x2, y2 = min(x + w, sw), min(y + h, sh)
        x, y = max(0, x), max(0, y)
        if x2 > x and y2 > y:
            surface.fill(color, (x, y, x2 - x, y2 - y))
