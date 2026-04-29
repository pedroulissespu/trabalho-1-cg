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
    SCREEN_W, SCREEN_H,
    PLAY_X, PLAY_Y, PLAY_W, PLAY_H,
    HUD_X, HUD_W,
    PLAYER_SHAPE, PLAYER_LEGS, PLAYER_BACKPACK,
    BOSS_SHAPE, PROJ_SHAPE,
)
from .state import GameState
from .assets import Assets


class Renderer:
    def __init__(self, screen):
        self.screen = screen

    def render(self, game):
        self.screen.fill((20, 10, 30))

        if game.state == GameState.TITLE:
            self._render_title(game)
        elif game.state in (GameState.PLAYING, GameState.PAUSED):
            self._render_game(game)
            if game.state == GameState.PAUSED:
                self._render_pause()
        elif game.state == GameState.GAME_OVER:
            self._render_game(game)
            self._render_game_over(game)
        elif game.state == GameState.VICTORY:
            self._render_game(game)
            self._render_victory(game)

    def _render_title(self, game):
        scr = self.screen
        anim = game.title_anim

        scr.fill((15, 10, 25))

        # Quadro verde (lousa)
        grad_pts = [(40, 40), (SCREEN_W - 40, 40), (SCREEN_W - 40, 320), (40, 320)]
        grad_colors = [(20, 60, 30), (30, 80, 40), (25, 70, 35), (15, 50, 25)]
        scanline_fill_gradient(scr, grad_pts, grad_colors)
        for i in range(4):
            draw_rect(scr, 38 + i, 38 + i, SCREEN_W - 78 - 2 * i, 284 - 2 * i,
                      (120 + i * 20, 80 + i * 10, 30))

        # Título
        bob = int(math.sin(anim * 2) * 4)
        draw_text_centered(scr, "SOBREVIVA AO SEMESTRE", SCREEN_W // 2, 65 + bob,
                           (255, 255, 220), 4)

        # === ALUNO (esquerda) vs NEGRESCO (direita) ===
        left_cx = SCREEN_W // 4
        right_cx = SCREEN_W * 3 // 4
        vs_y = 200

        # --- Aluno (esquerda) ---
        # Pernas animadas
        walk = math.sin(anim * 3) * 3
        for i, leg in enumerate(PLAYER_LEGS):
            leg_off = walk if i == 0 else -walk
            offset_leg = [(lx, ly + leg_off) for lx, ly in leg]
            m = identity()
            m = mat_mult(scale(3, 3), m)
            leg_pts = apply_transform(m, offset_leg)
            leg_pts = [(px + left_cx, py + vs_y) for px, py in leg_pts]
            if len(leg_pts) >= 3:
                scanline_fill(scr, leg_pts, (40, 40, 100))
                draw_polygon(scr, leg_pts, (60, 60, 140))

        # Mochila
        m = identity()
        m = mat_mult(scale(3, 3), m)
        bp_pts = apply_transform(m, PLAYER_BACKPACK)
        bp_pts = [(px + left_cx, py + vs_y) for px, py in bp_pts]
        if len(bp_pts) >= 3:
            scanline_fill(scr, bp_pts, (60, 40, 20))
            draw_polygon(scr, bp_pts, (90, 60, 30))

        # Corpo
        body_pts = apply_transform(m, PLAYER_SHAPE)
        body_pts = [(px + left_cx, py + vs_y) for px, py in body_pts]
        if len(body_pts) >= 3:
            body_colors = [(40, 100, 200), (60, 130, 220),
                           (50, 120, 210), (40, 100, 200)]
            scanline_fill_gradient(scr, body_pts, body_colors)
            draw_polygon(scr, body_pts, (80, 160, 255))

        # Cabeça
        draw_filled_circle(scr, left_cx, vs_y - 15, 10, (220, 180, 140))
        draw_circle(scr, left_cx, vs_y - 15, 10, (180, 140, 100))

        # Capelo
        draw_line(scr, left_cx - 14, vs_y - 24, left_cx + 14, vs_y - 24, (255, 220, 50))
        draw_line(scr, left_cx - 14, vs_y - 24, left_cx, vs_y - 32, (255, 220, 50))
        draw_line(scr, left_cx + 14, vs_y - 24, left_cx, vs_y - 32, (255, 220, 50))

        # Raios ao redor do aluno
        for i in range(8):
            a = anim * 1.5 + i * math.pi / 4
            r1, r2 = 40, 55
            x1 = left_cx + int(math.cos(a) * r1)
            y1 = vs_y + int(math.sin(a) * r1)
            x2 = left_cx + int(math.cos(a) * r2)
            y2 = vs_y + int(math.sin(a) * r2)
            bright = int(180 + 75 * math.sin(anim * 2 + i))
            draw_line(scr, x1, y1, x2, y2, (bright, bright, 100))

        draw_text_centered(scr, "ALUNO", left_cx, vs_y + 60, (100, 180, 255), 2)

        # --- VS (centro) ---
        vs_pulse = 3 + int(math.sin(anim * 3) * 2)
        draw_text_centered(scr, "VS", SCREEN_W // 2, vs_y - 5, (255, 80, 50), vs_pulse)

        # Elipses decorativas ao redor do VS
        for i in range(2):
            rx = int(30 + 10 * math.sin(anim * 2 + i * math.pi))
            ry = int(15 + 5 * math.cos(anim * 2 + i * math.pi))
            draw_ellipse(scr, SCREEN_W // 2, vs_y + 15 + i * 20, rx, ry, (140, 60, 40))

        # --- Boss Negresco (direita) ---
        boss_rot = anim * 0.5
        boss_sc = 2.0 + 0.2 * math.sin(anim * 1.5)
        m = identity()
        m = mat_mult(rotation(boss_rot), m)
        m = mat_mult(scale(boss_sc, boss_sc), m)
        boss_pts = apply_transform(m, BOSS_SHAPE)
        boss_pts = [(px + right_cx, py + vs_y) for px, py in boss_pts]

        if Assets.boss_sprite:
            tex_coords = []
            for px, py in BOSS_SHAPE:
                u = (px + 32) / 64
                v = (py + 32) / 64
                tex_coords.append((max(0, min(1, u)), max(0, min(1, v))))
            scanline_fill_texture(scr, boss_pts, tex_coords,
                                  Assets.boss_sprite, Assets.boss_sprite_w, Assets.boss_sprite_h)
            draw_polygon(scr, boss_pts, (180, 120, 60))
        else:
            boss_colors = []
            for i in range(len(boss_pts)):
                shade = 40 + (i * 15) % 60
                boss_colors.append((shade + 30, shade, max(0, shade - 10)))
            scanline_fill_gradient(scr, boss_pts, boss_colors)
            draw_polygon(scr, boss_pts, (150, 100, 40))

        draw_text_centered(scr, "NEGRESCO", right_cx, vs_y + 60, (255, 200, 100), 2)

        # Subtítulo
        draw_text_centered(scr, "DERROTE O PROF NEGRESCO", SCREEN_W // 2, 300,
                           (200, 200, 150), 2)

        # Menu
        items = ["JOGAR", "SAIR"]
        for idx, item in enumerate(items):
            cy = 370 + idx * 35
            color = (255, 255, 0) if idx == game.menu_selection else (180, 180, 180)
            if idx == game.menu_selection:
                draw_text_centered(scr, "> " + item + " <", SCREEN_W // 2, cy, color, 3)
            else:
                draw_text_centered(scr, item, SCREEN_W // 2, cy, color, 3)

        # Círculos decorativos embaixo
        for i in range(5):
            cx = 120 + i * 140
            cy = 450
            r = int(10 + 4 * math.sin(anim + i))
            cval = int(150 + 60 * math.sin(anim + i * 0.7))
            draw_circle(scr, cx, cy, r, (cval, 50, 50))

        draw_text_centered(scr, "WASD MOVER  SHIFT FOCO  ESC PAUSAR",
                           SCREEN_W // 2, 480, (100, 100, 100), 2)

    def _render_game(self, game):
        scr = self.screen

        # Fundo da área de jogo
        fill_rect(scr, PLAY_X, PLAY_Y, PLAY_W, PLAY_H, (10, 15, 30))

        # Calcular janela (mundo) e viewport (tela) — Requisito f)
        # A janela segue o jogador (translação) e tem zoom (escala)
        half_w = (PLAY_W / game.zoom) / 2
        half_h = (PLAY_H / game.zoom) / 2
        wx_min = game.cam_x - half_w
        wy_min = game.cam_y - half_h
        wx_max = game.cam_x + half_w
        wy_max = game.cam_y + half_h
        world_window = (wx_min, wy_min, wx_max, wy_max)
        # viewport com Y trocado para não inverter (mundo já usa Y pra baixo)
        vp = (PLAY_X, PLAY_Y + PLAY_H, PLAY_X + PLAY_W, PLAY_Y)
        vp_mat = window_to_viewport(world_window, vp)
        clip = (PLAY_X, PLAY_Y, PLAY_X + PLAY_W - 1, PLAY_Y + PLAY_H - 1)

        # Grid sutil com Cohen-Sutherland clipping
        grid_size = 40
        for gx in range(0, PLAY_W + 1, grid_size):
            sx0, sy0 = transform_point(vp_mat, gx, 0)
            sx1, sy1 = transform_point(vp_mat, gx, PLAY_H)
            draw_line_clipped(scr, int(sx0), int(sy0), int(sx1), int(sy1),
                              (20, 25, 45), *clip)
        for gy in range(0, PLAY_H + 1, grid_size):
            sx0, sy0 = transform_point(vp_mat, 0, gy)
            sx1, sy1 = transform_point(vp_mat, PLAY_W, gy)
            draw_line_clipped(scr, int(sx0), int(sy0), int(sx1), int(sy1),
                              (20, 25, 45), *clip)

        # Borda do mundo (visível quando com zoom)
        world_corners = [(0, 0), (PLAY_W, 0), (PLAY_W, PLAY_H), (0, PLAY_H)]
        world_screen = [transform_point(vp_mat, px, py) for px, py in world_corners]
        draw_polygon_clipped(scr, world_screen, (60, 60, 100), clip)

        # Borda da área de jogo
        draw_rect(scr, PLAY_X - 1, PLAY_Y - 1, PLAY_W + 2, PLAY_H + 2, (100, 100, 150))
        draw_rect(scr, PLAY_X - 2, PLAY_Y - 2, PLAY_W + 4, PLAY_H + 4, (60, 60, 100))

        # Boss
        bx, by = transform_point(vp_mat, game.boss.x, game.boss.y)
        self._render_boss(game.boss, int(bx), int(by), vp_mat, game.zoom)

        # Projéteis do boss
        for bp in game.boss_projectiles:
            sx, sy = transform_point(vp_mat, bp.x, bp.y)
            sx, sy = int(sx), int(sy)
            if clip[0] <= sx <= clip[2] and clip[1] <= sy <= clip[3]:
                r = max(2, int(4 * game.zoom))
                draw_filled_circle(scr, sx, sy, r, (255, 60, 60))
                draw_circle(scr, sx, sy, r, (255, 200, 100))

        # Projéteis do jogador
        for p in game.projectiles:
            sx, sy = transform_point(vp_mat, p.x, p.y)
            sx, sy = int(sx), int(sy)
            if clip[0] <= sx <= clip[2] and clip[1] <= sy <= clip[3]:
                pts = self._transform_shape_vp(PROJ_SHAPE, p.x, p.y, p.angle, vp_mat, game.zoom)
                if Assets.lapis_sprite:
                    tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
                    scanline_fill_texture_alpha(scr, pts, tex_coords,
                                               Assets.lapis_sprite,
                                               Assets.lapis_sprite_w,
                                               Assets.lapis_sprite_h)
                else:
                    scanline_fill(scr, pts, (180, 120, 50))
                    draw_polygon(scr, pts, (220, 170, 80))

        # Jogador (estudante)
        blink = game.player.invincible > 0 and (game.frame % 4 < 2)
        if not blink:
            px = game.player.x
            py = game.player.y
            ang = game.player.angle

            walk_offset = math.sin(game.frame * 0.3) * 2

            # Mochila
            bp_pts = self._transform_shape_vp(PLAYER_BACKPACK, px, py, ang, vp_mat, game.zoom)
            if len(bp_pts) >= 3:
                scanline_fill(scr, bp_pts, (60, 40, 20))
                draw_polygon(scr, bp_pts, (90, 60, 30))

            # Pernas
            for i, leg in enumerate(PLAYER_LEGS):
                leg_off = walk_offset if i == 0 else -walk_offset
                offset_leg = [(lx, ly + leg_off) for lx, ly in leg]
                leg_pts = self._transform_shape_vp(offset_leg, px, py, ang, vp_mat, game.zoom)
                if len(leg_pts) >= 3:
                    scanline_fill(scr, leg_pts, (40, 40, 100))
                    draw_polygon(scr, leg_pts, (60, 60, 140))

            # Corpo
            body_pts = self._transform_shape_vp(PLAYER_SHAPE, px, py, ang, vp_mat, game.zoom)
            if len(body_pts) >= 3:
                body_colors = [(40, 100, 200), (60, 130, 220),
                               (50, 120, 210), (40, 100, 200)]
                scanline_fill_gradient(scr, body_pts, body_colors)
                draw_polygon(scr, body_pts, (80, 160, 255))

            # Cabeça
            head_x, head_y = transform_point(vp_mat, px, py - 12)
            hr = max(3, int(5 * game.zoom))
            draw_filled_circle(scr, int(head_x), int(head_y), hr, (220, 180, 140))
            draw_circle(scr, int(head_x), int(head_y), hr, (180, 140, 100))

            # Hitbox visível no foco (Shift)
            if game.player.focused:
                cx, cy = transform_point(vp_mat, px, py)
                draw_filled_circle(scr, int(cx), int(cy), max(2, int(3 * game.zoom)), (255, 255, 255))
                draw_circle(scr, int(cx), int(cy), max(4, int(6 * game.zoom)), (255, 100, 100))

        # Indicador de zoom
        if abs(game.zoom - 1.0) > 0.05:
            draw_text(scr, f"ZOOM {game.zoom:.1f}X", PLAY_X + 5, PLAY_Y + 5, (200, 200, 100), 1)

        # HUD (painel direito)
        self._render_hud(game)

    def _render_boss(self, boss, sx, sy, vp_mat, zoom):
        scr = self.screen
        boss_sc = 1.5
        if Assets.boss_sprite:
            pts = self._transform_shape_vp(BOSS_SHAPE, boss.x, boss.y,
                                            boss.anim_timer * 0.3, vp_mat, zoom, boss_sc)
            tex_coords = []
            for px, py in BOSS_SHAPE:
                u = (px + 32) / 64
                v = (py + 32) / 64
                tex_coords.append((max(0, min(1, u)), max(0, min(1, v))))
            scanline_fill_texture(scr, pts, tex_coords,
                                  Assets.boss_sprite, Assets.boss_sprite_w, Assets.boss_sprite_h)
            draw_polygon(scr, pts, (180, 120, 60))
        else:
            pts = self._transform_shape_vp(BOSS_SHAPE, boss.x, boss.y,
                                            boss.anim_timer * 0.3, vp_mat, zoom, boss_sc)
            boss_colors = []
            for i in range(len(pts)):
                shade = 40 + (i * 15) % 60
                boss_colors.append((shade + 30, shade, max(0, shade - 10)))
            scanline_fill_gradient(scr, pts, boss_colors)
            draw_polygon(scr, pts, (150, 100, 40))

        draw_text_centered(scr, "NEGRESCO", sx, sy - int(40 * zoom), (255, 200, 100), 2)

    def _transform_shape_vp(self, shape, wx, wy, angle, vp_mat, zoom, extra_scale=1.0):
        """Transforma shape: rotação+escala local, depois world→viewport."""
        m = identity()
        m = mat_mult(rotation(angle), m)
        m = mat_mult(scale(extra_scale * zoom, extra_scale * zoom), m)
        pts = apply_transform(m, shape)
        # Converte centro do mundo para viewport, depois desloca os pontos locais
        cx, cy = transform_point(vp_mat, wx, wy)
        return [(px + cx, py + cy) for px, py in pts]

    def _render_hud(self, game):
        scr = self.screen
        p = game.player
        boss = game.boss
        hx = HUD_X
        hw = HUD_W

        # Painel de fundo
        fill_rect(scr, hx - 5, 15, hw + 10, SCREEN_H - 30, (15, 10, 25))
        draw_rect(scr, hx - 5, 15, hw + 10, SCREEN_H - 30, (80, 60, 120))

        y = 30

        # Título
        draw_text_centered(scr, "PROF NEGRESCO", hx + hw // 2, y, (255, 200, 100), 2)
        y += 20

        # Barra de HP do boss
        bar_w = hw - 20
        fill_rect(scr, hx + 10, y, bar_w, 12, (40, 20, 20))
        boss_ratio = max(0, boss.hp / boss.max_hp)
        fill_rect(scr, hx + 11, y + 1, int((bar_w - 2) * boss_ratio), 10, (220, 50, 50))
        draw_rect(scr, hx + 10, y, bar_w, 12, (200, 150, 100))
        draw_text_centered(scr, f"{boss.hp}/{boss.max_hp}", hx + hw // 2, y + 2,
                           (255, 255, 255), 1)
        y += 25

        # Separador
        draw_line(scr, hx + 5, y, hx + hw - 5, y, (80, 60, 120))
        y += 15

        # Info do aluno
        draw_text(scr, "ALUNO", hx + 10, y, (100, 180, 255), 2)
        y += 20

        # Barra de HP do player
        fill_rect(scr, hx + 10, y, bar_w, 12, (20, 40, 20))
        hp_ratio = max(0, p.hp / p.max_hp)
        hp_color = (50, 220, 50) if hp_ratio > 0.5 else (220, 220, 50) if hp_ratio > 0.25 else (220, 50, 50)
        fill_rect(scr, hx + 11, y + 1, int((bar_w - 2) * hp_ratio), 10, hp_color)
        draw_rect(scr, hx + 10, y, bar_w, 12, (150, 200, 150))
        draw_text_centered(scr, f"{p.hp}/{p.max_hp}", hx + hw // 2, y + 2,
                           (255, 255, 255), 1)
        y += 25

        # Stats
        draw_text(scr, f"DANO: {p.damage}", hx + 10, y, (200, 200, 200), 1)
        y += 12
        draw_text(scr, f"REGEN: {p.regen_rate:.1f}/S", hx + 10, y, (200, 200, 200), 1)
        y += 12
        draw_text(scr, f"PROJ: 5 LAPIS", hx + 10, y, (200, 200, 200), 1)
        y += 20

        # Separador
        draw_line(scr, hx + 5, y, hx + hw - 5, y, (80, 60, 120))
        y += 15

        # Timer
        secs = game.fight_timer // 60
        mins = secs // 60
        secs = secs % 60
        draw_text(scr, f"TEMPO: {mins}:{secs:02d}", hx + 10, y, (255, 255, 200), 2)
        y += 25

        # Controles
        draw_line(scr, hx + 5, y, hx + hw - 5, y, (80, 60, 120))
        y += 15
        draw_text(scr, "CONTROLES", hx + 10, y, (150, 150, 200), 2)
        y += 18
        controls = [
            "WASD - MOVER",
            "SHIFT - FOCO",
            "ESC - PAUSAR",
            "",
            "FOCO = HITBOX",
            "MENOR + LENTO",
        ]
        for line in controls:
            draw_text(scr, line, hx + 10, y, (120, 120, 160), 1)
            y += 10

        # Minimap (usa window_to_viewport)
        self._render_minimap(game, hx+45, hw-100, y)

    def _render_minimap(self, game, hx, hw, y_start):
        scr = self.screen
        y_start += 10

        draw_text(scr, "MINIMAP", hx + 10, y_start, (150, 150, 200), 2)
        y_start += 18

        # Viewport do minimap no HUD
        mm_w = hw - 20
        mm_h = int(mm_w * (PLAY_H / PLAY_W))
        mm_x = hx + 10
        mm_y = y_start

        # Fundo do minimap
        fill_rect(scr, mm_x, mm_y, mm_w, mm_h, (10, 15, 30))
        draw_rect(scr, mm_x, mm_y, mm_w, mm_h, (80, 80, 120))

        # Transformação janela (área de jogo) → viewport (minimap)
        window = (0, 0, PLAY_W, PLAY_H)
        viewport = (mm_x, mm_y + mm_h, mm_x + mm_w, mm_y)
        m = window_to_viewport(window, viewport)
        clip = (mm_x, mm_y, mm_x + mm_w - 1, mm_y + mm_h - 1)

        # Borda da área de jogo no minimap (Cohen-Sutherland)
        play_corners = [(0, 0), (PLAY_W, 0), (PLAY_W, PLAY_H), (0, PLAY_H)]
        play_screen = [transform_point(m, px, py) for px, py in play_corners]
        draw_polygon_clipped(scr, play_screen, (60, 60, 100), clip)

        # Projéteis do boss (set_pixel)
        for bp in game.boss_projectiles:
            bpx, bpy = transform_point(m, bp.x, bp.y)
            bpx, bpy = int(bpx), int(bpy)
            if mm_x <= bpx < mm_x + mm_w and mm_y <= bpy < mm_y + mm_h:
                set_pixel(scr, bpx, bpy, (255, 80, 80))

        # Projéteis do player (set_pixel)
        for p in game.projectiles:
            ppx, ppy = transform_point(m, p.x, p.y)
            ppx, ppy = int(ppx), int(ppy)
            if mm_x <= ppx < mm_x + mm_w and mm_y <= ppy < mm_y + mm_h:
                set_pixel(scr, ppx, ppy, (100, 200, 255))

        # Boss (circle)
        bsx, bsy = transform_point(m, game.boss.x, game.boss.y)
        draw_filled_circle(scr, int(bsx), int(bsy), 4, (200, 100, 40))
        draw_circle(scr, int(bsx), int(bsy), 4, (255, 180, 80))

        # Player (circle)
        psx, psy = transform_point(m, game.player.x, game.player.y)
        draw_filled_circle(scr, int(psx), int(psy), 3, (50, 150, 255))
        draw_circle(scr, int(psx), int(psy), 3, (100, 200, 255))

        # Retângulo da câmera/janela atual (Cohen-Sutherland clipping)
        half_w = (PLAY_W / game.zoom) / 2
        half_h = (PLAY_H / game.zoom) / 2
        cam_corners = [
            (game.cam_x - half_w, game.cam_y - half_h),
            (game.cam_x + half_w, game.cam_y - half_h),
            (game.cam_x + half_w, game.cam_y + half_h),
            (game.cam_x - half_w, game.cam_y + half_h),
        ]
        cam_screen = [transform_point(m, cx, cy) for cx, cy in cam_corners]
        draw_polygon_clipped(scr, cam_screen, (255, 255, 0), clip)

        y_after = mm_y + mm_h + 10

        # Textura decorativa no HUD (se existir)
        if Assets.ground_tex:
            tex_x, tex_y = hx + 10, y_after
            tex_s = min(hw - 20, 80)
            if tex_y + tex_s < SCREEN_H - 25:
                pts = [(tex_x, tex_y), (tex_x + tex_s, tex_y),
                       (tex_x + tex_s, tex_y + tex_s), (tex_x, tex_y + tex_s)]
                tex_coords = [(0, 0), (1, 0), (1, 1), (0, 1)]
                scanline_fill_texture(scr, pts, tex_coords,
                                      Assets.ground_tex, Assets.ground_tex_w, Assets.ground_tex_h)

    def _render_pause(self):
        scr = self.screen
        fill_rect(scr, PLAY_X + PLAY_W // 2 - 120, PLAY_Y + PLAY_H // 2 - 40, 240, 80, (0, 0, 0))
        draw_rect(scr, PLAY_X + PLAY_W // 2 - 120, PLAY_Y + PLAY_H // 2 - 40, 240, 80, (200, 200, 0))
        draw_text_centered(scr, "PAUSADO", PLAY_X + PLAY_W // 2, PLAY_Y + PLAY_H // 2 - 15,
                           (255, 255, 0), 4)
        draw_text_centered(scr, "ESC PARA CONTINUAR", PLAY_X + PLAY_W // 2, PLAY_Y + PLAY_H // 2 + 20,
                           (200, 200, 200), 2)

    def _render_game_over(self, game):
        scr = self.screen
        cx = PLAY_X + PLAY_W // 2
        cy = PLAY_Y + PLAY_H // 2
        fill_rect(scr, cx - 150, cy - 60, 300, 120, (30, 0, 0))
        draw_rect(scr, cx - 150, cy - 60, 300, 120, (255, 50, 50))
        draw_text_centered(scr, "REPROVADO", cx, cy - 35, (255, 50, 50), 5)
        draw_text_centered(scr, "O NEGRESCO TE VENCEU", cx, cy, (255, 180, 180), 2)

        secs = game.fight_timer // 60
        mins = secs // 60
        secs = secs % 60
        draw_text_centered(scr, f"TEMPO: {mins}:{secs:02d}", cx, cy + 20, (255, 255, 200), 2)
        draw_text_centered(scr, "ENTER PARA TENTAR DE NOVO", cx, cy + 42, (200, 200, 200), 2)

    def _render_victory(self, game):
        scr = self.screen
        cx = PLAY_X + PLAY_W // 2
        cy = PLAY_Y + PLAY_H // 2
        fill_rect(scr, cx - 160, cy - 70, 320, 140, (0, 20, 0))
        draw_rect(scr, cx - 160, cy - 70, 320, 140, (50, 255, 50))
        draw_text_centered(scr, "APROVADO", cx, cy - 45, (50, 255, 50), 5)
        draw_text_centered(scr, "PROF NEGRESCO DERROTADO", cx, cy - 5, (200, 255, 200), 2)

        secs = game.fight_timer // 60
        mins = secs // 60
        secs = secs % 60
        draw_text_centered(scr, f"TEMPO: {mins}:{secs:02d}", cx, cy + 20, (255, 255, 200), 2)
        draw_text_centered(scr, "ENTER PARA VOLTAR", cx, cy + 45, (200, 200, 200), 2)
