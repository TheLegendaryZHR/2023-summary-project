import random

from location import Coord, Room


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
                here = Coord(x, y)
                for direction in cardinal:
                    there = here.add(cardinal[direction])
                    if valid_coords(there):
                        this = self.get_room(here)
                        that = self.get_room(there)
                        this.connect_to(direction, that)

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
        self.steve_pos = steve_coord

        # choose position of Monster room opposite to where steve is
        boss_x = LABSIZE - 1 - (steve_coord.x % LABSIZE)
        boss_y = LABSIZE - 1 - (steve_coord.y % LABSIZE)
        boss_coord = Coord(boss_x, boss_y)
        self.boss_pos = boss_coord
        assert not boss_coord.is_same(steve_coord)

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
        assert thisroom.is_connected_tostart
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
        assert valid_coords(room1coords) and valid_coords(room2coords)
        assert not room1coords.is_same(room2coords)
        assert room1coords.is_adjacent(room2coords)
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
