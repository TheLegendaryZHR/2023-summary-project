"""action.py

Encapsulates action that can be carried out by characters.

Should not rely on other modules apart from text.py.
"""
import random
import time
from typing import Type

import text


class Action:
    """An action in the game has a name.

    Actions, when performed, may have side-effects,
    such as displaying text, or requiring player input.

    Attributes
    ----------
    + name: str

    Methods
    -------
    + do() -> int
    """
    name: str

    def do(self) -> int:
        raise NotImplementedError


class Attack(Action):
    """An attack generates a value for combat purposes.

    Attacks may have side-effects, such as displaying text
    or requiring player input.

    Attributes
    ----------
    + name: str
    - value: int

    Methods
    -------
    + get() -> int
    + do() -> int
    """
    name = "Attack"

    def __init__(self, value: int) -> None:
        self._value = value

    def get(self) -> int:
        """Get the calculated attack magnitude"""
        return self._value

    def do(self) -> int:
        """Carry out the attack, including any required effects.
        Return the final attack value.
        """
        return self.get()


class Explode(Attack):
    name = "Explode"

    def do(self) -> int:
        random_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        print(text.creeper_prompt)
        time.sleep(2)
        start_time = time.time()
        inp = input(text.creeper_quickevent(random_letter))
        print(text.creeper_explode)
        self.hitpoints = 0
        if inp.upper() == random_letter and time.time() - start_time <= 1.8:
            print("\n" + text.creeper_dodge_success)
            return 0
        elif inp.upper() != random_letter:
            print("\n" + text.creeper_dodge_failure)
        elif (time.time() - start_time) > 1.8:
            print("\n" + text.creeper_dodge_slow)
        return self.get()


class SonicBoom(Attack):
    name = "Sonic Boom"

    def do(self) -> int:
        print("This attack is not yet implemented, sorry!")
        return self.get()


class Heal(Action):
    """A heal generates a value for combat purposes.

    Heals may have side-effects, such as displaying text
    or requiring player input.

    Attributes
    ----------
    + name: str
    - value: int

    Methods
    -------
    + get() -> int
    + do() -> int
    """
    name: str = "Heal"

    def __init__(self, value: int) -> None:
        self._value = value

    def get(self) -> int:
        """Get the calculated healing magnitude"""
        return self._value

    def do(self) -> int:
        """Carry out the healing, including any required effects.
        Return the final healing value.
        """
        return self.get()


def get(name: str) -> Type[Action]:
    if name == "Attack":
        return Attack
    if name == "Explode":
        return Explode
    if name == "Heal":
        return Heal
     if name == "Sonic Boom":
        return SonicBoom
    raise ValueError(f"{name}: no such action")
