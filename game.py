#File containing the code for the game
import math
import random

import character
import create
import data
import text
from generator import LabyrinthGenerator
from maze import cardinal, Coord, Maze, Room


BOSS = "King Warden"


NORTH = "NORTH"
SOUTH = "SOUTH"
EAST = "EAST"
WEST = "WEST"


LABSIZE = 10


PI = 3.14159265359


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
        """Returns the room at the given coordinates"""
        return self.lab.get(coord)

    def set_room(self, coord: Coord, room: "Room") -> None:
        """Returns the room at the given coordinates"""
        self.lab.set(coord, room)

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
        generator = LabyrinthGenerator(x_size=LABSIZE, y_size=LABSIZE)
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
        return self.maze.get(self.steve_pos)

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

    def move_boss(self) -> None:
        """Tries to move the boss from its current room to any (available) neighbour rooms.
        
        Does not jump over walls.
        If the boss cannot move in any of the 4 cardinal directions, an error is raised as it implies that the room it is in is completely isolated, which should not happen.
        """
        directions = list(cardinal.values())
        random.shuffle(directions)
        for direction in directions:
            if self.maze.can_move_here(self.boss_pos, direction):
                self.boss_pos = self.boss_pos.add(direction)
                return None
        raise RuntimeError(
            f"Boss cannot move because its room {self.boss_pos} is unlinked to neighbours."
        )

    def move_steve(self, direction: Coord) -> None:
        assert self.maze.can_move_here(self.steve_pos, direction)
        self.steve_pos = self.steve_pos.add(direction)

    def game_is_over(self) -> bool:
        """
        Returns True if either Steve or Boss is dead.
        """
        if self.steve.isdead() or self.boss.isdead():  # other conditions
            return True

    def show_options(self, sit: str) -> None:
        """
        Print menu of options provided to users according to different situation.
        """
        if sit == 'creature':
            menu = "1. Attack \n2. Run away"
        elif sit == 'item':
            menu = '1. Pick Up \n2. Do not pick up'
        elif sit == 'restart':
            menu = '1. Yes \n2. No'
        elif sit == 'battle':
            menu = '1. Attack \n2. Heal'
        print(menu)

    def prompt_player(self) -> int:
        """
        Prompt player to choose option 1 or 2.
        Returns 1 or 2.
        """
        opt = input('Please choose option 1 or 2: ')
        while not self.isvalid(opt):
            print('Please enter a valid number(1/2).')
            opt = input('Please choose option 1 or 2: ')
        return opt

    def isvalid(self, opt) -> bool:
        """
        Validate player's choice when given 2 options.
        Returns a Boolean value.
        """
        if opt in '12' and len(opt) == 1:
            return True
        return False

    def battle(self) -> None:
        """
        Battle between Steve and creatures.
        Each takes a turn to deal damage or heal.
        Only boss and steve are able to heal themselves.
        Battle continues until one dies.
        """
        room = self.current_room()
        creature = room.creature
        print(f"You have encountered the {creature.get_name()}!")
        while not self.steve.isdead() and not creature.isdead():
            print(self.steve)  # show HP
            if self.steve.inventory.isempty():
                print(
                    f'You have no heal items! \nAttack the {creature.get_name()}.'
                )
                damage = self.steve.get_attack()
                creature.take_damage(damage)
                print(text.battle_hp_report(creature.get_name(), creature.get_health()))
                if creature.get_health() == 0:
                    continue
            else:
                self.show_options('battle')
                battle_option = self.prompt_player()
                if battle_option == '1':
                    #attack
                    damage = self.steve.get_attack()
                    creature.take_damage(damage)
                    print(text.battle_hp_report(creature.get_name(), creature.get_health()))
                elif battle_option == '2':
                    #heal
                    heal_option = None
                    n = 0
                    while not self.isvalid_heal(heal_option):
                        n += 1
                        if self.steve.inventory.is_empty():
                            print(text.inventory_empty + "\n")
                        else:
                            print("\nYou have:\n")
                            self.steve.display_inventory()
                        if n > 1:
                            self.invalid_opt()
                        heal_option = input(text.heal_prompt)
                        self.isvalid_heal(heal_option)
                    heal_option = int(heal_option) - 1
                    prevhp = self.steve.health
                    self.steve.eat(heal_option)
                    print(text.heal_report(self.steve.health - prevhp, self.steve.health))
                    print(text.damage_report(prevhp - self.steve.health, self.steve.health))
                    print(text.heal_success)
            #Steve endturn
            action = creature.act()
            damage = action.do()
            self.steve.take_damage(damage)
            if damage == 0:
                print(text.creature_selfheal(creature.name))
            else:
                print(text.creature_dealdmg(creature.name, damage))
        if room.creature.isdead():
            room.creature = None

    def isvalid_heal(self, heal_option) -> bool:
        """
        Validate player's option when choosing food items from inventory.
        Used for battle()
        """
        range_of_option = self.steve.inventory.length() + 1
        valid_opt = []
        for i in range(1, range_of_option):
            valid_opt.append(str(i))
        if heal_option in valid_opt:
            return True
        return False

    def show_winscreen(self) -> None:
        """
        Shows winscreen when Boss dies.
        """
        print(text.game_win)

    def show_losescreen(self) -> None:
        """
        Show losescreen when Steve dies."""
        print(text.game_lose)
        print(f"Score: {random.randint(0, 10000)}")

    def movesteve(self) -> None:
        """
        Move Steve to another room when no item or creatures left in the current room.
        """
        current_location = self.maze.current_coord()
        available_dir = []
        dir_provided = ''
        for dir_name, dir_coord in cardinal.items():
            if self.maze.can_move_here(current_location, dir_coord):
                available_dir.append(dir_name)
        for i in range(len(available_dir)):
            dir_provided = dir_provided + str(
                i + 1) + '. ' + available_dir[i] + ' '
        validity = False
        n = 0
        while validity is False:
            n += 1
            if n > 1:
                self.invalid_opt()
            print(text.move_prompt(dir_provided))
            choice = input('Next location: ')
            no_of_choice = len(available_dir)
            valid_choice = ''
            for i in range(no_of_choice):
                valid_choice += str(i + 1)
            if choice in valid_choice and len(choice) == 1:
                validity = True
        choice = int(choice)
        self.maze.move_steve(cardinal[available_dir[choice - 1]])

    def moveboss(self) -> None:
        """
        Move boss to another room.
        """
        self.maze.move_boss()

    def invalid_opt(self) -> None:
        """
        Show error message.
        """
        print(text.option_invalid)

    def visit(self, coord: Coord) -> None:
        """Treat the coord as visited"""
        self.visited.append(coord)

    def run(self):
        """Run the game"""
        # starting interface
        username = self.prompt_username()
        print(text.intro(username))

        # Main game loop
        while not self.game_is_over():
            print('\n')
            self.visit(self.maze.current_coord())
            print(self.steve.status())

            # creature is found in the room
            if self.current_room().creature:

                # show player action options
                self.show_options('creature')

                # prompt player to take actions
                option = self.prompt_player()

                # battle if player choose option 1
                if option == '1':
                    self.battle()
                    if self.game_is_over():
                        continue

                # steve has 40% chance of running away to another room, 60% chance to battle instead
                else:
                    odds = random.randint(1, 100)
                    if odds <= 40:
                        current_location = self.maze.current_coord()
                        available_dir = []
                        for dir_name, dir_coord in cardinal.items():
                            if self.maze.can_move_here(current_location, dir_coord):
                                available_dir.append(dir_name)
                        random_dir = random.choice(available_dir)
                        self.maze.move_steve(cardinal[random_dir])
                        print(text.escape_success)
                        continue
                    else:
                        print(text.escape_failure)
                        self.battle()
                        if self.game_is_over():
                            continue
            else:
                print(text.escape_notrequired)

            # item is found in the room
            # item can be 'Armor', 'Food', 'Weapon'
            # armor and weapon item will be automatically picked up
            # player can choose to pick up food item or not
            if self.current_room().item:
                item = self.current_room().item
                if isinstance(item, data.Weapon):
                    self.steve.equip_weapon(item)
                    print(text.found_item(
                        "stronger weapon",
                        f'It deals {item.get_attack()} damage now!'
                    ))
                elif isinstance(item, data.Armor):
                    self.steve.equip_armor(item)
                    print(text.found_item(
                        "stronger armor",
                        f'It blocks {item.get_defence()} damage now!'
                    ))
                else:
                    print(text.found_item(
                        item.name,
                        "Do you want to pick it up?"
                    ))
                    self.show_options('item')
                    item_choice = self.prompt_player()
                    if item_choice == '1':
                        self.steve.take_item(item, 1)
            else:
                print(text.no_item)

            # move steve to the next room according to player's input, 30% chance of moving boss to adjacent room
            self.movesteve()
            if random.randint(1, 100) <= 30:
                self.moveboss()

        # game end interface
        if self.steve.isdead():
            self.show_losescreen()
        else:
            self.show_winscreen()
