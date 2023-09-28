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
        self.connected_rooms: "dict[str, Room | None]" = {
            dir_name: None
            for dir_name, dir_coord in cardinal.items()
        }

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

    def get_creature(self) -> "Creature":
        """Getter method for creature attribute"""
        return self.creature

    def get_item(self) -> "Item":
        """Getter method for item attribute"""
        return self.item

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

    def get_neighbours(self) -> "list[Room | None]":
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
    "NORTH": Coord(0, 1),
    "SOUTH": Coord(0, -1),
    "EAST": Coord(0, 1),
    "WEST": Coord(0, -1)
}
