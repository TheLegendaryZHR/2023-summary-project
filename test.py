#File for QAE
# for each critical method, test the method (template is test_attack(), think abt what the mtd does/outcome aft method is run) !!!!!

import game
import generator
import maze


def test_lbr_init():
    gen = generator.LabyrinthGenerator(10, 10)
    gen.generate()
    lb = game.LabyrinthManager(gen.get_maze())


# def test_attack():
#     """Check that the attack() method"""
#     mg.attack()
#     assert mg.steve.isdead() or mg.creature.isdead()

# def test_movesteve():
#     befpos = mg.maze.current_coord()
#     mg.movesteve()
#     aftpos = mg.maze.current_coord()
#     if befpos == aftpos:
#         raise RuntimeError("After movesteve() was run, Steve did not move.")


def check_side(labyrinth, coord, direction: str):
    room = labyrinth.get(coord)
    side = room.get_direction(direction)

    # Check boundaries
    if direction == "NORTH" and coord.y == 0:
        assert side.is_boundary(
        ), f"{coord}: {direction} should be boundary, got {side!r}"
    if direction == "SOUTH" and coord.y == labyrinth.y_size - 1:
        assert side.is_boundary(
        ), f"{coord}: {direction} should be boundary, got {side!r}"
    if direction == "WEST" and coord.x == 0:
        assert side.is_boundary(
        ), f"{coord}: {direction} should be boundary, got {side!r}"
    if direction == "EAST" and coord.x == labyrinth.x_size - 1:
        assert side.is_boundary(
        ), f"{coord}: {direction} should be boundary, got {side!r}"

    # Check wall
    elif side.is_wall():
        side_room = labyrinth.get(coord.add(maze.cardinal[direction]))
        assert side_room.is_room()
        self = side_room.get_direction(maze.opposite(direction))
        assert self.is_wall(
        ), f"{coord}: Adjoining room {side.coord}'s {maze.opposite(direction)} should be a wall, got {self!r}"

    # Check room
    elif side.is_room():
        self = side.get_direction(maze.opposite(direction))
        assert self.is_room(
        ), f"{coord}: Adjoining room {side.coord}'s {maze.opposite(direction)} should be a room, got {self!r}"
        assert self.coord == room.coord, f"{coord}: Adjoining room {side.coord}'s {maze.opposite(direction)} should be self, got {self.coord}"


def test_recursivebacktrace():
    mazegen = generator.RecursiveBacktrace(game.LABSIZE, game.LABSIZE)
    mazegen.generate()
    labyrinth = mazegen.get_maze()
    for x in range(0, game.LABSIZE):
        for y in range(0, game.LABSIZE):
            coord = maze.Coord(x, y)
            for direction in maze.cardinal:
                check_side(labyrinth, coord, direction)


# mg.run()
test_recursivebacktrace()
