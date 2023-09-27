#File for data designer

import json
import random
import math
import time

# NOVICE = "NOVICE"
# JOURNEYMAN = "JOURNEYMAN"
# MASTER = "MASTER"
STARTROOM = "STARTROOM"
DIRLIST = [[0, 1], [0, -1], [1, 0], [-1, 0]]  # according to N, S, E, W
PI = 3.14159265359

#STANLEY TEST


class Coord:
    """Encapsulates a pair of 2D coordinates.
    Coordinates are represented as (x, y), with x and y being ints.
    """

    def __init__(self, x: int, y: int) -> None:
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.x = x
        self.y = y

    def add(self, coord: "Coord") -> "Coord":
        """Returns a Coord that is the sum of self and coord"""
        return Coord(self.x + coord.x, self.y + coord.y)

    def is_adjacent(self, coord: "Coord") -> bool:
        """Checks if coord is directly N, S, E, or W of self.
        Returns True if yes, otherwise False.
        """
        if abs(self.x - coord.x) == 1 and (self.y - coord.y) == 0:
            return True
        if abs(self.y - coord.y) == 1 and (self.x - coord.x) == 0:
            return True
        return False

    def is_same(self, coord: "Coord") -> bool:
        return (self.x == coord.x) and (self.y == coord.y)

    def is_zero(self) -> bool:
        return self.x == 0 and self.y == 0

    def direction_of(self, neighbour: "Coord") -> "Coord":
        return Coord(neighbour.x - self.x, neighbour.y - self.y)


cardinal = {
    "NORTH": Coord(0, 1),
    "SOUTH": Coord(0, -1),
    "EAST": Coord(0, 1),
    "WEST": Coord(0, -1)
}

LABSIZE = 10  # cannot be too small!!


def valid_coords(roomcoords: Coord) -> bool:
    if roomcoords.x not in list(range(LABSIZE)) or roomcoords.y not in list(range(LABSIZE)):
        return False
        print(
            f"valid_coords() says that roomcoords {roomcoords} elements are not within integers from 0 to {LABSIZE - 1}."
        )
    return True


