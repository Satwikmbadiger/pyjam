import time as _time
from dataclasses import dataclass
from typing import Dict, Union, Set

import pygame

__all__ = [
    "Inputs",
    "Button",
    "Axis",
    "QuitEvent",
    "KeyPress",
    "JoyButton",
    "JoyAxisTrigger",
    "JoyAxis",
]

version = "1.0"


def clamp(x, mini, maxi):

    if maxi < mini:
        return x
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


class ButtonInput:

    def match(self, event) -> bool:
        raise NotImplementedError

    def update(self, event):
        if self.match(event):
            return self.pressed(event)
        return None

    def pressed(self, event) -> bool:

        raise NotImplementedError


@dataclass(frozen=True)
class KeyPress(ButtonInput):

    key: int

    def match(self, event):
        return event.type in (pygame.KEYDOWN, pygame.KEYUP) and event.key == self.key

    def pressed(self, event) -> bool:
        return event.type == pygame.KEYDOWN


@dataclass(frozen=True)
class JoyButton(ButtonInput):

    button: int
    joy_id: int = 0

    def match(self, event):
        return (
            event.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP)
            and event.joy == self.joy_id
            and event.button == self.button
        )

    def pressed(self, event):
        return event.type == pygame.JOYBUTTONDOWN


@dataclass(frozen=True)
class JoyAxisTrigger(ButtonInput):

    axis: int
    threshold: float = 0.5
    above: bool = True
    joy_id: int = 0

    def match(self, event) -> bool:
        return (
            event.type == pygame.JOYAXISMOTION
            and event.joy == self.joy_id
            and event.axis == self.axis
        )

    def pressed(self, event) -> bool:
        return self.above == (event.value > self.threshold)


class QuitEvent(ButtonInput):
    def match(self, event) -> bool:
        return event.type == pygame.QUIT

    def pressed(self, event) -> bool:
        return True


@dataclass(frozen=True)
class JoyAxis:
    axis: int
    reversed: bool = False
    threshold: float = 0.2
    sensibility: float = 1.0
    joy_id: int = 0
    def match(self, event):

        return (
            event.type == pygame.JOYAXISMOTION
            and event.joy == self.joy_id
            and event.axis == self.axis
        )

    def value(self, event):

        if abs(event.value) < self.threshold:
            return 0

        scaled = event.value * self.sensibility
        if self.reversed:
            return -scaled
        else:
            return scaled


class RepeatCallback:
    def __init__(self, callback, delay):
        self.delay = delay
        self.callback = callback
        self.repetitions = 0


class Button:
    def __init__(self, *keys):

        self._keys: Set[ButtonInput] = {
            KeyPress(key) if isinstance(key, int) else key for key in keys
        }
        self._pressed = {}
        self.just_released = False
        self.just_pressed = False
        self.just_double_pressed = False

        self._always = set()
        self._on_press = set()
        self._on_release = set()
        self._on_double_press = set()
        self._repeat: Set[RepeatCallback] = set()

        self.last_press = float("-inf")
        self.press_time = 0
        self.dt = 0  # time since last frame

    def _call_all(self, container):
        for f in container:
            f(self)

    def update(self, dt):

        self.last_press += dt
        if self.pressed:
            self.press_time += dt

        self.dt = dt

        self._call_all(self._always)

        if self.just_pressed:
            self._call_all(self._on_press)

        if self.just_double_pressed:
            self._call_all(self._on_double_press)

        if self.just_released:
            self._call_all(self._on_release)

        if self.pressed:
            for c in self._repeat:
                if c.delay * c.repetitions <= self.press_time:
                    c.repetitions += 1
                    c.callback(self)

    def actualise(self, events):
        self.just_pressed = False
        self.just_double_pressed = False
        self.just_released = False

        old_pressed = self.pressed
        for event in events:
            for key in self._keys:
                if key.match(event):
                    self._pressed[key] = key.pressed(event)

        if not old_pressed:
            if self.pressed:
                self.press_time = 0
                self.just_pressed = True
            if self.double_pressed:
                self.just_double_pressed = True
        else:
            if not self.pressed:
                # All keys were just released
                self.last_press = 0
                self.just_released = True
                for c in self._repeat:
                    c.repetitions = 0

    @property
    def pressed(self):
        return sum(self._pressed.values(), 0) > 0

    @property
    def double_pressed(self):
        return self.pressed and self.last_press < 0.1

    def always_call(self, callback):
        self._always.add(callback)

    def on_press(self, callback):
        self._on_press.add(callback)

    def on_release(self, callback):
        self._on_release.add(callback)

    def on_double_press(self, callback):
        self._on_double_press.add(callback)

    def on_press_repeated(self, callback, delay):

        self._repeat.add(RepeatCallback(callback, delay))

    def remove(self, callback):
        if callback in self._always:
            self._always.remove(callback)
        if callback in self._on_press:
            self._on_press.remove(callback)
        if callback in self._on_release:
            self._on_release.remove(callback)
        if callback in self._on_double_press:
            self._on_double_press.remove(callback)

        to_remove = [rc for rc in self._repeat if rc.callback == callback]
        for rc in to_remove:
            self._repeat.remove(rc)


