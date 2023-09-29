#File containing the code for the game
import math
import random
from typing import Any

import action
import character
import create
import data
import text
from generator import Random
from maze import cardinal, Coord, Maze, Room


BOSS = "King Warden"


NORTH = "NORTH"
SOUTH = "SOUTH"
EAST = "EAST"
WEST = "WEST"


LABSIZE = 10


PI = 3.14159265359


def prompt_valid_choice(options: list[Any],
                        question: str,
                        errormsg: str) -> Any:
    """Prompt the user for a valid choice from enumerated options.
    Return the option corresponding to the choice.
    """
    for i, option in enumerate(options, start=1):
        print(f"{i}: {str(option)}")
    while True:
        choice = input(question + ": ")
        if not choice.isdecimal():
            print(errormsg)
        elif not 0 < int(choice) <= len(options):
            print(errormsg)
    return options[int(choice) - 1]
    

class LabyrinthManager:
    """This class encapsulates access to the labyrinth grid
    -- ATTRIBUTES --
    - lab: list[list[Room]]

    -- METHODS --
    + can_move_here() -> bool
    + get_room() -> Room
    + set_room(Room) -> None
   """

    def __init__(self, labyrinth: Maze):
        self.lab = labyrinth
        self.boss_pos = Coord(9, 9)  # Decided upon generation
        self.steve_pos = Coord(0, 0)  # Decided upon generation

    def can_move_here(self, this_coords: Coord, direction: Coord) -> bool:
        """Tells whether an adjacent room is accessible.
        Rules:
        1. There is no wall between this room and the neighbour.
        2. the coordinates are within the range of valid coordinates.
        """
        assert self.lab.valid_coords(this_coords)
        thisroom = self.get_room(this_coords)
        return thisroom.dir_is_accessible(direction)

    def get_room(self, coord: Coord) -> "Room":
        """Returns the room at the given coordinates.
        Result is assumed to be a valid room; do any required validation checks first.
        """
        room = self.lab.get(coord)
        assert isinstance(room, Room)
        return room

    def set_room(self, coord: Coord, room: "Room") -> None:
        """Returns the room at the given coordinates"""
        self.lab.set(coord, room)

    def _give_sound_clue(self):
        """Displays a message giving a hint how far away the boss is from steve
        and which direction steve might have to go in order to find the boss.
        
        Calculates straight line distance.
        Calculates which direction, N, S, E, W, NE, NW, SE, SW
        displays a message based on distance and direction.
        """
        displacement = self.steve_pos.direction_of(self.boss_pos)
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

    def _r_dir_calc(self, coord1: Coord, coord2: Coord) -> tuple[float, str]:
        """maths work for _give_sound_clue
        Determines the distance (r: float) and direction (:str) from
        coord1 (origin) to coord2 (destination).
        Returns r and direction
        """
        direction = self.steve_pos.direction_of(self.boss_pos)
        if direction.is_zero():
            return (0, "NONE")
        r = direction.length()
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


