import math


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
