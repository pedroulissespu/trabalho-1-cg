import math

from graphics import (
    set_pixel, draw_line, draw_circle, draw_filled_circle,
    draw_ellipse, draw_filled_ellipse,
    draw_polygon, scanline_fill, scanline_fill_gradient, scanline_fill_texture,
    scanline_fill_texture_alpha,
    flood_fill, draw_text, draw_text_centered, text_width,
    draw_rect, fill_rect,
    identity, rotation, scale, mat_mult, apply_transform, transform_point,
    window_to_viewport, draw_line_clipped, draw_polygon_clipped,
)
from .config import (
    SCREEN_W, SCREEN_H, WORLD_W, WORLD_H,
    PLAYER_SHAPE, GRADE_SHAPES, BOSS_SHAPE, PROJ_SHAPE, XP_SHAPE,
    GRADE_COLORS,
)
from .state import GameState
from .assets import Assets
from .powers import POWER_DEFS


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def render(self, game):
        self.screen.fill((0, 0, 0))

        if game.state == GameState.TITLE:
            self._render_title(game)
        elif game.state in (GameState.PLAYING, GameState.PAUSED, GameState.LEVEL_UP):
            self._render_game(game)
            if game.state == GameState.PAUSED:
                self._render_pause()
            elif game.state == GameState.LEVEL_UP:
                self._render_level_up(game)
        elif game.state == GameState.GAME_OVER:
            self._render_game(game)
            self._render_game_over(game)
        elif game.state == GameState.VICTORY:
            self._render_game(game)
            self._render_victory(game)

    def _render_title(self, game):
        scr = self.screen
        anim = game.title_anim

        # Fundo escuro (lousa)
        scr.fill((15, 25, 15))

        # Polígono com gradiente (quadro verde)
        grad_pts = [(40, 60), (SCREEN_W - 40, 60), (SCREEN_W - 40, 350), (40, 350)]
        grad_colors = [(20, 60, 30), (30, 80, 40), (25, 70, 35), (15, 50, 25)]
        scanline_fill_gradient(scr, grad_pts, grad_colors)

        # Moldura do quadro com retas (Bresenham)
        for i in range(4):
            draw_rect(scr, 38 + i, 58 + i, SCREEN_W - 78 - 2 * i, 294 - 2 * i,
                      (120 + i * 20, 80 + i * 10, 30))

        # Título
        bob = int(math.sin(anim * 2) * 4)
        draw_text_centered(scr, "SOBREVIVA AO SEMESTRE", SCREEN_W // 2, 100 + bob,
                           (255, 255, 220), 4)
        draw_text_centered(scr, "DERROTE AS NOTAS BAIXAS", SCREEN_W // 2, 145,
                           (200, 200, 150), 2)

        # Círculos decorativos — notas flutuando (Bresenham circunferência)
        grades = ["0", "1", "2", "3", "0"]
        for i in range(5):
            cx = 120 + i * 140
            cy = 200
            r = int(18 + 6 * math.sin(anim + i))
            cval = int(180 + 75 * math.sin(anim + i * 0.7))
            draw_circle(scr, cx, cy, r, (cval, 50, 50))
            draw_text_centered(scr, grades[i], cx, cy, (255, 200, 200), 2)

        # Elipses decorativas (Bresenham elipse)
        for i in range(3):
            cx = 200 + i * 200
            cy = 280
            rx = int(25 + 10 * math.sin(anim * 1.5 + i))
            ry = int(12 + 5 * math.cos(anim * 1.5 + i))
            draw_filled_ellipse(scr, cx, cy, rx, ry, (80, 50, 20))
            draw_ellipse(scr, cx, cy, rx, ry, (140, 90, 40))

        # Ícone aluno (círculo preenchido com flood fill)
        pcx, pcy = SCREEN_W // 2, 330
        draw_circle(scr, pcx, pcy, 15, (100, 180, 255))
        flood_fill(scr, pcx, pcy, (100, 180, 255), (100, 180, 255))
        # Capelo
        draw_line(scr, pcx - 18, pcy - 12, pcx + 18, pcy - 12, (255, 220, 50))
        draw_line(scr, pcx - 18, pcy - 12, pcx, pcy - 22, (255, 220, 50))
        draw_line(scr, pcx + 18, pcy - 12, pcx, pcy - 22, (255, 220, 50))

        # Raios de conhecimento
        for i in range(8):
            a = anim + i * math.pi / 4
            x1 = pcx + int(math.cos(a) * 25)
            y1 = pcy + int(math.sin(a) * 25)
            x2 = pcx + int(math.cos(a) * 40)
            y2 = pcy + int(math.sin(a) * 40)
            draw_line(scr, x1, y1, x2, y2, (255, 255, 150))

        # Boss preview
        draw_text_centered(scr, "BOSS FINAL", SCREEN_W // 2, 380, (200, 100, 50), 2)
        draw_filled_ellipse(scr, SCREEN_W // 2, 410, 30, 18, (60, 30, 10))
        draw_ellipse(scr, SCREEN_W // 2, 410, 30, 18, (120, 70, 30))
        draw_text_centered(scr, "NEGRESCO", SCREEN_W // 2, 410, (200, 180, 140), 1)

        # Menu
        items = ["JOGAR", "SAIR"]
        for idx, item in enumerate(items):
            cy = 460 + idx * 35
            color = (255, 255, 0) if idx == game.menu_selection else (180, 180, 180)
            if idx == game.menu_selection:
                draw_text_centered(scr, "> " + item + " <", SCREEN_W // 2, cy, color, 3)
            else:
                draw_text_centered(scr, item, SCREEN_W // 2, cy, color, 3)

        draw_text_centered(scr, "WASD MOVER  +/- ZOOM  ESC PAUSAR",
                           SCREEN_W // 2, 560, (100, 100, 100), 2)

    def _render_game(self, game):
        scr = self.screen
        cam = game.camera

        # Chão
        self._render_ground(cam)

        # Borda do mundo (com recorte Cohen-Sutherland)
        corners = [(0, 0), (WORLD_W, 0), (WORLD_W, WORLD_H), (0, WORLD_H)]
        screen_corners = [cam.world_to_screen(x, y) for x, y in corners]
        clip_screen = (0, 0, SCREEN_W - 1, SCREEN_H - 1)
        draw_polygon_clipped(scr, screen_corners, (100, 100, 100), clip_screen)

        # XP orbs
        for orb in game.xp_orbs:
            sx, sy = cam.world_to_screen(orb.x, orb.y)
            if 0 <= sx < SCREEN_W and 0 <= sy < SCREEN_H:
                pts = self._transform_shape(XP_SHAPE, orb.x, orb.y, 0, cam)
                colors = [(50, 255, 100), (150, 255, 50), (50, 200, 80), (100, 255, 180)]
                scanline_fill_gradient(scr, pts, colors)
                draw_text_centered(scr, "+", int(sx), int(sy), (255, 255, 255), 1)

        # Inimigos
        for e in game.enemies:
            sx, sy = cam.world_to_screen(e.x, e.y)
            if -40 < sx < SCREEN_W + 40 and -40 < sy < SCREEN_H + 40:
                if e.is_boss:
                    self._render_boss(e, sx, sy, cam)
                else:
                    sc = 1.0 + (e.kind * 0.3)
                    shape = GRADE_SHAPES[e.kind]
                    fill_c, border_c, label = GRADE_COLORS[e.kind]

                    sprite_data = Assets.grade_sprites.get(e.kind)
                    if sprite_data:
                        pts = self._transform_shape(shape, e.x, e.y, 0, cam, sc)
                        pixels, tw, th = sprite_data
                        tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
                        scanline_fill_texture_alpha(scr, pts, tex_coords,
                                                   pixels, tw, th)
                    else:
                        wobble = math.sin(e.anim_timer) * 0.1
                        pts = self._transform_shape(shape, e.x, e.y, wobble, cam, sc)
                        scanline_fill(scr, pts, fill_c)
                        draw_text_centered(scr, label, int(sx), int(sy),
                                           (255, 255, 255), 2)
                    draw_polygon(scr, pts, border_c)

                # Barra de HP
                if e.hp < e.max_hp:
                    bar_w = 20 if not e.is_boss else 50
                    ratio = e.hp / e.max_hp
                    bar_color = (255, 50, 50) if not e.is_boss else (255, 200, 0)
                    fill_rect(scr, sx - bar_w / 2, sy - 20, bar_w * ratio, 3, bar_color)
                    draw_rect(scr, sx - bar_w / 2, sy - 20, bar_w, 3, (200, 200, 200))

        # Projéteis do jogador
        for p in game.projectiles:
            sx, sy = cam.world_to_screen(p.x, p.y)
            if -10 < sx < SCREEN_W + 10 and -10 < sy < SCREEN_H + 10:
                pts = self._transform_shape(PROJ_SHAPE, p.x, p.y, p.angle, cam)
                if Assets.lapis_sprite:
                    tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
                    scanline_fill_texture_alpha(scr, pts, tex_coords,
                                               Assets.lapis_sprite,
                                               Assets.lapis_sprite_w,
                                               Assets.lapis_sprite_h)
                else:
                    scanline_fill(scr, pts, (180, 120, 50))
                    draw_polygon(scr, pts, (220, 170, 80))

        # Projéteis do boss
        for bp in game.boss_projectiles:
            sx, sy = cam.world_to_screen(bp.x, bp.y)
            if -10 < sx < SCREEN_W + 10 and -10 < sy < SCREEN_H + 10:
                draw_filled_circle(scr, int(sx), int(sy), 5, (255, 60, 60))
                draw_circle(scr, int(sx), int(sy), 5, (255, 200, 100))

        # Jogador (aluno)
        blink = game.player.invincible > 0 and (game.frame % 4 < 2)
        if not blink:
            pts = self._transform_shape(PLAYER_SHAPE, game.player.x, game.player.y,
                                        game.player.angle, cam)
            player_colors = [
                (40, 100, 200), (60, 140, 230), (30, 80, 180),
                (50, 120, 210), (35, 90, 190), (45, 110, 220)
            ]
            scanline_fill_gradient(scr, pts, player_colors)
            draw_polygon(scr, pts, (150, 200, 255))

        # HUD
        self._render_hud(game)

        # Minimapa
        self._render_minimap(game)

        # Aviso de boss
        if game.boss_spawned and game.boss_alive:
            if game.frame % 60 < 30:
                draw_text_centered(scr, "BOSS: PROF. NEGRESCO",
                                   SCREEN_W // 2, 50, (255, 100, 50), 3)

    def _render_boss(self, e, sx, sy, cam):
        scr = self.screen
        if Assets.boss_sprite:
            boss_sc = 1.5
            pts = self._transform_shape(BOSS_SHAPE, e.x, e.y, e.anim_timer * 0.3, cam, boss_sc)
            tex_coords = []
            for px, py in BOSS_SHAPE:
                u = (px + 32) / 64
                v = (py + 32) / 64
                tex_coords.append((max(0, min(1, u)), max(0, min(1, v))))
            scanline_fill_texture(scr, pts, tex_coords,
                                  Assets.boss_sprite, Assets.boss_sprite_w, Assets.boss_sprite_h)
            draw_polygon(scr, pts, (180, 120, 60))
        else:
            boss_sc = 1.5
            pts = self._transform_shape(BOSS_SHAPE, e.x, e.y, e.anim_timer * 0.3, cam, boss_sc)
            boss_colors = []
            for i in range(len(pts)):
                shade = 40 + (i * 15) % 60
                boss_colors.append((shade + 30, shade, shade - 10 if shade > 10 else 0))
            scanline_fill_gradient(scr, pts, boss_colors)
            draw_polygon(scr, pts, (150, 100, 40))

        draw_text_centered(scr, "NEGRESCO", int(sx), int(sy) - 35, (255, 200, 100), 2)
        bar_w = 60
        ratio = e.hp / e.max_hp
        fill_rect(scr, sx - bar_w / 2, sy + 35, bar_w * ratio, 4, (255, 50, 50))
        draw_rect(scr, sx - bar_w / 2, sy + 35, bar_w, 4, (255, 200, 100))

    def _render_ground(self, cam):
        scr = self.screen

        # Fundo sólido do mundo
        w_tl = cam.world_to_screen(0, 0)
        w_br = cam.world_to_screen(WORLD_W, WORLD_H)
        rx = max(0, int(w_tl[0]))
        ry = max(0, int(w_tl[1]))
        rw = min(SCREEN_W, int(w_br[0])) - rx
        rh = min(SCREEN_H, int(w_br[1])) - ry
        if rw > 0 and rh > 0:
            scr.fill((45, 55, 45), (rx, ry, rw, rh))

        # Grid com linhas Bresenham
        grid_size = 128
        x0w, y0w = cam.screen_to_world(0, 0)
        x1w, y1w = cam.screen_to_world(SCREEN_W, SCREEN_H)

        gx_start = int(x0w // grid_size) * grid_size
        for gx in range(gx_start, int(x1w) + grid_size, grid_size):
            if 0 <= gx <= WORLD_W:
                sx, sy0 = cam.world_to_screen(gx, max(0, y0w))
                _, sy1 = cam.world_to_screen(gx, min(WORLD_H, y1w))
                draw_line_clipped(scr, int(sx), int(sy0), int(sx), int(sy1),
                                  (55, 70, 55), 0, 0, SCREEN_W - 1, SCREEN_H - 1)

        gy_start = int(y0w // grid_size) * grid_size
        for gy in range(gy_start, int(y1w) + grid_size, grid_size):
            if 0 <= gy <= WORLD_H:
                sx0, sy = cam.world_to_screen(max(0, x0w), gy)
                sx1, _ = cam.world_to_screen(min(WORLD_W, x1w), gy)
                draw_line_clipped(scr, int(sx0), int(sy), int(sx1), int(sy),
                                  (55, 70, 55), 0, 0, SCREEN_W - 1, SCREEN_H - 1)

        # Textura mapeada em área decorativa (centro do mundo)
        tex_world_x, tex_world_y = WORLD_W // 2 - 64, WORLD_H // 2 - 64
        tex_corners_w = [
            (tex_world_x, tex_world_y), (tex_world_x + 128, tex_world_y),
            (tex_world_x + 128, tex_world_y + 128), (tex_world_x, tex_world_y + 128)
        ]
        tex_corners_s = [cam.world_to_screen(cx, cy) for cx, cy in tex_corners_w]
        xs = [c[0] for c in tex_corners_s]
        ys = [c[1] for c in tex_corners_s]
        if max(xs) > 0 and min(xs) < SCREEN_W and max(ys) > 0 and min(ys) < SCREEN_H:
            tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
            scanline_fill_texture(scr, tex_corners_s, tex_coords,
                                  Assets.ground_tex, Assets.ground_tex_w, Assets.ground_tex_h)

    def _transform_shape(self, shape, wx, wy, angle, cam, extra_scale=1.0):
        m = identity()
        m = mat_mult(rotation(angle), m)
        m = mat_mult(scale(extra_scale * cam.zoom, extra_scale * cam.zoom), m)
        pts = apply_transform(m, shape)
        sx, sy = cam.world_to_screen(wx, wy)
        return [(px + sx, py + sy) for px, py in pts]

    @staticmethod
    def _score_to_grade(score):
        grade = min(10.0, score / 300.0)
        if grade >= 9.0:
            letter = "A"
        elif grade >= 8.0:
            letter = "B+"
        elif grade >= 7.0:
            letter = "B"
        elif grade >= 6.0:
            letter = "C"
        elif grade >= 5.0:
            letter = "D"
        elif grade >= 4.0:
            letter = "D-"
        else:
            letter = "F"
        return grade, letter

    def _render_hud(self, game):
        scr = self.screen
        p = game.player

        # Barra de HP
        bar_x, bar_y, bar_w, bar_h = 10, 10, 200, 14
        fill_rect(scr, bar_x, bar_y, bar_w, bar_h, (40, 40, 40))
        hp_ratio = max(0, p.hp / p.max_hp)
        hp_color = (50, 220, 50) if hp_ratio > 0.5 else (220, 220, 50) if hp_ratio > 0.25 else (220, 50, 50)
        fill_rect(scr, bar_x + 1, bar_y + 1, int((bar_w - 2) * hp_ratio), bar_h - 2, hp_color)
        draw_rect(scr, bar_x, bar_y, bar_w, bar_h, (200, 200, 200))
        draw_text(scr, f"ENERGIA {p.hp}/{p.max_hp}", bar_x + 4, bar_y + 4, (255, 255, 255), 1)

        # Barra de XP
        xp_y = bar_y + bar_h + 4
        fill_rect(scr, bar_x, xp_y, bar_w, 8, (20, 20, 40))
        xp_ratio = p.xp / p.xp_next if p.xp_next > 0 else 0
        fill_rect(scr, bar_x + 1, xp_y + 1, int((bar_w - 2) * xp_ratio), 6, (100, 100, 255))
        draw_rect(scr, bar_x, xp_y, bar_w, 8, (150, 150, 200))

        # Período e Nota
        grade, letter = self._score_to_grade(game.score)
        draw_text(scr, f"PERIODO {p.level}", bar_x, xp_y + 14, (200, 200, 255), 2)
        draw_text(scr, f"NOTA {grade:.1f} ({letter})", bar_x + 120, xp_y + 14, (255, 255, 200), 2)

        # Timer do semestre
        secs = game.semester_timer // 60
        boss_secs = game.boss_spawn_time // 60
        remaining = max(0, boss_secs - secs)
        r_min = remaining // 60
        r_sec = remaining % 60
        if not game.boss_spawned:
            draw_text(scr, f"BOSS EM {r_min}:{r_sec:02d}", SCREEN_W - 170, 10, (255, 180, 80), 2)
        else:
            draw_text(scr, "BOSS ATIVO", SCREEN_W - 150, 10, (255, 80, 80), 2)

        draw_text(scr, f"NOTAS {len(game.enemies)}", SCREEN_W - 150, 30, (200, 200, 200), 1)

        # Poderes ativos
        active = game.powers.get_active()
        if active:
            pw_y = xp_y + 30
            for pid, lvl in active:
                pdef = POWER_DEFS[pid]
                draw_filled_circle(scr, bar_x + 6, pw_y + 4, 5, pdef["color"])
                draw_text(scr, pdef["icon"], bar_x + 3, pw_y + 1, (255, 255, 255), 1)
                lvl_str = "I" * lvl
                draw_text(scr, f"{pdef['name']} {lvl_str}", bar_x + 14, pw_y + 1,
                          pdef["color"], 1)
                pw_y += 10

    def _render_minimap(self, game):
        scr = self.screen
        vp_x, vp_y, vp_w, vp_h = SCREEN_W - 160, SCREEN_H - 120, 150, 110

        fill_rect(scr, vp_x, vp_y, vp_w, vp_h, (10, 10, 20))
        draw_rect(scr, vp_x, vp_y, vp_w, vp_h, (100, 100, 100))

        world_window = (0, 0, WORLD_W, WORLD_H)
        viewport = (vp_x, vp_y, vp_x + vp_w, vp_y + vp_h)
        m = window_to_viewport(world_window, viewport)
        clip = (vp_x, vp_y, vp_x + vp_w, vp_y + vp_h)

        # Jogador
        px, py = transform_point(m, game.player.x, game.player.y)
        draw_filled_circle(scr, int(px), int(py), 3, (50, 150, 255))

        # Inimigos
        for e in game.enemies:
            ex, ey = transform_point(m, e.x, e.y)
            if vp_x <= ex <= vp_x + vp_w and vp_y <= ey <= vp_y + vp_h:
                set_pixel(scr, int(ex), int(ey), (255, 80, 80))

        # Câmera view rect (Cohen-Sutherland)
        cx0, cy0 = game.camera.screen_to_world(0, 0)
        cx1, cy1 = game.camera.screen_to_world(SCREEN_W, SCREEN_H)
        cam_corners = [(cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1)]
        cam_screen = apply_transform(m, cam_corners)
        draw_polygon_clipped(scr, cam_screen, (255, 255, 0), clip)

    def _render_pause(self):
        scr = self.screen
        fill_rect(scr, SCREEN_W // 2 - 180, SCREEN_H // 2 - 50, 360, 100, (0, 0, 0))
        draw_rect(scr, SCREEN_W // 2 - 180, SCREEN_H // 2 - 50, 360, 100, (200, 200, 0))
        draw_text_centered(scr, "AULA PAUSADA", SCREEN_W // 2, SCREEN_H // 2 - 20,
                           (255, 255, 0), 4)
        draw_text_centered(scr, "P PARA CONTINUAR", SCREEN_W // 2, SCREEN_H // 2 + 30,
                           (200, 200, 200), 2)

    def _render_game_over(self, game):
        scr = self.screen
        grade, _ = self._score_to_grade(game.score)
        grade = min(grade, 4.9)
        letter = "F" if grade < 3.0 else "D-" if grade < 4.0 else "D"
        fill_rect(scr, SCREEN_W // 2 - 180, SCREEN_H // 2 - 80, 360, 160, (30, 0, 0))
        draw_rect(scr, SCREEN_W // 2 - 180, SCREEN_H // 2 - 80, 360, 160, (255, 50, 50))
        draw_text_centered(scr, "REPROVADO", SCREEN_W // 2, SCREEN_H // 2 - 50,
                           (255, 50, 50), 5)
        draw_text_centered(scr, "O SEMESTRE TE VENCEU",
                           SCREEN_W // 2, SCREEN_H // 2, (255, 180, 180), 2)
        draw_text_centered(scr, f"NOTA FINAL {grade:.1f} ({letter})",
                           SCREEN_W // 2, SCREEN_H // 2 + 25, (255, 255, 200), 3)
        draw_text_centered(scr, "ENTER PARA TENTAR DE NOVO",
                           SCREEN_W // 2, SCREEN_H // 2 + 55, (200, 200, 200), 2)

    def _render_victory(self, game):
        scr = self.screen
        grade, _ = self._score_to_grade(game.score)
        grade = max(grade, 6.0)
        if grade >= 9.0: letter = "A"
        elif grade >= 8.0: letter = "B+"
        elif grade >= 7.0: letter = "B"
        else: letter = "C"
        fill_rect(scr, SCREEN_W // 2 - 200, SCREEN_H // 2 - 90, 400, 180, (0, 20, 0))
        draw_rect(scr, SCREEN_W // 2 - 200, SCREEN_H // 2 - 90, 400, 180, (50, 255, 50))
        draw_text_centered(scr, "APROVADO", SCREEN_W // 2, SCREEN_H // 2 - 55,
                           (50, 255, 50), 5)
        draw_text_centered(scr, "VOCE SOBREVIVEU AO SEMESTRE",
                           SCREEN_W // 2, SCREEN_H // 2 - 10, (200, 255, 200), 2)
        draw_text_centered(scr, "PROF NEGRESCO DERROTADO",
                           SCREEN_W // 2, SCREEN_H // 2 + 15, (255, 220, 100), 2)
        draw_text_centered(scr, f"NOTA FINAL {grade:.1f} ({letter})",
                           SCREEN_W // 2, SCREEN_H // 2 + 40, (255, 255, 200), 3)
        draw_text_centered(scr, "ENTER PARA VOLTAR",
                           SCREEN_W // 2, SCREEN_H // 2 + 65, (200, 200, 200), 2)

    def _render_level_up(self, game):
        scr = self.screen
        choices = game.power_choices
        sel = game.power_selection
        n = len(choices)

        box_w, box_h = 340, 50 + n * 50
        bx = SCREEN_W // 2 - box_w // 2
        by = SCREEN_H // 2 - box_h // 2

        # Fundo
        fill_rect(scr, bx, by, box_w, box_h, (10, 10, 30))
        draw_rect(scr, bx, by, box_w, box_h, (100, 200, 255))
        draw_rect(scr, bx + 1, by + 1, box_w - 2, box_h - 2, (60, 120, 180))

        draw_text_centered(scr, "PERIODO AVANCADO", SCREEN_W // 2, by + 14,
                           (100, 200, 255), 3)
        draw_text_centered(scr, "ESCOLHA UM PODER", SCREEN_W // 2, by + 34,
                           (180, 180, 220), 1)

        for i, pid in enumerate(choices):
            pdef = POWER_DEFS[pid]
            cur_lvl = game.powers.get_level(pid)
            next_lvl = cur_lvl + 1
            cy = by + 55 + i * 50

            is_sel = (i == sel)
            # Destaque na opção selecionada
            if is_sel:
                fill_rect(scr, bx + 4, cy - 8, box_w - 8, 40, (30, 30, 60))
                draw_rect(scr, bx + 4, cy - 8, box_w - 8, 40, (255, 255, 100))

            # Ícone (círculo com letra)
            icon_x = bx + 24
            icon_y = cy + 10
            draw_filled_circle(scr, icon_x, icon_y, 10, pdef["color"])
            draw_text_centered(scr, pdef["icon"], icon_x, icon_y, (255, 255, 255), 2)

            # Nome
            name_color = (255, 255, 100) if is_sel else (220, 220, 220)
            draw_text(scr, pdef["name"], bx + 40, cy - 2, name_color, 2)

            # Nível: barras
            for lvl_i in range(pdef["max_level"]):
                lx = bx + 40 + lvl_i * 12
                ly = cy + 16
                if lvl_i < cur_lvl:
                    fill_rect(scr, lx, ly, 8, 6, pdef["color"])
                elif lvl_i == cur_lvl:
                    fill_rect(scr, lx, ly, 8, 6, (255, 255, 100))
                draw_rect(scr, lx, ly, 8, 6, (120, 120, 120))

            # Descrição do próximo nível
            if next_lvl <= pdef["max_level"]:
                desc = pdef["desc"][next_lvl - 1]
            else:
                desc = "MAX"
            desc_color = (180, 220, 100) if is_sel else (140, 140, 140)
            draw_text(scr, desc, bx + 40 + pdef["max_level"] * 12 + 8, cy + 16,
                      desc_color, 1)