class Axis:
    def __init__(self, negative, positive, *axis, smooth=0.1):

        if isinstance(negative, int):
            negative = [negative]
        if isinstance(positive, int):
            positive = [positive]

        self._negative = {KeyPress(n): False for n in negative}
        self._positive = {KeyPress(p): False for p in positive}
        self._axis = set(axis)
        self._callbacks = set()
        self._smooth = smooth

        self.non_zero_time = 0
        self.zero_time = 0

        # Hold the number of keys pressed
        self._int_value = 0
        # Hold the smoothed number of keys pressed
        self._value = 0
        # Hold the total value of axis,
        # separately because of different tracking methods
        self._axis_value = 0

    def __str__(self):
        return f"Axis({self.value})"

    @property
    def value(self):
        return clamp(self._value + self._axis_value, -1, 1)

    def always_call(self, callback):
        self._callbacks.add(callback)

    def remove(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def update(self, dt):
        if self._int_value != 0:
            # Nonzero check is okay as JoyAxis already count the threshold
            self.non_zero_time += dt
            self.zero_time = 0
        else:
            self.non_zero_time = 0
            self.zero_time += dt

        if self._smooth <= 0:
            self._value = self._int_value
        else:
            dv = dt / self._smooth
            if self._int_value > 0:
                self._value += dv
            elif self._int_value < 0:
                self._value -= dv
            else:
                if self._value > 0:
                    self._value -= dv
                else:
                    self._value += dv

                if abs(self._value) <= dv:
                    # To have hard zeros
                    self._value = 0
        self._value = clamp(self._value, -1, 1)

        for c in self._callbacks:
            c(self)

    def actualise(self, events):
        axis_value = 0
        any_axis = False
        for event in events:
            for pos in self._positive:
                if pos.match(event):
                    self._positive[pos] = pos.pressed(event)
            for neg in self._negative:
                if neg.match(event):
                    self._negative[neg] = neg.pressed(event)

            for axis in self._axis:
                if axis.match(event):
                    # We take the most extreme value
                    val = axis.value(event)
                    if abs(val) > abs(axis_value):
                        axis_value = val
                    any_axis = True

        self._int_value = sum(self._positive.values()) - sum(self._negative.values())
        if any_axis:
            self._axis_value = axis_value


class Inputs(dict, Dict[str, Union[Button, Axis]]):
    def __init__(self):
        super().__init__()
        self._last_time = _time.time()

    def trigger(self, events):

        # make sure we can iterate it multiple times
        events = list(events)
        for inp in self.values():
            inp.actualise(events)

        dt = _time.time() - self._last_time
        self._last_time = _time.time()

        for inp in self.values():
            # update times and trigger callbacks
            inp.update(dt)