class MUDGame:
    """This class encapsulates data for the main game implementation.

    -- ATTRIBUTES --
    - maze: Maze
    - boss_pos: Coord
    - steve_pos: Coord

    -- METHODS --
    + current_coord() -> Coord
    + current_room() -> Room
    + layout() -> str
    + move_boss(self) -> None
    + move_steve(self) -> None
    """

    def __init__(self) -> None:
        self.gameover = False  # default
        self.won = False  # default
        generator = Random(x_size=LABSIZE, y_size=LABSIZE)
        generator.generate()
        labyrinth = generator.get_maze()
        self.maze = LabyrinthManager(labyrinth)
        self.steve = create.steve()
        self.visited = []
        self.boss = create.creature_from_name(BOSS)
        self.boss_pos = Coord(9, 9)
        self.steve_pos = Coord(0, 0)

    def current_coord(self) -> Coord:
        return self.steve_pos

    def current_room(self) -> Room:
        return self.maze.get_room(self.steve_pos)

    def prompt_username(self) -> str:
        """Prompt the player for username"""
        while True:
            username = input(text.username_prompt).strip()
            if username == "":
                print(text.username_error)
            else:
                return username

    def layout(self) -> str:
        outputstr = ""
        for y in range(self.maze.lab.y_size):
            fulltopstr = ""
            fullmidstr = ""
            fullbottomstr = ""
            for x in range(self.maze.lab.x_size):
                room = self.maze.get_room(Coord(x, self.maze.lab.y_size - y - 1))
                N, S, E, W = room.get_neighbours()
                topstr = " || " if N else "    "
                bottomstr = " || " if S else "    "
                midstr = "=" if W else " "
                if room.coord == self.steve_pos:
                    midstr += "S"
                else:
                    midstr += "/"
                if room.coord == self.boss_pos:
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

    def move_boss(self) -> None:
        """Tries to move the boss from its current room to any (available) 
        neighbour rooms.
        
        Does not jump over walls.
        If the boss cannot move in any of the 4 cardinal directions, an error is raised
        as it implies that the room it is in is completely isolated, which should not
        happen.
        """
        directions = list(cardinal.values())
        random.shuffle(directions)
        for direction in directions:
            if self.maze.can_move_here(self.boss_pos, direction):
                self.boss_pos = self.boss_pos.add(direction)
                return None
        raise RuntimeError(
            f"No movement direction available to Boss at {self.boss_pos}."
        )

    def move_steve(self, direction: str) -> None:
        """Move Steve in the specified direction.
        The direction is assumed to have been validated.
        """
        self.steve_pos = self.steve_pos.add(cardinal[direction])

    def game_is_over(self) -> bool:
        """
        Returns True if either Steve or Boss is dead.
        """
        return self.steve.isdead() or self.boss.isdead()

    def prompt_encounter(self) -> action.Action:
        choice = prompt_valid_choice(
            [action.EnterBattle, action.RunAway],
            text.option_prompt,
            text.option_invalid
        )
        return choice()

    def prompt_pickup_item(self, item: str) -> action.Action:
        choice = prompt_valid_choice(
            [action.PickUp, action.DoNothing],
            text.option_prompt,
            text.option_invalid
        )
        return choice(item)

    def prompt_restart(self) -> str:
        return prompt_valid_choice(
            ["Yes", "No"],
            text.option_prompt,
            text.option_invalid
        )

    def prompt_battle_choice(self, steve: character.Steve) -> action.Action:
        food_items = [
            slot.item
            for slot in steve.get_food_items()
        ]
        if not food_items:
            return action.Attack(steve.get_attack())
        choice = prompt_valid_choice(
            [action.Attack, action.Eat],
            text.option_prompt,
            text.option_invalid
        )
        if isinstance(choice, action.Attack):
            return action.Attack(steve.get_attack())
        elif isinstance(choice, action.Eat):
            print("\nYou have:\n")
            food = prompt_valid_choice(
                food_items,
                text.heal_prompt,
                text.option_invalid
            )
            return action.Eat(food.name)
        else:
            raise TypeError(f"{choice!r}: invalid action")

    def enter_battle(self, steve: character.Steve, creature: character.Creature) -> None:
        """
        Battle between Steve and creatures.
        Each takes a turn to deal damage or heal.
        Only boss and steve are able to heal themselves.
        Battle continues until one dies.
        """
        print(f"You have encountered the {creature.name}!")
        while not steve.isdead() and not creature.isdead():
             self.handle_battle_round(steve, creature)
        if creature.isdead():
            self.current_room().creature = None

    def handle_attack(self, aggressor: character.Combatant, defender: character.Combatant, damage: int) -> int:
        defender.take_damage(damage)
        print(text.battle_hp_report(
            defender.name,
            defender.health
        ))
        return damage

    def handle_battle_choice(self,
                             choice: action.Action,
                             actor: character.Combatant,
                             actee: character.Combatant) -> None:
        if isinstance(choice, action.Attack):
            damage = choice.do()
            self.handle_attack(actor, actee, damage)
            print(text.creature_dealdmg(actor.name, damage))
        elif isinstance(choice, action.Heal):
            healing = choice.do()
            print(text.creature_selfheal(actor.name))
            self.handle_heal(actor, healing)
        elif isinstance(choice, action.Eat):
            food = choice.do()
            assert isinstance(actor, character.Steve)
            self.handle_eat(actor, food)
        raise ValueError(f"{choice!r}: invalid battle choice")

    def handle_battle_round(self, steve: character.Steve, creature: character.Creature) -> None:
        """One round of battle consists of Steve making a choice, followed by
        the creature if it is still alive.
        """
        # Steve's turn
        choice = self.prompt_battle_choice(steve)
        self.handle_battle_choice(choice, steve, creature)
        if creature.isdead():
            return
        # Creature's turn
        choice = creature.act()
        self.handle_battle_choice(choice, creature, steve)

    def handle_eat(self, steve: character.Steve, name: str) -> None:
        food = steve.inventory.get(name)
        assert isinstance(food, data.Food)
        steve.consume_item(food)
        self.handle_heal(steve, food.hprestore)

    def handle_escape(self, steve: character.Steve, creature: character. Creature) -> None:
        odds = random.randint(1, 100)
        # Fail to escape
        if odds > 40:
            print(text.escape_failure)
            self.enter_battle(steve, creature)
        # Succeeded in escaping
        current_location = self.current_coord()
        available_dir = []
        for dir_name, dir_coord in cardinal.items():
            if self.maze.can_move_here(current_location, dir_coord):
                  available_dir.append(dir_name)
        random_dir = random.choice(available_dir)
        self.move_steve(random_dir)
        print(text.escape_success)

    def handle_heal(self, combatant: character.Combatant, amt: int) -> None:
        prevhp = combatant.health
        combatant.heal(amt)
        print(text.heal_report(
            combatant.health - prevhp,
            combatant.health
        ))
        print(text.damage_report(
            prevhp - combatant.health,
            combatant.health
        ))
        print(text.heal_success)

    def handle_menu_choice(self, choice: action.Action, steve: character.Steve, creature: character.Creature) -> None:
        if isinstance(choice, action.EnterBattle):
                    self.enter_battle(steve, creature)
        elif isinstance(choice, action.RunAway):
            self.handle_escape(steve, creature)
        elif isinstance(choice, action.PickUp):
            item = choice.do()
            self.steve.take_item(item, 1)
        elif isinstance(choice, action.DoNothing):
            print(text.no_item)

    def prompt_direction(self) -> str:
        """Prompt player for a valid direction to move."""
        current_location = self.current_coord()
        available_dir = []
        for dir_name, dir_coord in cardinal.items():
            if self.maze.can_move_here(current_location, dir_coord):
                available_dir.append(dir_name)
        direction = prompt_valid_choice(available_dir,
                    text.move_prompt,
                    text.option_invalid)
        return direction

    def visit(self, coord: Coord) -> None:
        """Treat the coord as visited"""
        self.visited.append(coord)

    def game_end(self) -> None:
        """Display suitable text at game end"""
        if self.steve.isdead():
            print(text.game_win)
        else:
            print(text.game_lose)
        print(f"Score: {random.randint(0, 10000)}")

    def run(self):
        """Run the game"""
        # starting interface
        username = self.prompt_username()
        print(text.intro(username))

        # Main game loop
        while not self.game_is_over():
            print('\n')
            room = self.current_room()
            self.visit(self.current_coord())
            print(self.steve.status())
            if not room.creature:
                print(text.escape_notrequired)
            else:
                choice = self.prompt_encounter()
                self.handle_menu_choice(choice, self.steve, room.creature)
            if self.game_is_over():
                break
            # Pick up loot
            if not room.item:
                print(text.no_item)
                continue
            if isinstance(room.item, data.Weapon):
                self.steve.equip_weapon(room.item)
                print(text.found_item(
                    "stronger weapon",
                    f'It deals {room.item.get_attack()} damage now!'
                ))
            elif isinstance(room.item, data.Armor):
                self.steve.equip_armor(room.item)
                print(text.found_item(
                    "stronger armor",
                    f'It blocks {item.get_defence()} damage now!'
                ))
            else:
                print(text.found_item(
                    room.item.name,
                    "Do you want to pick it up?"
                ))
                choice = self.prompt_pickup_item(room.item.name)
                self.handle_menu_choice(choice, self.steve, room.creature)

            # Move steve and boss
            direction = self.prompt_direction()
            self.move_steve(direction)
            if random.randint(1, 100) <= 30:
                self.move_boss()

        self.game_end()
