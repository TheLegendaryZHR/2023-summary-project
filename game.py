#File containing the code for the game
import random

import data

NORTH = "NORTH"
SOUTH = "SOUTH"
EAST = "EAST"
WEST = "WEST"


class MUDGame:
    """This class encapsulates data for the main game implementation."""

    def __init__(self) -> None:
        self.gameover = False  # default
        self.won = False  # default
        generator = data.LabyrinthGenerator()
        generator.generate()
        labyrinth = generator.get_lab()
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
                print(
                    'Please enter a valid username with at least one character.'
                )
            username = input('Enter your username: ')

        print(
            f'{username}, OH NO YOU ARE TRAPPED! \nYou will go through a series of rooms that may give you items or have ANGRY creatures wanting you DEAD :P \nKill them all, especially the boss to escape! \nGOOD LUCK ;D'
        )

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
            if len(self.steve._inventory) == 0:
                print(
                    f'You have no heal items! \nAttack the {creature.get_name()}.'
                )
                damage = self.steve.get_attack()
                creature.take_damage(damage)
                print(
                    f"{creature.get_name()} now has {creature.get_health()} HP"
                )
                if creature.get_health() == 0:
                    continue
            else:
                self.show_options('battle')
                battle_option = self.prompt_player()
                if battle_option == '1':
                    #attack
                    damage = self.steve.get_attack()
                    creature.take_damage(damage)
                    print(
                        f"{creature.get_name()} now has {creature.get_health()} HP"
                    )
                elif battle_option == '2':
                    #heal
                    heal_option = None
                    n = 0
                    while not self.isvalid_heal(heal_option):
                        n += 1
                        self.steve.display_inventory()
                        if n > 1:
                            self.invalid_opt()
                        heal_option = input('Please choose a food item: ')
                        self.isvalid_heal(heal_option)
                    heal_option = int(heal_option) - 1
                    self.steve.eat(heal_option)
                    print('Healed!')
            #Steve endturn
            damage = creature.random_move()
            self.steve.take_damage(damage)
            if damage == 0:
                print(f"The {creature.name} has healed itself.")
            else:
                print(f"The {creature.name} has dealt {damage} damage on you.")
        if room.creature.isdead():
            room.set_creature_None()

    def isvalid_heal(self, heal_option) -> bool:
        """
        Validate player's option when choosing food items from inventory.
        Used for battle()
        """
        range_of_option = len(self.steve._inventory) + 1
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
        print('Congratulations! \nYou have escaped!')

    def show_losescreen(self) -> None:
        """
        Show losescreen when Steve dies."""
        print("YOU DIED...")
        print(f"Score: {random.randint(0, 10000)}")

    def movesteve(self) -> None:
        """
        Move Steve to another room when no item or creatures left in the current room.
        """
        current_location = self.maze.get_current_pos()
        opt_dir = {'1': NORTH, '2': SOUTH, '3': EAST, '4': WEST}
        available_dir = []
        dir_provided = ''
        for dir in opt_dir.values():
            if self.maze.can_move_here(current_location, dir):
                available_dir.append(dir)
        for i in range(len(available_dir)):
            dir_provided = dir_provided + str(
                i + 1) + '. ' + available_dir[i] + ' '
        validity = False
        n = 0
        while validity is False:
            n += 1
            if n > 1:
                self.invalid_opt()
            print('Where are you going next? ' + dir_provided)
            choice = input('Next location: ')
            no_of_choice = len(available_dir)
            valid_choice = ''
            for i in range(no_of_choice):
                valid_choice += str(i + 1)
            if choice in valid_choice and len(choice) == 1:
                validity = True
        choice = int(choice)
        self.maze.move_steve(available_dir[choice - 1])

    def moveboss(self) -> None:
        """
        Move boss to another room.
        """
        self.maze.move_boss()

    def invalid_opt(self) -> None:
        """
        Show error message.
        """
        print('Please enter a valid option.')

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
                        opt_dir = {
                            '1': NORTH,
                            '2': SOUTH,
                            '3': EAST,
                            '4': WEST
                        }
                        available_dir = []
                        for dir in opt_dir.values():
                            if self.maze.can_move_here(current_location, dir):
                                available_dir.append(dir)
                                random_dir = random.choice(available_dir)
                        self.maze.move_steve(random_dir)
                        print('You have successfully ran away!')
                        continue
                    else:
                        print("Too late to escape!")
                        self.battle()
                        if self.game_is_over():
                            continue
            else:
                print('No creature found in this room.')

            # item is found in the room
            # item can be 'Armor', 'Food', 'Weapon'
            # armor and weapon item will be automatically picked up
            # player can choose to pick up food item or not
            if self.item_found():
                coord = self.maze.get_current_pos()
                room = self.maze.get_room(coord)
                item = room.get_item()
                if item.item_type == 'Weapon':
                    self.steve.equip_weapon(item)
                    print(
                        f'You have found a stronger weapon! It deals {item.get_attack()} damage now!'
                    )
                elif item.item_type == 'Armor':
                    self.steve.equip_armour(item)
                    print(
                        f'You have found a stronger armor! It blocks {item.get_defence()} damage now!'
                    )
                else:
                    print(
                        f"You have found a {item.name}! \nDo you want to pick it up?"
                    )
                    self.show_options('item')
                    item_choice = self.prompt_player()
                    if item_choice == '1':
                        self.steve._add_item_to_inv(item, 1)
            else:
                print('No item found in this room.')

            # move steve to the next room according to player's input, 30% chance of moving boss to adjacent room
            self.movesteve()
            if random.randint(1, 100) <= 30:
                self.moveboss()

        # game end interface
        if self.steve.isdead():
            self.show_losescreen()
        else:
            self.show_winscreen()
