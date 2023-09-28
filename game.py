#File containing the code for the game
import random

import data
from generator import LabyrinthGenerator
import text

NORTH = "NORTH"
SOUTH = "SOUTH"
EAST = "EAST"
WEST = "WEST"


LABSIZE = 10


class MUDGame:
    """This class encapsulates data for the main game implementation."""

    def __init__(self) -> None:
        self.gameover = False  # default
        self.won = False  # default
        generator = LabyrinthGenerator(x_size=LABSIZE, y_size=LABSIZE)
        generator.generate()
        labyrinth = generator.get_maze()
        self.maze = data.LabyrinthManager(labyrinth)
        self.steve = data.Steve()
        self.steve_path = []
        self.boss = data.Boss()

    def introduce(self) -> None:
        """
        Starting interface of the game
        """
        username = ''
        n = 0
        while username.strip(' ') == '':
            n += 1
            if n > 1:
                print(text.username_error)
            username = input(text.username_prompt)

        print(text.intro(username))

    def game_is_over(self) -> bool:
        """
        Returns True if either Steve or Boss is dead.
        """
        if self.steve.isdead() or self.boss.isdead():  # other conditions
            return True

    def show_status(self) -> None:
        """
        Print status of Steve.
        """
        print(self.steve)

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
        coord = self.maze.get_current_pos()
        room = self.maze.get_room(coord)
        creature = room.get_creature()
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
                        self.steve.display_inventory()
                        if n > 1:
                            self.invalid_opt()
                        heal_option = input(text.heal_prompt)
                        self.isvalid_heal(heal_option)
                    heal_option = int(heal_option) - 1
                    self.steve.eat(heal_option)
                    print(text.heal_success)
            #Steve endturn
            damage = creature.random_move()
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

    def creature_encountered(self) -> bool:
        """
        Returns True when creature is found in the room.
        """
        coord = self.maze.get_current_pos()
        room = self.maze.get_room(coord)
        if room.get_creature() is None:
            return False
        return True

    def item_found(self) -> bool:
        """
        Returns True if item is found in the room.
        """
        coord = self.maze.get_current_pos()
        room = self.maze.get_room(coord)
        if room.get_item() is None:
            return False
        return True

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
        current_location = self.maze.get_current_pos()
        available_dir = []
        dir_provided = ''
        for dir_name, dir_coord in data.cardinal.items():
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
        self.maze.move_steve(data.cardinal[available_dir[choice - 1]])

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

    def run(self):

        # starting interface
        self.introduce()

        # while loop continue until steve or boss die
        while not self.game_is_over():
            print('\n')

            # append the current location to steve_path
            self.steve_path.append(self.maze.get_current_pos)

            # print steve's status
            self.show_status()

            # creature is found in the room
            if self.creature_encountered():

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
                        current_location = self.maze.get_current_pos()
                        available_dir = []
                        for dir_name, dir_coord in data.cardinal.items():
                            if self.maze.can_move_here(current_location, dir_coord):
                                available_dir.append(dir_name)
                        random_dir = random.choice(available_dir)
                        self.maze.move_steve(data.cardinal[random_dir])
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
            if self.item_found():
                coord = self.maze.get_current_pos()
                room = self.maze.get_room(coord)
                item = room.get_item()
                if isinstance(item, data.Weapon):
                    self.steve.equip_weapon(item)
                    print(text.found_item(
                        "stronger weapon",
                        f'It deals {item.get_attack()} damage now!'
                    ))
                elif isinstance(item, data.Armor):
                    self.steve.equip_armour(item)
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
