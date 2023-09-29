"""location.py

This module contains classes and functions used to manage
locations in the game.
"""


class Coord:
    """Encapsulates a pair of 2D coordinates.
    Coordinates are represented as (x, y), with x and y being ints.
    """

    def __init__(self, x: int, y: int) -> None:
        assert isinstance(x, int)
        assert isinstance(y, int)
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

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


class Side:
    """Superclass representing what player might encounter for each side of a room.

    Methods
    -------
    + is_boundary() -> bool
    + is_room() -> bool
    + is_wall() -> bool
    """

    def is_boundary(self) -> bool:
        raise NotImplementedError

    def is_room(self) -> bool:
        raise NotImplementedError

    def is_wall(self) -> bool:
        raise NotImplementedError


class Boundary(Side):
    """Represents the edges of the maze.
    There is no room on the other side.
    """

    def is_boundary(self) -> bool:
        return True

    def is_room(self) -> bool:
        return False

    def is_wall(self) -> bool:
        return False


class Wall(Side):
    """Represents a wall, with a room on the other side.
    This room cannot be accessed through normal means.
    """

    def is_boundary(self) -> bool:
        return False

    def is_room(self) -> bool:
        return False

    def is_wall(self) -> bool:
        return True


class Room(Side):
    """
    -- ATTRIBUTES --
    + coord: Coord
    + type: dict
    + connected: bool
    - connected_rooms: dict
    
    -- METHODS --
    + get_direction(direction: str) -> Room
    + set_direction(direction: str, room: Room) -> None
    """

    def __init__(self, coord: Coord):
        self.coord = coord
        self.cleared = False
        self.type = {"startroom?": False, "steve?": False, "boss?": False}
        self.is_connected_tostart = False
        self.creature = None
        self.item = None
        self.connected_rooms: dict[str, Side] = {
            dir_name: Wall()
            for dir_name, dir_coord in cardinal.items()
        }

    def is_boundary(self) -> bool:
        return False

    def is_room(self) -> bool:
        return True

    def is_wall(self) -> bool:
        return False

    def get_coord(self) -> Coord:
        return self.coord

    def connect_to(self, direction: str, room: "Room") -> None:
        """Connect the given room in the given direction.
        The given room must be validated for adjacency before calling this method.
        """
        # We use quick-and-dirty validation for errors we do not expect
        # such as those due to programmer error
        # When validating user input or other errors which might be caused by the user,
        # We give more detailed error messages to aid in handling the error.
        assert isinstance(room, Room)
        assert self.coord.is_adjacent(room.coord)
        assert direction in cardinal
        # makes assumptions that {direction} of this room is neighbour.
        self.set_direction(direction, room)

    def get_direction(self, dir_name: str) -> Side:
        assert dir_name in cardinal, f"{dir_name!r}: invalid direction"
        return self.connected_rooms[dir_name]

    def set_direction(self, dir_name: str, side: Side) -> None:
        assert isinstance(side, Side)
        assert dir_name in cardinal, f"{dir_name!r}: invalid direction"
        self.connected_rooms[dir_name] = side

    def get_neighbours(self) -> list[Side]:
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
        return False


cardinal = {
    "NORTH": Coord(0, -1),
    "SOUTH": Coord(0, 1),
    "EAST": Coord(1, 0),
    "WEST": Coord(-1, 0)
}


def opposite(direction: str) -> str:
    if direction == "NORTH":
        return "SOUTH"
    if direction == "SOUTH":
        return "NORTH"
    if direction == "EAST":
        return "WEST"
    if direction == "WEST":
        return "EAST"
    raise AssertionError


def roomgrid(x_size: int, y_size: int) -> list[list[Side]]:
    """Generate a grid of rooms with dimensions x-by-y"""
    boundary = Boundary()
    wall = Wall()
    grid = []
    for x in range(x_size):
        grid.append([])
        for y in range(y_size):
            grid[x].append(Room(Coord(x, y)))
    # Set boundaries
    for x in range(x_size):
        grid[x][0].set_direction("NORTH", boundary)
        grid[x][y_size - 1].set_direction("SOUTH", boundary)
    for y in range(y_size):
        grid[0][y].set_direction("WEST", boundary)
        grid[x_size - 1][y].set_direction("EAST", boundary)
    return grid


class Maze:
    """Encapsulates data for a maze layout.

    Attributes
    ----------
    + x_size: int
    + y_size: int
    - lab: list[list[Room]]

    Methods
    -------
    + get(coord: Coord) -> Room
    + set(coord: Coord, room: Room) -> None
    + valid_coords(coord: Coord) -> bool
    """

    def __init__(self, x_size: int, y_size: int) -> None:
        assert x_size > 1
        assert y_size > 1
        self.x_size = x_size
        self.y_size = y_size
        self.lab = roomgrid(x_size, y_size)

    def __repr__(self) -> str:
        return f"Maze(x_size={self.x_size}, y_size={self.y_size})"

    def valid_coords(self, coord: Coord) -> bool:
        """Check if the given coord is valid within the maze"""
        if not (0 <= coord.x < self.x_size):
            return False
        if not (0 <= coord.y < self.y_size):
            return False
        return True

    def get(self, coord: Coord) -> "Room":
        """Returns the room at the given coordinates"""
        return self.lab[coord.x][coord.y]

    def set(self, coord: Coord, room: "Room") -> None:
        """Returns the room at the given coordinates"""
        assert isinstance(room, Room)
        self.lab[coord.x][coord.y] = room