class LabyrinthGenerator:
    """Generates a labyrinth for the game.
    
    -- ATTRIBUTES --
    - lab: list[list[Room]]
    
    -- METHODS --
    + generate(self) -> None
    - generate_place_steve_boss() -> None:
    - generate_link_rooms(room1coords: list, room2coords: list) -> None:
    - generate_rooms_connected() -> bool:
   """

    def __init__(self):
        self.lab = []
        for _ in range(LABSIZE):
            self.lab.append([None] * LABSIZE)

    def get_room(self, coord: Coord) -> "Room":
        """Returns the room at the given coordinates"""
        return self.lab[coord.x][coord.y]

    def set_room(self, coord: Coord, room: "Room") -> None:
        """Returns the room at the given coordinates"""
        self.lab[coord.x][coord.y] = room

    def get_lab(self) -> list[list["Room"]]:
        """Return the generated lab"""
        return self.lab

    def generate(self) -> None:
        """Generates a maze without walls"""
        for x in range(LABSIZE):
            for y in range(LABSIZE):
                coord = Coord(x, y)
                self.set_room(coord, Room(coord))
        self._generate_nowalls()

    def _generate_nowalls(self) -> None:
        """Helper method for the generate() method.
        Makes sure all rooms are connected to all adjacent rooms 
        in the labyrinth.
        """
        for x in range(LABSIZE):
            for y in range(LABSIZE):
                coord = Coord(x, y)
                this = self.get_room(coord)
                for direction in cardinal.values():
                    neighbour = coord.add(direction)
                    if valid_coords(neighbour):
                        neighbour = self.get_room(neighbour)
                        this.connect_dir(direction, neighbour)
 
    def generate_random(self) -> None:
        """Generates the maze by:
        1. Filling in empty rooms in the empty maze
        2. Chooses (somewhat) randomly which room is the startroom room where
           Steve is placed
        3. Places the boss room opposite to startroom
        4. Makes the rooms connected like a maze structure (with walls)
        5. (Unimplemented functionality) Takes in a difficulty level and sets
           the game accordingly
        
        Requires the use of helper methods, namely:

        _generate_place_steve_boss()
        _generate_maze()
        _generate_recursive_linking()
        _generate_count_unconnected_rooms()
        _generate_force_connect()
        _generate_is_linkable_by_recursive()
        _generate_link_rooms()
        """
        # self.difficulty_level = difficulty_level
        # put in empty rooms
        for x in range(LABSIZE):
            for y in range(LABSIZE):
                coord = Coord(x, y)
                self.set_room(coord, Room(coord))
        # choose location for steve and boss
        self._generate_place_steve_boss()
        # connecting all the rooms in a maze-like fashion
        self._generate_maze(self.steve_pos)

    def _generate_place_steve_boss(self) -> None:
        """One of many helper methods of the generate() method.

        Chooses a startroom somewhat randomly, places Steve there,
        and places the boss in a room opposite of startroom

        How startroom is chosen:
        - The possible rooms to be picked are rooms nearer to the perimeter than the center.
        - e.g. If the labyrinth is 10 by 10 rooms, the middle 6 by 6 rooms cannot
          be chosen as startroom. the surrounding 64 rooms can be chosen as rooms.
        - Of the 64 rooms nearing the far sides of the labyrinth, one room is chosen
          at random.
        - This means that LABSIZE cannot be too small, or the generation may break.
          ie LABSIZE cannot be less than 4.

        How bossroom is chosen:
        - e.g. LABSIZE is set to 10 and startroom coords are [1, 7]
        - bossroom is at the opposite of the labyrinth at [8, 2]

        Startroom will be remembered throughout the game, the starting position
        of the boss will not be remembered. 
        """
        # choose position of Start room randomly
        n = LABSIZE // 4
        n = random.randint(-n, n - 1) % LABSIZE
        m = random.randint(0, LABSIZE - 1)
        nm = [n, m]
        random.shuffle(nm)
        steve_coord = Coord(nm[0], nm[1])
        self.get_room(steve_coord).settype_startroom()
        self.steve_pos = steve_coord

        # choose position of Monster room opposite to where steve is
        boss_x = LABSIZE - 1 - (steve_coord.x % LABSIZE)
        boss_y = LABSIZE - 1 - (steve_coord.y % LABSIZE)
        boss_coord = Coord(boss_x, boss_y)
        self.boss_pos = boss_coord
        if boss_coord.is_same(
                steve_coord):  # if they happen to be placed in the same room
            raise ValueError(
                "Steve and the Boss have been put at the same location.")

    def _generate_maze(self, startroom_pos: Coord) -> None:
        """Links up all rooms in a maze-like fashion"""
        # link up a "large" number of rooms
        print("Loading: Generating maze...")
        self._generate_recursive_linking(startroom_pos)
        unconnected = self._generate_count_unconnected_rooms()
        print("Loading: Tying loose ends...")
        # linearly search through the grid to find unconnected rooms, and connects them.
        # Stops when all are connected.
        while unconnected != 0:
            for x in range(LABSIZE):
                for y in range(LABSIZE):
                    coord = Coord(x, y)
                    room = self.get_room(coord)
                    if not room.is_connected_tostart:
                        self._generate_force_connect(coord)
            unconnected = self._generate_count_unconnected_rooms()

    def _generate_force_connect(self, roomcoords: Coord) -> None:
        """links holes in connectivity of maze to as many adjacent rooms as possible.
        Game design: Does so in an unpredictable (random) sequence, so that this
        has a lower chance of being exploitable by the player.
        """
        newdirlist = list(cardinal.values())
        random.shuffle(newdirlist)
        for i in range(4):
            neighbourcoords = roomcoords.add(newdirlist[i])
            if valid_coords(neighbourcoords):
                self._generate_link_rooms(
                    roomcoords, neighbourcoords)  # forcing a connection.

    def _generate_is_linkable_by_recursive(self, roomcoords: Coord) -> bool:
        """Rules for a this room with coordinates roomcoords to be linked to its
        neighbour that is attempting to link to this:
        
        1. It must have valid coords, within the appropriate range from 0 to LABSIZE - 1
        2. It must not already be connected to the start.
        """
        if not valid_coords(roomcoords):
            return False
        room_object = self.get_room(roomcoords)
        if room_object.is_connected_tostart:  # has access
            return False
        return True

    def _generate_recursive_linking(self, thisroomcoords: Coord) -> None:
        """
        Attempts to link a large number of rooms, recursively
        Rules for whether a neighbour room is linkable:
        0. The room exists (has coordinates within the valid range)
        1. The room is not already linked.

        thisroom will make an attempt to link to linkable neighbour rooms.
        The success of the attempt is based on chance.
        This chance can be changed, but is hardcoded.
        This chance should be quite high above 25%; the lower the odds,
        the more holes in connectivity, the more cleanup linking has to be done.
        
        """
        # current room should already be connected
        thisroom = self.get_room(thisroomcoords)  # object thisroom object
        if not thisroom.is_connected_tostart:
            raise ValueError(
                "Room that is trying to (recursively) link to others is not yet connected, should not happen."
            )
        # iteration through N, S, E, W:
        # checking whether they are linkable by rules
        # if linkable, there is a chance of linking
        for direction in cardinal.values():
            neighbourcoords = thisroomcoords.add(direction)
            if self._generate_is_linkable_by_recursive(neighbourcoords):
                odds = random.randint(1, 100)
                if odds <= 58:  # n% chance of linking;
                    self._generate_link_rooms(thisroomcoords, neighbourcoords)
                    self._generate_recursive_linking(
                        neighbourcoords)  # recursion call
        # base case should be inherently built into this loop:
        # Recursion branch ends at a room where
        # 1. All adjacent rooms are not linkable
        # 2. By chance, the labyrinth chooses not to link this room to any other room.

    def _generate_link_rooms(self, room1coords: Coord,
                             room2coords: Coord) -> None:
        # validation
        if not valid_coords(room1coords) or not valid_coords(room2coords):
            raise IndexError(
                "_generate_link_rooms(): a room passed in has coords outside of labyrinth. Cannot be linked."
            )
        if room1coords.is_same(room2coords):
            raise IndexError(
                "_generate_link_rooms(): the same room is passed twice, cannot be linked."
            )
        if not room1coords.is_adjacent(room2coords):
            raise IndexError(
                "_generate_link_rooms(): non adjacent rooms are passed, cannot be linked."
            )
        # linking rooms
        room1 = self.get_room(room1coords)
        room2 = self.get_room(room2coords)
        if room1.is_connected_tostart or room2.is_connected_tostart:
            room1.is_connected_tostart = True
            room2.is_connected_tostart = True
        if not room1.is_connected_tostart and not room2.is_connected_tostart:
            # every linking must happen between rooms of which 1 MUST be connected.
            return None  # no linking done if both are unconnected.
        # print(room1.coords) #xyzxyz
        # print(room2.coords) #xyzxyz
        room1.connect_to(room2)
        room2.connect_to(room1)

    def _generate_count_unconnected_rooms(self) -> int:
        """
        One of many helper methods of the generate() method.
        
        Linearly search the rooms to check whether the rooms are connected to the
        startroom.
        Returns the number of rooms that are not connected.
        
        """
        number_of_unconnected = 0
        for column in self.lab:
            for room in column:
                # room is an instance of the Room class
                if not room.is_connected_tostart:
                    number_of_unconnected += 1  # counter
        return number_of_unconnected

 
