"""Main game class — owns the loop, states, and all gameplay systems."""

import pygame

from config.settings import (
    BOARD_ORIGIN_X,
    BOARD_ORIGIN_Y,
    BOARD_PIXEL_HEIGHT,
    BOARD_PIXEL_WIDTH,
    FPS,
    LINE_CLEAR_FLASH,
    LOCK_DELAY,
    MAX_DT,
    NEXT_QUEUE_COUNT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from src.core.board import Board
from src.core.game_state import PAUSABLE_STATES, GameState
from src.systems.assets import AssetManager
from src.core.tetromino import Tetromino
from src.systems.audio import AudioManager
from src.systems.bag import Bag
from src.systems.high_scores import HighScores
from src.systems.input import Action, InputHandler
from src.systems.scoring import Scoring
from src.systems.platform import is_android, is_mobile
from src.systems.settings_store import SettingsStore
from src.systems.touch_input import TouchRepeat
from src.ui.animations import (
    AnimatedCounter,
    PieceAnimator,
    RowFallAnimator,
    ScorePopupManager,
    ScreenFader,
)
import src.ui.colors as colors
from src.ui.colors import current_theme
from src.ui.effects import BackgroundAnimator, NotificationBanner, ParticleSystem, ScreenShake
from src.ui.coords import DisplayMapper
from src.ui.hud import HUD
from src.ui.menu_screen import MainMenuScreen
from src.ui.menus import OptionsMenu, PauseMenu
from src.ui.renderer import Renderer
from src.ui.themes import get_theme
from src.utils.easing import clamp_dt

WALL_KICKS: list[tuple[int, int]] = [
    (0, 0), (-1, 0), (1, 0), (0, -1), (-2, 0), (2, 0), (0, -2),
]

BOARD_CENTER = (
    BOARD_ORIGIN_X + BOARD_PIXEL_WIDTH // 2,
    BOARD_ORIGIN_Y + BOARD_PIXEL_HEIGHT // 2,
)


class Game:
    """Orchestrates the Pygame window, update logic, and rendering."""

    def __init__(self) -> None:
        pygame.init()
        self.settings = SettingsStore()
        self.virtual = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self._create_display()
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.running = True

        self.renderer = Renderer(self.virtual)
        self.hud = HUD(self.virtual)
        self.audio = AudioManager()
        self.audio.apply_settings(
            self.settings.music_volume,
            self.settings.sfx_volume,
            self.settings.music_enabled,
            self.settings.music_track,
        )
        self.assets = AssetManager()
        self.display_mapper = DisplayMapper()
        self.mouse_pos = (0, 0)
        self.main_menu = MainMenuScreen()
        self.main_menu.sync_theme_selection(self.settings)
        self.pause_menu = PauseMenu()
        self.options_menu = OptionsMenu()
        self.options_menu.sync_from_settings(self.settings)
        self._state_before_pause = GameState.PLAYING
        self._options_return_state = GameState.MENU
        self.high_scores = HighScores()
        self.particles = ParticleSystem()
        self.shake = ScreenShake()
        self.shake_offset = (0, 0)
        self.banner = NotificationBanner()
        self.background = BackgroundAnimator()
        self.piece_anim = PieceAnimator()
        self.row_fall = RowFallAnimator()
        self.score_popups = ScorePopupManager()
        self.score_counter = AnimatedCounter()
        self.fader = ScreenFader()
        self.theme_toast_timer = 0.0
        self.theme_toast_label = current_theme().label
        self._flash_finished = False
        self.touch_repeat = TouchRepeat()
        self._app_paused = False

        self.state = GameState.MENU
        self._last_fullscreen = self.settings.fullscreen
        self._last_display_scale = self.settings.display_scale
        self._reset_session_state()
        if self.settings.music_enabled:
            self.audio.start_music()
        if is_mobile():
            pygame.mouse.set_visible(False)

    def _create_display(self) -> None:
        if is_android():
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h),
                pygame.FULLSCREEN,
            )
            return
        flags = pygame.SCALED
        if self.settings.fullscreen:
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode((info.current_w, info.current_h), flags | pygame.FULLSCREEN)
        else:
            w = max(WINDOW_WIDTH, int(WINDOW_WIDTH * self.settings.display_scale))
            h = max(WINDOW_HEIGHT, int(WINDOW_HEIGHT * self.settings.display_scale))
            self.screen = pygame.display.set_mode((w, h), flags)

    def _toggle_fullscreen(self) -> None:
        self.settings.toggle_fullscreen()
        self._create_display()

    def _cycle_theme(self) -> None:
        name = self.settings.cycle_theme()
        self._on_theme_changed(name)

    def _on_theme_changed(self, name: str) -> None:
        theme = get_theme(name)
        self.theme_toast_label = theme.label
        self.theme_toast_timer = 1.5
        self.renderer.invalidate_cache()
        self.background.invalidate()
        self.main_menu.invalidate()
        self.banner.show(f"Theme: {theme.label}", duration=1.0)

    def _sync_audio_settings(self) -> None:
        self.audio.apply_settings(
            self.settings.music_volume,
            self.settings.sfx_volume,
            self.settings.music_enabled,
            self.settings.music_track,
        )

    def _pause_game(self) -> None:
        if self.state not in PAUSABLE_STATES:
            return
        self._state_before_pause = self.state
        self.state = GameState.PAUSED
        self.audio.play("menu")

    def _resume_game(self) -> None:
        self.state = self._state_before_pause if self._state_before_pause else GameState.PLAYING

    def _open_options(self, return_state: GameState) -> None:
        self._options_return_state = return_state
        self.options_menu.sync_from_settings(self.settings)
        self.state = GameState.OPTIONS
        self.audio.play("menu")

    def _close_options(self) -> None:
        self._sync_audio_settings()
        if (
            self.settings.fullscreen != self._last_fullscreen
            or self.settings.display_scale != self._last_display_scale
        ):
            self._create_display()
        self._last_fullscreen = self.settings.fullscreen
        self._last_display_scale = self.settings.display_scale
        self.renderer.invalidate_cache()
        self.background.invalidate()
        self.state = self._options_return_state

    def _on_options_changed(self) -> None:
        self._sync_audio_settings()
        theme = get_theme(self.settings.theme)
        self.theme_toast_label = theme.label
        self.renderer.invalidate_cache()
        self.background.invalidate()
        self.main_menu.invalidate()

    def _handle_android_back(self) -> bool:
        """System back: step out of overlays, pause in-game, or quit from menu."""
        if self.state == GameState.OPTIONS:
            self._close_options()
            return True
        if self.state == GameState.PAUSED:
            self._resume_game()
            return True
        if self.state == GameState.GAME_OVER:
            self.state = GameState.MENU
            return True
        if self.state in PAUSABLE_STATES:
            self._pause_game()
            return True
        if self.state == GameState.MENU:
            self.running = False
            self.settings.save()
            return True
        return False

    def _handle_global_key(self, event: pygame.event.Event) -> bool:
        if is_android():
            return False
        if event.key == pygame.K_F11:
            self._toggle_fullscreen()
            return True
        if event.key == pygame.K_F8:
            self.settings.toggle_music()
            self.audio.apply_settings(
                self.settings.music_volume,
                self.settings.sfx_volume,
                self.settings.music_enabled,
            )
            label = "Music ON" if self.settings.music_enabled else "Music OFF"
            self.banner.show(label, duration=0.9)
            return True
        if event.key == pygame.K_v:
            self._cycle_theme()
            return True
        if event.key == pygame.K_LEFTBRACKET:
            self.settings.adjust_music_volume(-0.1)
            self.audio.set_music_volume(self.settings.music_volume)
            return True
        if event.key == pygame.K_RIGHTBRACKET:
            self.settings.adjust_music_volume(0.1)
            self.audio.set_music_volume(self.settings.music_volume)
            return True
        return False

    def _reset_session_state(self) -> None:
        self.board = Board()
        self.bag = Bag()
        self.scoring = Scoring()
        self.input = InputHandler()
        self.active_piece = Tetromino.spawn(self.bag.next())
        self.next_piece_kind = self.bag.next()
        self.hold_kind: str | None = None
        self.can_hold = True
        self.ghost_piece = self.board.compute_ghost(self.active_piece)
        self.flashing_rows: list[int] = []
        self.clear_anim_timer = 0.0
        self._flash_finished = False
        self.drop_timer = 0.0
        self.lock_timer = 0.0
        self.is_new_high_score = False
        self.high_score_rank = 0
        self.particles.clear()
        self.shake = ScreenShake()
        self.piece_anim.reset()
        self.piece_anim.on_spawn()
        self.row_fall = RowFallAnimator()
        self.score_counter.set(0)
        self.score_counter.display = 0.0
        self.display_score = 0

    def _start_new_game(self) -> None:
        self.fader.fade_to(180, 0.15)
        self._reset_session_state()
        self.fader.fade_to(0, 0.25)

    def _virtual_mouse(self, screen_pos: tuple[int, int]) -> tuple[int, int]:
        return self.display_mapper.to_virtual(screen_pos)

    def _handle_menu_click(self, action: str | None) -> None:
        if action == "play":
            self._start_new_game()
            self.state = GameState.PLAYING
            self.audio.play("menu")
        elif action == "options":
            self._open_options(GameState.MENU)
        elif action == "theme":
            self._on_theme_changed(self.settings.theme)
            self.main_menu.sync_theme_selection(self.settings)
            self.main_menu.invalidate()

    def _handle_pause_click(self, action: str | None) -> None:
        if action == "resume":
            self._resume_game()
        elif action == "options":
            self._open_options(GameState.PAUSED)
        elif action == "menu":
            self.fader.fade_to(120, 0.2)
            self.state = GameState.MENU

    def _handle_options_result(self, result: str | None) -> None:
        if result == "back":
            self._close_options()
        elif result in ("changed", "scale"):
            self._on_options_changed()
            self.main_menu.sync_theme_selection(self.settings)
            if (
                self.settings.fullscreen != self._last_fullscreen
                or self.settings.display_scale != self._last_display_scale
            ):
                self._create_display()
                self._last_fullscreen = self.settings.fullscreen
                self._last_display_scale = self.settings.display_scale
            if result == "scale":
                self.banner.show(f"Window: {int(self.settings.display_scale * 100)}%", duration=0.9)

    def handle_events(self) -> None:
        back_key = getattr(pygame, "K_AC_BACK", 4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.settings.save()
                continue

            if event.type == pygame.APP_WILLENTERBACKGROUND:
                self._app_paused = True
                if self.state in PAUSABLE_STATES and self.state != GameState.PAUSED:
                    self._pause_game()
                self.audio.pause_music()
                continue

            if event.type == pygame.APP_DIDENTERFOREGROUND:
                self._app_paused = False
                if self.settings.music_enabled:
                    self.audio.unpause_music()
                continue

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = self._virtual_mouse(event.pos)
                continue

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                vm = self._virtual_mouse(event.pos)
                self.touch_repeat.release()
                if self.state == GameState.OPTIONS:
                    self._handle_options_result(self.options_menu.handle_release(self.settings))
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                vm = self._virtual_mouse(event.pos)
                self.mouse_pos = vm
                if self.state == GameState.MENU:
                    self._handle_menu_click(self.main_menu.handle_click(vm, self.settings))
                elif self.state == GameState.PAUSED:
                    self._handle_pause_click(self.pause_menu.handle_click(vm))
                elif self.state == GameState.OPTIONS:
                    self._handle_options_result(self.options_menu.handle_click(vm, self.settings))
                elif self.state == GameState.GAME_OVER:
                    action = self.hud.handle_click(vm, "game_over")
                    if action == "restart":
                        self._start_new_game()
                        self.state = GameState.PLAYING
                    elif action == "menu":
                        self.state = GameState.MENU
                elif self.state in PAUSABLE_STATES:
                    action = self.hud.handle_click(
                        vm, "playing", touch_enabled=self.settings.touch_controls
                    )
                    if action == "pause":
                        self._pause_game()
                    elif action and self.state == GameState.PLAYING:
                        if action in ("left", "right", "soft_drop"):
                            for touch_action in self.touch_repeat.press(action):
                                self._apply_touch_action(touch_action)
                        else:
                            self._apply_touch_action(action)
                    elif self.state == GameState.PLAYING:
                        board_action = self.hud.board_click_action(vm)
                        if board_action:
                            if board_action in ("left", "right", "soft_drop"):
                                for touch_action in self.touch_repeat.press(board_action):
                                    self._apply_touch_action(touch_action)
                            else:
                                self._apply_touch_action(board_action)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in (back_key, pygame.K_ESCAPE) and is_android():
                    if self._handle_android_back():
                        continue
                if self._handle_global_key(event):
                    continue

            if event.type != pygame.KEYDOWN:
                continue

            if self.state == GameState.MENU:
                if event.key == pygame.K_RETURN:
                    self._handle_menu_click("play")
                elif event.key == pygame.K_o:
                    self._open_options(GameState.MENU)
            elif self.state == GameState.PAUSED:
                self._handle_pause_click(self.pause_menu.handle_key(event.key))
            elif self.state == GameState.OPTIONS:
                self._handle_options_result(self.options_menu.handle_key(event.key, self.settings))
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_r:
                    self._start_new_game()
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_m:
                    self.state = GameState.MENU
            elif self.state in PAUSABLE_STATES:
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    self._pause_game()
                elif self.state == GameState.PLAYING:
                    for action in self.input.process_event(event):
                        self._apply_action(action)

    def update(self, dt: float) -> None:
        dt = clamp_dt(dt, MAX_DT)
        self.background.update(dt)
        ui_state = ""
        if self.state == GameState.PLAYING:
            ui_state = "playing"
        elif self.state == GameState.GAME_OVER:
            ui_state = "game_over"
        self.hud.update(
            dt,
            self.mouse_pos,
            ui_state=ui_state,
            touch_enabled=self.settings.touch_controls,
        )

        if self.state == GameState.MENU:
            self.main_menu.update(dt, self.mouse_pos)
        elif self.state == GameState.PAUSED:
            self.pause_menu.update(dt, self.mouse_pos)
        elif self.state == GameState.OPTIONS:
            self.options_menu.update(dt, self.mouse_pos)
            if self.options_menu._dragging_slider:
                slider = self.options_menu._dragging_slider
                if slider.action == "music_volume":
                    self.settings.music_volume = slider.value
                else:
                    self.settings.sfx_volume = slider.value
                self._sync_audio_settings()
        self.particles.update(dt)
        self.shake_offset = self.shake.update(dt)
        self.banner.update(dt)
        self.piece_anim.update(dt)
        self.row_fall.update(dt)
        self.score_popups.update(dt)
        self.fader.update(dt)
        self.score_counter.set(self.scoring.score)
        self.display_score = self.score_counter.update(dt)

        if self.theme_toast_timer > 0:
            self.theme_toast_timer -= dt

        if self.state == GameState.PLAYING and not self._app_paused:
            for touch_action in self.touch_repeat.poll(dt):
                self._apply_touch_action(touch_action)
            self._update_playing(dt)
        elif self.state == GameState.LINE_CLEAR:
            self._update_line_clear(dt)
        elif self.state == GameState.ROW_FALL:
            if not self.row_fall.active:
                self._spawn_next_piece()
                self.state = GameState.PLAYING

    def _update_playing(self, dt: float) -> None:
        for action in self.input.poll(dt):
            self._apply_action(action)

        if self._is_on_ground():
            self.lock_timer += dt
            if self.lock_timer >= LOCK_DELAY:
                self._lock_active_piece()
                return

        if not self.input.is_soft_dropping():
            self.drop_timer += dt
            if self.drop_timer >= self.scoring.drop_interval:
                self.drop_timer = 0.0
                if self._nudge_down():
                    self.piece_anim.on_step_down()

        self.ghost_piece = self.board.compute_ghost(self.active_piece)

    def _update_line_clear(self, dt: float) -> None:
        self.clear_anim_timer += dt
        if not self._flash_finished and self.clear_anim_timer >= LINE_CLEAR_FLASH:
            self._apply_line_clear()
            self._flash_finished = True

    def _apply_line_clear(self) -> None:
        cleared_rows = self.flashing_rows
        grid_snapshot = [row[:] for row in self.board.grid]
        cleared = self.board.clear_lines()
        old_level = self.scoring.level
        old_score = self.scoring.score
        self.scoring.add_lines(cleared)
        gained = self.scoring.score - old_score

        if gained > 0:
            self.score_popups.spawn(f"+{gained}", BOARD_CENTER[0], BOARD_CENTER[1] - 40, colors.TETRIS_GOLD)

        if cleared == 4:
            self.audio.play("tetris")
            self.banner.show("TETRIS!", duration=1.6, color=colors.TETRIS_GOLD)
        elif cleared > 0:
            self.audio.play("line_clear")
            labels = {1: "SINGLE!", 2: "DOUBLE!", 3: "TRIPLE!"}
            self.banner.show(labels.get(cleared, ""), duration=1.0)

        if self.scoring.level > old_level:
            self.audio.play("level_up")
            self.banner.show(f"LEVEL {self.scoring.level}", duration=1.2)
            self.hud.trigger_level_pulse()

        self.row_fall.start(cleared_rows, grid_snapshot)
        self.state = GameState.ROW_FALL if self.row_fall.active else GameState.PLAYING
        if not self.row_fall.active:
            self._spawn_next_piece()

    def _apply_touch_action(self, action: str) -> None:
        mapping = {
            "left": Action.MOVE_LEFT,
            "right": Action.MOVE_RIGHT,
            "rotate": Action.ROTATE_CW,
            "soft_drop": Action.MOVE_DOWN,
            "hard_drop": Action.HARD_DROP,
            "hold": Action.HOLD,
        }
        game_action = mapping.get(action)
        if game_action is not None:
            self._apply_action(game_action)

    def _apply_action(self, action: Action) -> None:
        moved = False

        if action == Action.MOVE_LEFT:
            moved = self._try_move(dx=-1)
            if moved:
                self.piece_anim.on_step_horizontal(-1)
        elif action == Action.MOVE_RIGHT:
            moved = self._try_move(dx=1)
            if moved:
                self.piece_anim.on_step_horizontal(1)
        elif action == Action.MOVE_DOWN:
            moved = self._nudge_down(fast=True)
            if moved:
                self.scoring.add_soft_drop()
                self.audio.play("soft_drop")
        elif action == Action.ROTATE_CW:
            moved = self._try_rotate(direction=1)
            if moved:
                self.piece_anim.on_rotate()
                self.audio.play("rotate")
        elif action == Action.ROTATE_CCW:
            moved = self._try_rotate(direction=-1)
            if moved:
                self.piece_anim.on_rotate()
                self.audio.play("rotate")
        elif action == Action.HARD_DROP:
            self._hard_drop()
            return
        elif action == Action.HOLD:
            self._try_hold()
            return

        if moved and action in (Action.MOVE_LEFT, Action.MOVE_RIGHT):
            self.audio.play("move")
        if moved:
            self._reset_lock_timer_if_grounded()

    def _try_move(self, dx: int = 0, dy: int = 0) -> bool:
        moved = self.active_piece.moved(dx=dx, dy=dy)
        if self.board.is_valid_position(moved):
            self.active_piece = moved
            return True
        return False

    def _try_rotate(self, direction: int) -> bool:
        rotated = self.active_piece.rotated(direction)
        for dx, dy in WALL_KICKS:
            candidate = rotated.moved(dx=dx, dy=dy)
            if self.board.is_valid_position(candidate):
                self.active_piece = candidate
                return True
        return False

    def _nudge_down(self, *, fast: bool = False) -> bool:
        moved = self.active_piece.moved(dy=1)
        if self.board.is_valid_position(moved):
            self.active_piece = moved
            self.piece_anim.on_step_down(fast=fast)
            return True
        return False

    def _is_on_ground(self) -> bool:
        return not self.board.is_valid_position(self.active_piece.moved(dy=1))

    def _reset_lock_timer_if_grounded(self) -> None:
        if self._is_on_ground():
            self.lock_timer = 0.0

    def _hard_drop(self) -> None:
        ghost = self.board.compute_ghost(self.active_piece)
        cells = ghost.y - self.active_piece.y
        self.scoring.add_hard_drop(cells)
        self.active_piece = ghost
        self.piece_anim.on_step_down(fast=True)
        self.piece_anim.on_lock()
        self.audio.play("hard_drop")
        if self.settings.particles_enabled:
            self.particles.spawn_from_cells(self.active_piece.cells, self.active_piece.kind, count=4)
        self.shake.trigger(4.0, 0.12)
        self._lock_active_piece()

    def _try_hold(self) -> None:
        if not self.can_hold:
            return

        self.can_hold = False
        self.lock_timer = 0.0

        if self.hold_kind is None:
            self.hold_kind = self.active_piece.kind
            self.active_piece = Tetromino.spawn(self.next_piece_kind)
            self.next_piece_kind = self.bag.next()
        else:
            swap_kind = self.hold_kind
            self.hold_kind = self.active_piece.kind
            self.active_piece = Tetromino.spawn(swap_kind)

        self.piece_anim.on_spawn()
        self.audio.play("hold")
        self.hud.trigger_hold_flash()

        if not self.board.is_valid_position(self.active_piece):
            self._enter_game_over()

    def _lock_active_piece(self) -> None:
        self.piece_anim.on_lock()
        self.board.lock_piece(self.active_piece)
        self.can_hold = True
        self.lock_timer = 0.0
        self.audio.play("lock")

        self.flashing_rows = self.board.get_full_rows()
        if self.flashing_rows:
            self.clear_anim_timer = 0.0
            self._flash_finished = False
            if self.settings.particles_enabled:
                self.particles.spawn_line_clear(self.flashing_rows)
            if len(self.flashing_rows) >= 4:
                self.shake.trigger(10.0, 0.45)
            else:
                self.shake.trigger(4.0, 0.18)
            self.state = GameState.LINE_CLEAR
        else:
            self.scoring.combo = -1
            self._spawn_next_piece()

    def _spawn_next_piece(self) -> None:
        self.active_piece = Tetromino.spawn(self.next_piece_kind)
        self.next_piece_kind = self.bag.next()
        self.drop_timer = 0.0
        self.lock_timer = 0.0
        self.ghost_piece = self.board.compute_ghost(self.active_piece)
        self.piece_anim.reset()
        self.piece_anim.on_spawn()

        if not self.board.is_valid_position(self.active_piece):
            self._enter_game_over()

    def _enter_game_over(self) -> None:
        self.audio.play("game_over")
        self.is_new_high_score = self.high_scores.is_high_score(self.scoring.score)
        if self.is_new_high_score:
            self.high_score_rank = self.high_scores.add(
                self.scoring.score,
                self.scoring.lines,
                self.scoring.level,
            )
        self.state = GameState.GAME_OVER

    def _render_state(self) -> GameState:
        if self.state == GameState.PAUSED:
            return self._state_before_pause
        if self.state == GameState.OPTIONS and self._options_return_state == GameState.PAUSED:
            return self._state_before_pause
        return self.state

    def draw(self) -> None:
        self.background.draw(self.virtual, WINDOW_WIDTH, WINDOW_HEIGHT)

        if self.state == GameState.MENU:
            self.main_menu.draw(self.virtual, self.high_scores.entries)
            self.fader.draw(self.virtual)
            self._present()
            return

        if self.state == GameState.OPTIONS and self._options_return_state == GameState.MENU:
            self.main_menu.draw(self.virtual, self.high_scores.entries)
            self.options_menu.draw(self.virtual, self.settings, self.assets)
            self.fader.draw(self.virtual)
            self._present()
            return

        render_state = self._render_state()
        self.renderer.set_shake(*self.shake_offset)

        glow = 0.0
        wave_progress = -1.0
        if render_state == GameState.LINE_CLEAR:
            flash_t = min(1.0, self.clear_anim_timer / LINE_CLEAR_FLASH)
            glow = 0.5 + 0.5 * abs((self.clear_anim_timer * 8) % 2 - 1)
            wave_progress = flash_t
        self.renderer.set_glow_pulse(glow)
        self.renderer.set_clear_wave(wave_progress)

        self.renderer.draw_board_background()

        clear_progress = 0.0
        if render_state == GameState.LINE_CLEAR:
            clear_progress = min(1.0, self.clear_anim_timer / LINE_CLEAR_FLASH)

        self.renderer.draw_locked_cells(
            self.board,
            flashing_rows=self.flashing_rows if render_state == GameState.LINE_CLEAR else None,
            clear_progress=clear_progress,
            row_fall=self.row_fall if render_state == GameState.ROW_FALL else None,
        )

        if render_state in (GameState.PLAYING, GameState.PAUSED):
            self.renderer.draw_ghost_piece(self.ghost_piece)
            self.renderer.draw_piece(
                self.active_piece,
                y_offset=self.piece_anim.offset_y,
                x_offset=self.piece_anim.offset_x,
                alpha=int(self.piece_anim.alpha),
                squash=self.piece_anim.squash,
            )

        if self.settings.particles_enabled:
            self.particles.draw(self.virtual)
        self.score_popups.draw(self.virtual)
        self.banner.draw(self.virtual, BOARD_CENTER)

        if self.theme_toast_timer > 0:
            alpha = min(1.0, self.theme_toast_timer / 0.3)
            self.hud.draw_theme_toast(self.theme_toast_label, alpha)

        next_queue = [self.next_piece_kind, *self.bag.peek(NEXT_QUEUE_COUNT - 1)]
        self.hud.draw_next_queue(next_queue)
        self.hud.draw_hold_piece(self.hold_kind, self.can_hold)
        self.hud.draw_stats(
            self.scoring.score,
            self.scoring.lines,
            self.scoring.level,
            self.scoring.combo,
            display_score=self.display_score,
        )

        if self.state in (GameState.PLAYING, GameState.LINE_CLEAR, GameState.ROW_FALL):
            self.hud.draw_play_chrome(touch_enabled=self.settings.touch_controls)

        if self.state == GameState.PAUSED:
            self.pause_menu.draw(self.virtual, self.assets)
        elif self.state == GameState.OPTIONS:
            self.options_menu.draw(self.virtual, self.settings, self.assets)
        elif self.state == GameState.GAME_OVER:
            self.hud.draw_game_over(
                self.scoring.score,
                self.is_new_high_score,
                self.high_score_rank,
            )

        self.fader.draw(self.virtual)
        self._present()

    def _present(self) -> None:
        fullscreen = is_android() or self.settings.fullscreen
        self.display_mapper.refresh(self.screen, fullscreen=fullscreen)
        if fullscreen:
            sw, sh = self.screen.get_size()
            scale = min(sw / WINDOW_WIDTH, sh / WINDOW_HEIGHT)
            nw = max(1, int(WINDOW_WIDTH * scale))
            nh = max(1, int(WINDOW_HEIGHT * scale))
            scaled = pygame.transform.smoothscale(self.virtual, (nw, nh))
            self.screen.fill(colors.BACKGROUND)
            self.screen.blit(scaled, ((sw - nw) // 2, (sh - nh) // 2))
        else:
            sw, sh = self.screen.get_size()
            if sw != WINDOW_WIDTH or sh != WINDOW_HEIGHT:
                scaled = pygame.transform.smoothscale(self.virtual, (sw, sh))
                self.screen.fill(colors.BACKGROUND)
                self.screen.blit(scaled, (0, 0))
            else:
                self.screen.blit(self.virtual, (0, 0))
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            dt = clamp_dt(self.clock.tick(FPS) / 1000.0, MAX_DT)
            self.handle_events()
            self.update(dt)
            self.draw()
        self.settings.save()
        pygame.quit()