import random

from maze import cardinal, Coord, opposite, Maze, Room


class LabyrinthGenerator:
    """Base class for all labyrinth generators.

    -- ATTRIBUTES --
    - maze: Maze
    
    -- METHODS --
    + generate(self) -> None
    + get_maze(self) -> Maze
    """
    def __init__(self, x_size: int, y_size: int):
        self.maze = Maze(x_size, y_size)

    def generate(self) -> None:
        """Execute the maze generation.
        No return is required.
        """
        raise NotImplementedError

    def get_maze(self) -> Maze:
        return self.maze


class Random(LabyrinthGenerator):
    """Generates a labyrinth for the game.
    
    -- ATTRIBUTES --
    - maze: Maze
    
    -- METHODS --
    + generate(self) -> None
    + get_maze(self) -> Maze
    - generate_place_steve_boss() -> None:
    - generate_link_rooms(room1coords: list, room2coords: list) -> None:
    - generate_rooms_connected() -> bool:
    """

    def generate(self) -> None:
        """Helper method for the generate() method.
        Makes sure all rooms are connected to all adjacent rooms 
        in the labyrinth.
        """
        for x in range(self.maze.x_size):
            for y in range(self.maze.y_size):
                here = Coord(x, y)
                for direction in cardinal:
                    there = here.add(cardinal[direction])
                    if self.maze.valid_coords(there):
                        this = self.maze.get(here)
                        that = self.maze.get(there)
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
        for x in range(self.maze.x_size):
            for y in range(self.maze.y_size):
                coord = Coord(x, y)
                self.maze.set(coord, Room(coord))
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
        - This means that size cannot be too small, or the generation may break.
          ie size cannot be less than 4.

        How bossroom is chosen:
        - e.g. size is set to 10 and startroom coords are [1, 7]
        - bossroom is at the opposite of the labyrinth at [8, 2]

        Startroom will be remembered throughout the game, the starting position
        of the boss will not be remembered. 
        """
        # choose position of Start room randomly
        n = self.maze.x_size // 4
        n = random.randint(-n, n - 1) % self.maze.x_size
        m = random.randint(0, self.maze.x_size - 1)
        nm = [n, m]
        random.shuffle(nm)
        steve_coord = Coord(nm[0], nm[1])
        self.steve_pos = steve_coord

        # choose position of Monster room opposite to where steve is
        boss_x = self.maze.x_size - 1 - (steve_coord.x % self.maze.x_size)
        boss_y = self.maze.y_size - 1 - (steve_coord.y % self.maze.y_size)
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
            for x in range(self.maze.x_size):
                for y in range(self.maze.y_size):
                    coord = Coord(x, y)
                    room = self.maze.get(coord)
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
            if self.maze.valid_coords(neighbourcoords):
                self._generate_link_rooms(
                    roomcoords, neighbourcoords)  # forcing a connection.

    def _generate_is_linkable_by_recursive(self, roomcoords: Coord) -> bool:
        """Rules for a this room with coordinates roomcoords to be linked to its
        neighbour that is attempting to link to this:
        
        1. It must have valid coords, within the appropriate range from 0 to self.maze.x_size - 1
        2. It must not already be connected to the start.
        """
        if not self.maze.valid_coords(roomcoords):
            return False
        room_object = self.maze.get(roomcoords)
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
        thisroom = self.maze.get(thisroomcoords)  # object thisroom object
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
        assert self.maze.valid_coords(room1coords) and self.maze.valid_coords(room2coords)
        assert not room1coords.is_same(room2coords)
        assert room1coords.is_adjacent(room2coords)
        # linking rooms
        room1 = self.maze.get(room1coords)
        room2 = self.maze.get(room2coords)
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
        for column in self.maze.lab:
            for room in column:
                # room is an instance of the Room class
                if not room.is_connected_tostart:
                    number_of_unconnected += 1  # counter
        return number_of_unconnected


class RecursiveBacktrace(LabyrinthGenerator):
    """Implements recursive backtracing for maze generation.

    This strategy keeps track of visited rooms.
    1. Generate all rooms with walls
    2. Visit a random unvisited neighbour and carve through the adjoining wall
    3. Repeat until it is not possible to proceed.
    4. Go back to the last room with unvisited neighbours and repeat.

    Reference: http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking
    """
    def __init__(self, x_size: int, y_size: int):
        super().__init__(x_size, y_size)
        self.visited = []
        
    def generate(self) -> None:
        # Start in top row
        coord = Coord(random.randint(0, self.maze.y_size - 1), 0)
        room = self.maze.get(coord)
        assert isinstance(room, Room)
        self.explore(room)

    def visit(self, coord: Coord) -> None:
        assert isinstance(coord, Coord)
        assert coord not in self.visited
        self.visited.append(coord)

    def dig(self, room: Room, direction: str) -> None:
        """'Dig' through a wall in the given direction
        to join room to the next room.
        """
        new_coord = room.coord.add(cardinal[direction])
        new_room = self.maze.get(new_coord)
        assert new_room.get_direction(opposite(direction)).is_wall()
        room.set_direction(direction, new_room)
        new_room.set_direction(opposite(direction), room)

    def explore(self, room: Room) -> None:
        """Recursively explore the maze, digging through 
        walls to unexplored rooms.
        """
        self.visit(room.coord)
        choices = list(cardinal.items())
        random.shuffle(choices)
        while choices:
            # Skip visited neighbours and boundaries
            direction, change = choices.pop()
            side = room.get_direction(direction)
            if side.is_boundary():
                continue
            new_coord = room.coord.add(change)
            assert new_coord.x >= 0 and new_coord.y >= 0, f"{room.coord}: {direction} should be a boundary"
            if new_coord in self.visited:
                continue
            # Any rooms found should have been visited
            # and therefore skipped earlier
            assert not side.is_room(), (
                f"At {room.coord}: {new_coord}"
                " has a room that is not visited"
            )
            # Side is wall, new_coord is unvisited
            self.dig(room, direction)
            self.explore(self.maze.get(new_coord))
    