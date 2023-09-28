#File for data designer

import json
import math
import random
import time
from typing import Optional, Type

import text
from maze import Coord, Maze, Room, cardinal

PI = 3.14159265359


class LabyrinthManager:
    """
    -- ATTRIBUTES --
    - lab: list[list[Room]]
    - difficulty_level
    - boss_pos: Coord
    - steve_pos: Coord

    -- METHODS --
    + get_room() -> Room
    + set_room(Room) -> None
    + layout() -> str
    + get_current_pos() -> Coord
    + move_boss(self) -> None
    + move_steve(self) -> None
    + can_move_here() -> bool
   """

    def __init__(self, labyrinth: Maze):
        self.lab = labyrinth
        self.difficulty_level = None
        self.boss_pos = Coord(9, 9)  # Decided upon generation
        self.steve_pos = Coord(0, 0)  # Decided upon generation

    def get_room(self, coord: Coord) -> "Room":
        """Returns the room at the given coordinates"""
        return self.lab.get(coord)

    def set_room(self, coord: Coord, room: "Room") -> None:
        """Returns the room at the given coordinates"""
        self.lab.set(coord, room)

    def layout(self) -> str:
        outputstr = ""
        for y in range(self.lab.y_size):
            fulltopstr = ""
            fullmidstr = ""
            fullbottomstr = ""
            for x in range(self.lab.x_size):
                room = self.get_room(Coord(x, self.lab.y_size - y - 1))
                N, S, E, W = room.get_neighbours()
                topstr = " || " if N else "    "
                bottomstr = " || " if S else "    "
                midstr = "=" if W else " "
                if room.steve_ishere():
                    midstr += "S"
                else:
                    midstr += "/"
                if room.boss_ishere():
                    midstr += "B"
                else:
                    midstr += "/"
                if E:
                    midstr += "="
                else:
                    midstr += " "
                fulltopstr += topstr
                fullmidstr += midstr
                fullbottomstr += bottomstr
            outputstr += fulltopstr + "\n" + fullmidstr + "\n" + fullbottomstr + "\n"
        return outputstr

    def get_current_pos(self) -> Coord:
        """Tells the coordinates of Steve's current location."""
        return self.steve_pos

    def move_boss(self) -> None:
        """Tries to move the boss from its current room to any (available) neighbour rooms.
        
        Does not jump over walls.
        If the boss cannot move in any of the 4 cardinal directions, an error is raised as it implies that the room it is in is completely isolated, which should not happen.
        """
        directions = list(cardinal.values())
        random.shuffle(directions)
        for direction in directions:
            if self.can_move_here(self.boss_pos, direction):
                self.boss_pos = self.boss_pos.add(direction)
                return None
        raise RuntimeError(
            f"Boss cannot move because its room {self.boss_pos} is unlinked to neighbours."
        )

    def move_steve(self, direction: Coord) -> None:
        assert self.can_move_here(self.steve_pos, direction)
        self.steve_pos = self.steve_pos.add(direction)

    def can_move_here(self, this_coords: Coord, direction: Coord) -> bool:
        """Tells whether an adjacent room is accessible.
        Rules:
        1. There is no wall between this room and the neighbour.
        2. the coordinates are within the range of valid coordinates.
        """
        assert self.lab.valid_coords(this_coords)
        thisroom = self.get_room(this_coords)
        return thisroom.dir_is_accessible(direction)

    def _steve_useitem(self, item) -> None:
        """Uses a utility item. Not implemented because no utility items are implemented yet."""
        raise NotImplementedError

    def _give_sound_clue(self):
        """Displays a message giving a hint how far away the boss is from steve
        and which direction steve might have to go in order to find the boss.
        
        Calculates straight line distance.
        Calculates which direction, N, S, E, W, NE, NW, SE, SW
        displays a message based on distance and direction.
        """
        displacement = self._sb_xy_distance()
        if displacement.is_zero():
            # They are in the same room, a clue doesn't need to be given LOL
            return None
        i = random.randint(0, 100)
        if i <= 20:
            print(random.choice(text.clues_noclue))
            return None

        r, dirstr = self._r_dir_calc(displacement)
        if r < 3:
            print(random.choice(text.clues_shortrange))
        elif r < 6:
            i = random.randint(1, 100)
            if i == 1:
                print(text.easter_egg)
            else:
                print(random.choice(text.clues_mediumrange))
        elif r < 10:
            print(random.choice(text.clues_longrange))
        else:
            print(random.choice(text.clues_distant))

        print(text.clues_direction(dirstr))

    def _r_dir_calc(self, coord: Coord) -> tuple[float, str]:
        """maths work for _give_sound_clue
        Finds r and theta using x and y (polar coordinates system)
        returns r and direction
        """
        displacement = self._sb_xy_distance()
        if displacement.is_zero():
            return None
        r = math.sqrt((coord.x**2) + (coord.y**2))  # Pythagorean theorem
        basic = abs(math.atan(coord.y / coord.x))
        if coord.y > 0:
            if coord.x > 0:
                theta = basic  # 1st quadrant
            elif coord.x < 0:
                theta = PI - basic  # 2nd quadrant
            else:
                theta = PI / 2  # up
        elif coord.y < 0:
            if coord.x < 0:
                theta = PI + basic  # 3rd quadrant
            elif coord.x > 0:
                theta = 2 * PI - basic  # 4th quadrant
            else:
                theta = 3 * PI / 2  # down
        elif coord.y == 0:
            if coord.x > 0:
                theta = 0  # right
            if coord.x < 0:
                theta = PI  # left
        dirstr = None
        dirstrlist = [
            "EAST", "NORTHEAST", "NORTH", "NORTHWEST", "WEST", "SOUTHWEST",
            "SOUTH", "SOUTHEAST"
        ]
        if theta <= PI / 8 or theta > 15 * PI / 8:
            dirstr = dirstrlist[0]
        lowerbound = PI / 8
        upperbound = lowerbound + PI / 4
        i = 1
        while i <= 7 and dirstr is not None:
            if i > lowerbound and i <= upperbound:
                dirstr = dirstrlist[i]
            i += 1
            lowerbound += PI / 4
            upperbound += PI / 4
        assert dirstr is not None
        return r, dirstr

    def _sb_xy_distance(self) -> Coord:
        """returns x, y displacement of boss from steve."""
        return self.steve_pos.direction_of(self.boss_pos)


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