class LabyrinthManager:
    """
    -- ATTRIBUTES --
    - lab: list[list[Room]]
    - difficulty_level
    - boss_pos: Coord
    - steve_pos: Coord
    - posscoords: list[int]

    -- METHODS --
    + get_room() -> Room
    + set_room(Room) -> None
    + layout() -> str
    + get_current_pos() -> Coord
    + move_boss(self) -> None
    + move_steve(self) -> None
    + can_move_here() -> bool
   """

    def __init__(self, labyrinth: list[list["Room"]]):
        self.lab = labyrinth
        self.difficulty_level = None
        self.boss_pos = Coord(9, 9)  # Decided upon generation
        self.steve_pos = Coord(0, 0)  # Decided upon generation
        self.posscoords = list(range(LABSIZE))

    def get_room(self, coord: Coord) -> "Room":
        """Returns the room at the given coordinates"""
        return self.lab[coord.x][coord.y]

    def set_room(self, coord: Coord, room: "Room") -> None:
        """Returns the room at the given coordinates"""
        self.lab[coord.x][coord.y] = room

    def layout(self) -> str:
        outputstr = ""
        for y in range(LABSIZE):
            fulltopstr = ""
            fullmidstr = ""
            fullbottomstr = ""
            for x in range(LABSIZE):
                room = self.get_room(Coord(x, LABSIZE - y - 1))
                N, S, E, W = room.get_neighbours()
                if N:
                    topstr = " || "
                else:
                    topstr = "    "
                if S:
                    bottomstr = " || "
                else:
                    bottomstr = "    "
                if W:
                    midstr = "="
                else:
                    midstr = " "
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
        if not self.can_move_here(self.steve_pos, direction):
            raise ValueError(
                "move_steve() attempted to move steve to a direction that is not possible."
            )
        self.steve_pos = self.steve_pos.add(direction)

    def can_move_here(self, this_coords: Coord, direction: Coord) -> bool:
        """Tells whether an adjacent room is accessible.
        Rules:
        1. There is no wall between this room and the neighbour.
        2. the coordinates are within the range of valid coordinates.
        """
        if not valid_coords(this_coords):  # this should not happen at all
            raise IndexError("entity is not inside of maze")
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
        if displacement.is_zero(
        ):  # They are in the same room, a clue doesn't need to be given LOL
            return None
        i = random.randint(0, 100)
        if i <= 20:
            i = random.randint(0, 2)
            if i == 0:
                print("The warmth of the torch comforts you.")
            elif i == 1:
                print(
                    "There was dead silence, so silent you hear your heart tremble."
                )
            else:
                print(
                    "A silent whine was heard in the distance. It might just be any creature out there."
                )
            return None
        r, dirstr = self._r_dir_calc(displacement)
        if r < 3:
            i = random.randint(0, 2)
            if i == 0:
                print(
                    "The torches suddenly blew out without wind, leaving you in darkness. A series of intense heartbeats echoed, sending chills down to your spine. The torhces were then relit slowly, perhaps magically."
                )
            else:
                print(
                    "A blood-curdling roar seemed to shake the entire room with it. You flinched with no control over your body."
                )
            print("You must be close to the king warden.")
        elif r < 6:
            i = random.randint(1, 100)
            if i == 1:
                print("You hear a rawr.")
                print("Easter egg achieved!")
            else:
                print(
                    "A hair-raising, wrathful whine from afar stuns you, shattering the stillness of cold air."
                )
        elif r < 10:
            print("Distant but colossal footsteps were heard.")
        else:
            print("Hardly audible footsteps were heard.")
        print(f"The sound seemed to come from {dirstr}.")

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
        if dirstr is None:
            raise RuntimeError(
                "Person who implemented _r_dir_calc() has a skill issue")
        return r, dirstr

    def _sb_xy_distance(self) -> Coord:
        """returns x, y displacement of boss from steve."""
        return self.steve_pos.direction_of(self.boss_pos)


