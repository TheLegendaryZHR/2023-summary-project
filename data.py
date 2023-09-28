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
        outputstr = f"Name: {self.name}\nType: {self.__class__.__name__}"
        return outputstr


class Food(Item):

    def __init__(self, name: str, hprestore: int):
        super().__init__(name)
        self.hprestore = hprestore

    def __str__(self):
        return super().__str__() + f"\nRestores: {self.hprestore} HP"

    def get_restore(self):
        return self.hprestore


class Armor(Item):

    def __init__(self, name: str, defence: int, armor_slot: int):
        super().__init__(name)
        self.defence = defence
        self.armor_slot = armor_slot

    def __str__(self):
        return super().__str__() + f"\nProvides: {self.defence} defence"

    def get_defence(self):
        return self.defence


class Weapon(Item):

    def __init__(self, name: str, attack: int):
        super().__init__(name)
        self.attack = attack

    def __str__(self):
        return super().__str__() + f"\nDoes: {self.attack} damage"

    def get_attack(self):
        return self.attack


def random_creature() -> "Creature":
    """returns a randomly generated creature"""
    creature_data = random.choice(creature_list)
    if creature_data["name"] == "Creeper":
        #remove creeper for now
        return Creature(creature_data["name"], creature_data["base_hp"],
                        creature_data["base_atk"])
    else:
        return Creature(creature_data["name"], creature_data["base_hp"],
                        creature_data["base_atk"])


item_type_list = ["Armor", "Food", "Weapon"]


def random_item() -> "Item":
    """returns a randomly generated item"""
    item_type = random.choice(item_type_list)
    if item_type == "Armor":
        item_data = random.choice(armor_list)
        return Armor(item_data["name"], item_data["defence"],
                     item_data["slot"])
    elif item_type == "Food":
        item_data = random.choice(food_list)
        return Food(item_data["name"], item_data["hprestore"])
    elif item_type == "Weapon":
        item_data = random.choice(weapon_list)
        return Weapon(item_data["name"], item_data["atk"])


with open("content/creatures.json", 'r', encoding='utf-8') as f:
    creature_list = json.load(f)
with open("content/items/armor.json", 'r', encoding='utf-8') as f:
    armor_list = json.load(f)
with open("content/items/food.json", 'r', encoding='utf-8') as f:
    food_list = json.load(f)
with open("content/items/weapon.json", 'r', encoding='utf-8') as f:
    weapon_list = json.load(f)
turn = 1