DEFAULT_HITPOINTS = 50


class Slot:
    """Encapsulates a single inventory slot"""

    def __init__(self, item, count: int = 1):
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


class Inventory:
    """Encapsulates access to a character's inventory"""

    def __init__(self):
        self.contents = {}

    def add(self, item: "Item", num: int = 1) -> bool:
        """Add the item into the inventory.
        Return True if the item was successfully added to inventory,
        otherwise False.
        """
        if item.name in self.contents:
            self.contents[item.name].incr(num)
        else:
            self.contents[item.name] = Slot(item, num)
        return True

    def consume(self, item: "Item", num: int = 1) -> bool:
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

    def items(self, category: Optional[Type[Item]] = None) -> list[Slot]:
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
        self.armour = {}
        for slot in ["helmet", "chestplate", "leggings", "boots"]:
            self.armour[slot] = None
        self.health = DEFAULT_HITPOINTS
        self.weapon = None
        self.base_damage = 5  # default

    def __str__(self):
        return f"Steve has {self.health} HP."

    def display_inventory(self) -> None:
        if self.inventory.is_empty():
            print(text.inventory_empty + "\n")
            return
        print("\nYou have:\n")
        item_slots = self.inventory.items()
        for line in self.inventory.format_contents(item_slots):
            print(line)

    def get_all_items(self) -> list[Slot]:
        """Return a list of slots representing all inventory items"""
        return self.inventory.items()

    def get_food_items(self) -> list[Slot]:
        """Return a list of slots representing food items"""
        return self.inventory.items(Food)

    def take_item(self, item: "Item", num: int) -> bool:
        """Return True if the item was successfully added to inventory,
        otherwise False.
        """
        return self.inventory.add(item, num)

    def _discard_item(self, item: Item, num: int) -> None:
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

    def equip_armour(self, armouritem: Item) -> None:
        self.armour[armouritem.armor_slot] = armouritem
        return None

    def eat(self, foodindex: int) -> None:
        fooditem = self._inventory[foodindex]["item"]
        #validation
        assert foodindex >= 0
        assert isinstance(fooditem, Food)
        # consumption
        self.remove_item_from_inv(foodindex)
        self.heal_health(fooditem.hprestore)

    def find_item(self, item: "Item") -> int:
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
        prevhp = self.health
        if change > 0:
            self.health = min(self.health + change, 50)
            print(text.heal_report(self.health - prevhp, self.health))
            return None
        self.health = max(self.health + change, 0)
        print(text.damage_report(prevhp - self.health, self.health))
        return None

    def get_defence(self):
        defence = 0
        for armor in self.armour.values():
            if armor is not None:
                defence += armor.get_defence()
        return defence

    def equip_weapon(self, weapon):
        self.weapon = weapon

    def get_attack(self):
        if self.weapon is None:
            return self.base_damage
        return self.base_damage + self.weapon.get_attack()

    def isdead(self) -> bool:
        """Tells whether Steve is dead or not. Returns True if yes, else False."""
        if self.health <= 0:
            return True
        return False

    def take_damage(self, damage):
        """Updates hitpoints attribute based on how much damage is dealt."""
        if damage is not None:
            damage = int(damage * ((100 - self.get_defence()) / 100))
            self.health = max(0, self.health - damage)


class Creature:
    """
    -- ATTRIBUTES --
    name: name
    attack: damage stat
    hitpoints: current health
    maxhp: highest possible health
    -- METHODS --
    get_attack
    get_health
    """

    def __init__(self, name: str, maxhp: int, attack: int):
        self.name = name
        maxhp = self._generate_maxhp(maxhp, turn)
        self.hitpoints = maxhp
        self.attack = self._generate_attack(attack, turn)
        self.maxhp = maxhp

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
