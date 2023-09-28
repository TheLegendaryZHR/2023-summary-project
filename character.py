import random
from typing import Container, Generic, Optional, Type, TypeVar

from action import Action
import data
import text

DEFAULT_HITPOINTS = 50
I = TypeVar("I")


class Slot(Generic[I]):
    """Encapsulates a single inventory slot"""

    def __init__(self, item: I, count: int = 1):
        self.item = item
        self.count = count

    def incr(self, num: int) -> None:
        """Increment count by num"""
        assert num > 0
        self.count += num

    def decr(self, num: int) -> None:
        """Decrement count by num"""
        assert num > 0
        assert self.count >= num
        self.count -= num


class Inventory(Container[data.Item]):
    """Encapsulates access to a character's inventory"""

    def __init__(self):
        self.contents = {}

    def __contains__(self, item: data.Item) -> bool:
        """Implements support for the `in` keyword.
        Required by the Container type.
        """
        return any(slot.item.name == item.name
                   for slot in self.contents.values())

    def add(self, item: data.Item, num: int = 1) -> bool:
        """Add the item into the inventory.
        Return True if the item was successfully added to inventory,
        otherwise False.
        """
        if item.name in self.contents:
            self.contents[item.name].incr(num)
        else:
            self.contents[item.name] = Slot(item, num)
        return True

    def consume(self, item: data.Item, num: int = 1) -> bool:
        """remove num of item from the inventory.
        Return True if the item was successfully removed inventory,
        otherwise False.
        """
        # Check item existence
        if item.name not in self.contents:
            return False
        # Check if count is sufficient
        slot = self.contents[item.name]
        if slot.count < num:
            return False
        self.contents[item.name].decr(num)
        return True

    def is_empty(self) -> bool:
        return len(self.contents) == 0

    def length(self) -> int:
        """Returns number of slots in inventory"""
        return len(self.contents)

    def format_contents(self, slots: list[Slot]) -> list[str]:
        """Return a list of strings, each string representing
        one item in the inventory and its count"""
        contents = []
        for i, slot in enumerate(slots, start=1):
            contents.append(f"{i:>2}. {slot.count:>2} x {slot.item.name}")
        return contents

    def items(self, category: Optional[Type[data.Item]] = None) -> list[Slot]:
        """Return a list of item slots in inventory of the given type."""
        if not category:
            return list(self.contents.values())
        else:
            return [
                slot for slot in self.contents.values()
                if isinstance(slot.item, category)
            ]


class Steve:
    """
    -- ATTRIBUTES --
    
    -- METHODS --
    """

    def __init__(self):
        self.inventory = Inventory()
        self._inventory = []  # list of dict
        # each dict in self.inventory describes an item, as well as the number of it in the inventory.
        # e.g. {"item": Health_Potion, "number": 2}
        # There should NOT be duplicate dicts in self.inventory e.g. 2 different dicts in self.inventory with "item" being Health_Potions
        self.armor = {}
        for slot in ["helmet", "chestplate", "leggings", "boots"]:
            self.armor[slot] = None
        self.health = DEFAULT_HITPOINTS
        self.weapon = None
        self.base_damage = 5  # default

    def __str__(self):
        return f"Steve has {self.health} HP."

    def display_inventory(self) -> None:
        item_slots = self.inventory.items()
        for line in self.inventory.format_contents(item_slots):
            print(line)

    def get_all_items(self) -> list[Slot]:
        """Return a list of slots representing all inventory items"""
        return self.inventory.items()

    def get_food_items(self) -> list[Slot]:
        """Return a list of slots representing food items"""
        return self.inventory.items(data.Food)

    def take_item(self, item: data.Item, num: int) -> bool:
        """Return True if the item was successfully added to inventory,
        otherwise False.
        """
        return self.inventory.add(item, num)

    def _discard_item(self, item: data.Item, num: int) -> None:
        for index, dict_ in enumerate(
                self._inventory):  # Linear search through inventory
            if str(item) == str(
                    dict_["item"]):  # new_item is already in the inventory
                self._inventory[index]["number"] -= num
                if self._inventory[index]["number"] <= 0:
                    self._inventory[index] = None
                return None
        print("Error: Item is not in inventory.")
        return None

    def equip_armor(self, armoritem: data.Armor) -> None:
        self.armor[armoritem.armor_slot] = armoritem
        return None

    def eat(self, foodindex: int) -> None:
        fooditem = self._inventory[foodindex]["item"]
        #validation
        assert foodindex >= 0
        assert isinstance(fooditem, data.Food)
        # consumption
        self.remove_item_from_inv(foodindex)
        self.heal_health(fooditem.hprestore)

    def find_item(self, item: data.Item) -> int:
        """Linear search through inventory to find the index of the item"""
        for i in self._inventory:
            if str(i["item"]) == str(item):
                return i
        return -1  # return value is -1 when not found.

    def remove_item_from_inv(self, index) -> None:
        assert index in range(self.inventory.length())
        if self._inventory[index][
                "number"] == 1:  # Steve has only 1 of this such item left
            self._inventory.pop(index)
            # This dict is removed as there are no more of such items in the inventory
            return None
        self._inventory[index]["number"] -= 1
        return None

    def heal_health(self, change: int) -> None:
        if change == 0:
            return None
        if change > 0:
            self.health = min(self.health + change, 50)
            return None
        self.health = max(self.health + change, 0)
        return None

    def get_defence(self) -> int:
        defence = 0
        for armor in self.armor.values():
            if armor is not None:
                defence += armor.get_defence()
        return defence

    def equip_weapon(self, weapon: data.Weapon) -> None:
        self.weapon = weapon

    def get_attack(self) -> int:
        if self.weapon is None:
            return self.base_damage
        return self.base_damage + self.weapon.get_attack()

    def isdead(self) -> bool:
        """Tells whether Steve is dead or not. Returns True if yes, else False."""
        if self.health <= 0:
            return True
        return False

    def take_damage(self, damage: int) -> None:
        """Updates hitpoints attribute based on how much damage is dealt."""
        assert isinstance(damage, int)
        damage = int(damage * ((100 - self.get_defence()) / 100))
        self.health = max(0, self.health - damage)


