#File for data designer

import json
import random

import text


FOODITEM = "FOODITEM"
WEAPONITEM = "WEAPONITEM"
ARMOURITEM = "ARMOURITEM"
UTILITYITEM = "UTILITYITEM"


class Item:
    """
    -- ATTRIBUTES --
    
    -- METHODS --
    """

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        outputstr = f"{self.name} [{self.__class__.__name__}]"
        return outputstr


class Food(Item):

    def __init__(self, name: str, hprestore: int):
        super().__init__(name)
        self.hprestore = hprestore

    def __str__(self):
        return super().__str__() + f": restores {self.hprestore} HP"

    def get_restore(self):
        return self.hprestore


class Armor(Item):

    def __init__(self, name: str, defence: int, armor_slot: int):
        super().__init__(name)
        self.defence = defence
        self.armor_slot = armor_slot

    def __str__(self):
        return super().__str__() + f": provides {self.defence} defence"

    def get_defence(self):
        return self.defence


class Weapon(Item):

    def __init__(self, name: str, attack: int):
        super().__init__(name)
        self.attack = attack

    def __str__(self):
        return super().__str__() + f": deals {self.attack} damage"

    def get_attack(self):
        return self.attack


with open("content/items/armor.json", 'r', encoding='utf-8') as f:
    armor_data = json.load(f)
with open("content/items/food.json", 'r', encoding='utf-8') as f:
    food_data = json.load(f)
with open("content/items/weapon.json", 'r', encoding='utf-8') as f:
    weapon_data = json.load(f)