class Room:
    """
    -- ATTRIBUTES --
    + coord: Coord
    + type: dict
    + connected: bool
    - connected_rooms: dict
    
    -- METHODS --
    + get_direction(direction: str) -> Room
    + set_direction(direction: str, room: Room) -> None
    + settype_startroom(self) -> None
    + steve_leaves(self) -> None
    + steve_enters -> None
    + steve_leaves -> None
    + steve_enters -> None

    
    """

    def __init__(self, coord: Coord):
        self.coord = coord
        self.cleared = False
        self.type = {"startroom?": False, "steve?": False, "boss?": False}
        self.is_connected_tostart = False
        self.creature = None
        self.item = None
        # setting mynorth, mysouth, myeast, mywest status attributes where possible
        self.connected_rooms: "dict[str, Room | None]" = {
            dir_name: None
            for dir_name, dir_coord in cardinal.items()
        }
        # self.mynorth = None
        # self.mysouth = None
        # self.myeast = None
        # self.mywest = None

    def get_coord(self) -> Coord:
        return self.coord

    def connect_dir(self, direction: Coord, room: "Room") -> None:
        """Connect the given room in the given direction."""
        if not isinstance(room, Room):
            print(self.coord, room.coords)
            raise ValueError(
                f"room variable {room} passed is not a room")
        if not self.coord.is_adjacent(room.coord):
            print(self.coord, room.coord)
            raise RuntimeError(
                "room variable passed is not an adjacent room")

        # makes assumptions that {direction} of this room is neighbour.
        if direction.is_same(cardinal["NORTH"]):
            self.set_direction("NORTH", room)
        elif direction.is_same(cardinal["SOUTH"]):
            self.set_direction("SOUTH", room)
        elif direction.is_same(cardinal["EAST"]):
            self.set_direction("EAST", room)
        elif direction.is_same(cardinal["WEST"]):
            self.set_direction("WEST", room)
        else:
            raise ValueError("Direction passed is not of the right value")

    def get_creature(self) -> "Creature":
        """Getter method for creature attribute"""
        return self.creature

    def get_item(self) -> "Item":
        """Getter method for item attribute"""
        return self.item

    def set_creature(self, creature: "Creature") -> None:
        """setter method for creature; might not need it"""
        if self.creature is not None:
            return None
        self.creature = creature
        return None

    def set_item(self, item: "Item") -> None:
        if self.item is not None:
            return None
        self.item = item

    def get_direction(self, dir_name: str) -> "Room | None":
        if dir_name in cardinal:
            return self.connected_rooms[dir_name]
        raise ValueError(f"{dir_name!r}: invalid direction")

    def set_direction(self, dir_name: str, room: "Room") -> None:
        assert isinstance(room, Room)
        if dir_name in cardinal:
            self.connected_rooms[dir_name] = room
            return
        raise ValueError(f"{dir_name!r}: invalid direction")

    def connect_to(self, room: "Room") -> None:
        """Determines the direction of room relative to this room.
        If given room is adjacent, connect it to this one.
        Otherwise, raise ValueError.
        """
        if not self.coord.is_adjacent(room.get_coord()):
            raise ValueError(
                f"connect_to(), room {room.get_coord()} is not adjacent to this room {self.coord}"
            )
        diff = self.coord.direction_of(room.get_coord())
        if diff == cardinal["NORTH"]:
            if not self.get_direction("NORTH"):
                raise ValueError(
                    f'Room {self.coord} has no room to the north of it, access cannot be set.'
                )
            self.set_direction("NORTH", room)
        elif diff == cardinal["SOUTH"]:
            if not self.get_direction("SOUTH"):
                raise ValueError(
                    f'Room {self.coord} has no room to the south of it, access cannot be set.'
                )
            self.set_direction("SOUTH", room)
        elif diff == cardinal["EAST"]:
            if not self.get_direction("EAST"):
                raise ValueError(
                    f'Room {self.coord} has no room to the east of it, access cannot be set.'
                )
            self.set_direction("EAST", room)
        elif diff == cardinal["WEST"]:
            if not self.get_direction("WEST"):
                raise ValueError(
                    f'Room {self.coord} has no room to the west of it, access cannot be set.'
                )
            self.set_direction("WEST", room)
        else:
            raise ValueError(
                f"{self!r} and {room!r} should be adjacent but are not"
            )

    def get_neighbours(
        self
    ) -> "list[Room | None]":  # corresponding to N, S, E, W
        """Return a list of rooms in each of the N, S, E, W directions."""
        return list(self.connected_rooms.values())

    def dir_is_accessible(self, direction: Coord) -> bool:
        """Returns True if a room exists in the given direction,
        otherwise False.
        """
        assert isinstance(direction, Coord)
        if direction not in cardinal.values():
            return False
        for dir_name, dir_coord in cardinal.items():
            if direction == dir_coord:
                return bool(self.get_direction(dir_name))
        raise ValueError(
            "argument passed into dir_is_accessible() should be a direction value."
        )