class Creature:
    """
    -- ATTRIBUTES --
    + name: str
    + maxhp: int
    + attack: int
    + hitpoints: int
    - actions: list[Action]
    
    -- METHODS --
    get_attack
    get_health
    """

    def __init__(self,
                 name: str,
                 maxhp: int,
                 attack: int,
                 actions: Optional[list[Action]] = None):
        self.name = name
        self.maxhp = maxhp
        self.attack = attack
        self.hitpoints = maxhp
        self.actions = actions

    def __str__(self):
        return f"Name: {self.name}, HP:{self.hitpoints}/{self.maxhp}"

    def _generate_maxhp(self, maxhp: int, turn_number: int) -> int:
        maxhp = int(
            (maxhp * ((turn_number / 10) + 1) * random.randint(90, 110) / 100))
        return maxhp

    def get_name(self) -> str:
        """Returns the name of the creature"""
        return self.name

    def _generate_attack(self, attack: int, turn_number: int) -> int:
        """"""
        attack = int((attack) * ((turn_number / 10) + 1) *
                     (random.randint(90, 110) / 100))
        return attack

    def get_attack(self):
        """Getter for attack attribute.
        Might not need this"""
        return self.attack

    def get_health(self):
        """Getter for hitpoints attribute"""
        return self.hitpoints

    def take_damage(self, damage: int) -> None:
        """Updates health based on the damage the creature suffered"""
        self.hitpoints = max(0, self.hitpoints - damage)

    def random_move(self) -> int:
        """Chooses randomly from the following attack moves that the creature can make:
        
        1. normal attack
        
        """
        return self.get_attack()

    def isdead(self) -> bool:
        """Tells whether Creature is dead or not. Returns True if yes, else False."""
        if self.hitpoints <= 0:
            return True
        return False


class Creeper(Creature):

    def _generate_attack(self, attack: int, turn_number: int) -> int:
        random_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        print(text.creeper_prompt)
        time.sleep(2)
        start_time = time.time()
        inp = input(text.creeper_quickevent(random_letter))
        print(text.creeper_explode)
        self.hitpoints = 0
        if inp.upper() == random_letter and time.time() - start_time <= 1.8:
            print("\n" + text.creeper_dodge_success)
            return None
        elif inp.upper() != random_letter:
            print("\n" + text.creeper_dodge_failure)
        elif (time.time() - start_time) > 1.8:
            print("\n" + text.creeper_dodge_slow)
        attack = int((attack) * ((turn_number / 10) + 1) *
                     (random.randint(90, 110) / 100))
        return attack


class Boss(Creature):
    """
    -- ATTRIBUTES --
    
    -- METHODS --
    """

    def __init__(self):
        super().__init__("King Warden", 100, 10)

    def heal(self) -> None:
        """One of the moves that the boss can make
        Deals boss by an amount"""
        heal = random.randint(10, 20)
        self.hitpoints = min(self.hitpoints + heal, self.maxhp)

    def sonic_boom(self) -> bool:
        """Unimplemented attack that would make the battle more interesting"""
        raise NotImplementedError

    def random_move(self) -> int:
        """If current health gt 50 HP, returns attack damage.
        If current health lte 50 HP, 30 percent chance it heals itself, and does no damage. Otherwise, returns attack damage."""
        if self.hitpoints > 50:
            return self.attack
        if random.randint(0, 100) <= 30:
            self.heal()
            return 0
        return self.attack
