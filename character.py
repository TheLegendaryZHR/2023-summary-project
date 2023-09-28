import json
import random
from typing import Container, Generic, Optional, Type, TypeVar

from action import Action
import data
import text


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
        if self.contents[item.name].count == 0:
            del self.contents[item.name]
        return True

    def get(self, name: str) -> data.Item:
        return self.contents[name]

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

    def __init__(self, name: str, maxhp: int, base_damage: int):
        self.inventory = Inventory()
        self.name = name
        self.maxhp = maxhp
        self.health = maxhp
        self.base_damage = base_damage
        self.armor: dict[str, Optional[data.Armor]] = {
            "helmet": None,
            "chestplate": None,
            "leggings": None,
            "boots": None,
        }
        self.weapon = None

    def __str__(self):
        return self.status()

    def status(self) -> str:
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

    def equip_armor(self, armoritem: data.Armor) -> None:
        self.armor[armoritem.armor_slot] = armoritem

    def eat(self, food: data.Food) -> None:
        assert isinstance(food, data.Food)
        self.inventory.consume(food)
        self.heal(food.hprestore)

    def heal(self, change: int) -> None:
        assert change > 0
        self.health = min(self.health + change, self.maxhp)

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
        """Updates health attribute based on how much damage is dealt."""
        assert isinstance(damage, int)
        damage = int(damage * ((100 - self.get_defence()) / 100))
        self.health = max(0, self.health - damage)


class Creature:
    """
    -- ATTRIBUTES --
    + name: str
    + maxhp: int
    + attack: int
    + health: int
    - actions: list[Action]
    
    -- METHODS --
    + take_damage(dmg: int) -> None
    + get_attack() -> int
    """

    def __init__(self,
                 name: str,
                 maxhp: int,
                 attack: int,
                 actions: list[Action]):
        self.name = name
        self.maxhp = maxhp
        self.attack = attack
        self.health = maxhp
        self.actions: dict[str, Action] = {
            action.name: action
            for action in actions
        }

    def __str__(self):
        return f"Name: {self.name}, HP:{self.health}/{self.maxhp}"

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

    def take_damage(self, damage: int) -> None:
        """Updates health based on the damage the creature suffered"""
        self.health = max(0, self.health - damage)

    def act(self, choice: str) -> Action:
        """Chooses an action from available actions.
        If not overridden, will choose a random action.
        """
        return random.choice(self.actions)

    def isdead(self) -> bool:
        """Tells whether Creature is dead or not. Returns True if yes, else False."""
        if self.health <= 0:
            return True
        return False


class HealingCreature(Creature):
    """A creature that is capable of healing.

    This creature must have Heal in its actions.
    """
    def __init__(self,
                 name: str,
                 maxhp: int,
                 attack: int,
                 actions: list[Action]) -> None:
        super().__init__(name, maxhp, attack, actions)
        assert "Heal" in self.actions

    def act(self) -> Action:
        """If current health gt 50 HP, returns attack damage.
        If current health lte 50 HP, 30 percent chance it heals itself, and does no damage. Otherwise, returns attack damage."""
        if self.health <= 50:
            if random.randint(0, 100) <= 30:
                return self.actions["Heal"]
        action = None
        while not isinstance(action, Attack):
            action = random.choice(self.actions)
        return action


with open("content/creatures.json", 'r', encoding='utf-8') as f:
    creature_data = json.load(f)