FOODITEM = "FOODITEM"
WEAPONITEM = "WEAPONITEM"
ARMOURITEM = "ARMOURITEM"
UTILITYITEM = "UTILITYITEM"


class Item:
    """
    -- ATTRIBUTES --
    
    -- METHODS --
    """

    def __init__(self, name, item_type):
        self.name = name
        self.item_type = item_type

    def __str__(self) -> str:
        outputstr = f"Name: {self.name}\nType: {self.item_type}"
        return outputstr


class Food(Item):

    def __init__(self, name, item_type, hprestore):
        super().__init__(name, item_type)
        self.hprestore = hprestore

    def __str__(self):
        return super().__str__() + f"\nRestores: {self.hprestore} HP"

    def get_restore(self):
        return self.hprestore


class Armor(Item):

    def __init__(self, name, item_type, defence, armor_slot):
        super().__init__(name, item_type)
        self.defence = defence
        self.armor_slot = armor_slot

    def __str__(self):
        return super().__str__() + f"\nProvides: {self.defence} defence"

    def get_defence(self):
        return self.defence


class Weapon(Item):

    def __init__(self, name, item_type, attack):
        super().__init__(name, item_type)
        self.attack = attack

    def __str__(self):
        return super().__str__() + f"\nDoes: {self.attack} damage"

    def get_attack(self):
        return self.attack


