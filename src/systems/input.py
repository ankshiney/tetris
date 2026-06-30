"""Keyboard input with DAS/ARR for smooth repeated movement."""

from enum import Enum, auto

import pygame

from config.settings import ARR_INTERVAL, DAS_DELAY, SOFT_DROP_INTERVAL


class Action(Enum):
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_DOWN = auto()
    ROTATE_CW = auto()
    ROTATE_CCW = auto()
    HARD_DROP = auto()
    HOLD = auto()


class InputHandler:
    """Translates Pygame events and held keys into game actions."""

    def __init__(self) -> None:
        self._das_direction = 0
        self._das_timer = 0.0
        self._arr_timer = 0.0
        self._soft_drop_timer = 0.0

    def process_event(self, event: pygame.event.Event) -> list[Action]:
        if event.type != pygame.KEYDOWN:
            if event.type == pygame.KEYUP and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self._sync_das_direction()
            return []

        actions: list[Action] = []

        if event.key == pygame.K_LEFT:
            actions.append(Action.MOVE_LEFT)
            self._das_direction = -1
            self._das_timer = 0.0
            self._arr_timer = 0.0
        elif event.key == pygame.K_RIGHT:
            actions.append(Action.MOVE_RIGHT)
            self._das_direction = 1
            self._das_timer = 0.0
            self._arr_timer = 0.0
        elif event.key == pygame.K_DOWN:
            actions.append(Action.MOVE_DOWN)
            self._soft_drop_timer = 0.0
        elif event.key in (pygame.K_UP, pygame.K_x):
            actions.append(Action.ROTATE_CW)
        elif event.key == pygame.K_z:
            actions.append(Action.ROTATE_CCW)
        elif event.key == pygame.K_SPACE:
            actions.append(Action.HARD_DROP)
        elif event.key == pygame.K_c:
            actions.append(Action.HOLD)

        return actions

    def poll(self, dt: float) -> list[Action]:
        actions: list[Action] = []
        keys = pygame.key.get_pressed()

        if self._das_direction == -1 and keys[pygame.K_LEFT]:
            actions.extend(self._poll_das(dt, Action.MOVE_LEFT))
        elif self._das_direction == 1 and keys[pygame.K_RIGHT]:
            actions.extend(self._poll_das(dt, Action.MOVE_RIGHT))
        elif not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self._das_direction = 0

        if keys[pygame.K_DOWN]:
            self._soft_drop_timer += dt
            if self._soft_drop_timer >= SOFT_DROP_INTERVAL:
                self._soft_drop_timer = 0.0
                actions.append(Action.MOVE_DOWN)

        return actions

    def is_soft_dropping(self) -> bool:
        return pygame.key.get_pressed()[pygame.K_DOWN]

    def _poll_das(self, dt: float, action: Action) -> list[Action]:
        self._das_timer += dt
        if self._das_timer < DAS_DELAY:
            return []
        self._arr_timer += dt
        if self._arr_timer >= ARR_INTERVAL:
            self._arr_timer = 0.0
            return [action]
        return []

    def _sync_das_direction(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self._das_direction = -1
        elif keys[pygame.K_RIGHT]:
            self._das_direction = 1
        else:
            self._das_direction = 0
        self._das_timer = 0.0
        self._arr_timer = 0.0