DEFAULT_HITPOINTS = 50


class Steve:
    """
    -- ATTRIBUTES --
    
    -- METHODS --
    """

    def __init__(self):
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
        if self._inventory == []:
            print("You have no items in your inventory.\n")
            return None
        print("\nYou have:\n")
        for i in range(len(self._inventory)):
            dict_ = self._inventory[i]
            item, number = str(dict_["item"]), str(dict_["number"])
            prefix = i + 1
            print(f"{prefix:>2}. {number:>2} x {item}")
        print("\n")
        return None

    def _add_item_to_inv(self, new_item: "Item", num: int) -> None:
        for index, dict_ in enumerate(
                self._inventory):  # Linear search through inventory
            if str(new_item) == str(
                    dict_["item"]):  # new_item is already in the inventory
                self._inventory[index]["number"] += num
                return None
        # If exit loop, inventory does not have any of new_item
        # create a dict to add to self.inventory
        self._inventory.append({"item": new_item, "number": num})
        return None

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
        if foodindex < 0:
            raise RuntimeError(
                f"{fooditem} cannot be consumed as Steve's inventory does not have it."
            )
        if not fooditem.item_type == "Food":
            raise ValueError(
                f"{fooditem} cannot be consumed as it is not food.")
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
        if index not in list(range(len(self._inventory))):
            raise ValueError(
                "Item that is trying to be removed from inventory has an index outside of the range of Steve's inventory."
            )
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
            print(
                f"You were healed by {self.health - prevhp} HP and now have {self.health}."
            )
            return None
        self.health = max(self.health + change, 0)
        print(
            f"You got hurt by {prevhp - self.health} HP and have {self.health} left."
        )
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

    def _generate_maxhp(self, maxhp: int, turn_number: int) -> None:
        maxhp = int(
            (maxhp * ((turn_number / 10) + 1) * random.randint(90, 110) / 100))
        return maxhp

    def get_name(self) -> None:
        """Returns the name of the creature"""
        return self.name

    def _generate_attack(self, attack: int, turn_number: int) -> None:
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

    def _generate_attack(self, attack: int, turn_number: int):
        random_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        print(
            "AHHHHHHH A CREEPER HAS APPEARED!!!! RUN AWAY QUICK BY\n PRESSING THE FOLLOWING LETTER:"
        )
        time.sleep(2)
        start_time = time.time()
        inp = input("ENTER THE LETTER " + random_letter + " QUICK: ")
        print("KABOOOOOMMMMM THE CREEPER EXPLODEDDDDD!!!!!!")
        self.hitpoints = 0
        if inp.upper() == random_letter and time.time() - start_time <= 1.8:
            print(
                "\nLuckily, your quick reactions allowed you to avoid the explosion. You took no damage."
            )
            return None
        elif inp.upper() != random_letter:
            print(
                "\nOh no! You took the wrong action and got caught in the blast!"
            )
        elif (time.time() - start_time) > 1.8:
            print("\nOh no! You were too slow and got caught in the blast!")
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
        return Armor(item_data["name"], item_type, item_data["defence"],
                     item_data["slot"])
    elif item_type == "Food":
        item_data = random.choice(food_list)
        return Food(item_data["name"], item_type, item_data["hprestore"])
    elif item_type == "Weapon":
        item_data = random.choice(weapon_list)
        return Weapon(item_data["name"], item_type, item_data["atk"])


with open("content/creatures.json", 'r', encoding='utf-8') as f:
    creature_list = json.load(f)
with open("content/items/armor.json", 'r', encoding='utf-8') as f:
    armor_list = json.load(f)
with open("content/items/food.json", 'r', encoding='utf-8') as f:
    food_list = json.load(f)
with open("content/items/weapon.json", 'r', encoding='utf-8') as f:
    weapon_list = json.load(f)
turn = 1
