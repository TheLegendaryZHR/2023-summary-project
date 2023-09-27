



username_prompt = 'Enter your username: '
username_error = 'Please enter a valid username with at least one character.'

def intro(username: str) -> str:
    return f'{username}, OH NO YOU ARE TRAPPED! \nYou will go through a series of rooms that may give you items or have ANGRY creatures wanting you DEAD :P \nKill them all, especially the boss to escape! \nGOOD LUCK ;D'

def battle_hp_report(name: str, hp: int) -> str:
    return f"{name} now has {hp} HP"

def heal_report(healing: int, health: int) -> str:
    return f"You were healed by {healing} HP and now have {health}."

def damage_report(damage: int, health: int) -> str:
    return f"You got hurt by {damage} HP and have {health} left."

heal_prompt = 'Please choose a food item: '
heal_success = 'Healed!'

def creature_selfheal(name: str) -> str:
    return f"The {name} has healed itself."

def creature_dealdmg(name: str, dmg: int) -> str:
    return f"The {name} has dealt {dmg} damage on you."

game_win = 'Congratulations! \nYou have escaped!'
game_lose = "YOU DIED..."

escape_success = 'You have successfully ran away!'
escape_failure = "Too late to escape!"
escape_notrequired = 'No creature found in this room.'

option_invalid = 'Please enter a valid option.'

def move_prompt(directions: str) -> str:
    return 'Where are you going next? ' + directions

def found_item(name: str, effect: str) -> str:
    return f"'You have found a {name}! {effect}"

no_item = 'No item found in this room.'

inventory_empty = "You have no items in your inventory."

creeper_prompt = "AHHHHHHH A CREEPER HAS APPEARED!!!! RUN AWAY QUICK BY\n PRESSING THE FOLLOWING LETTER:"

def creeper_quickevent(letter: str) -> str:
    return "ENTER THE LETTER " + letter + " QUICK: "

creeper_explode = "KABOOOOOMMMMM THE CREEPER EXPLODEDDDDD!!!!!!"

creeper_dodge_success = "Luckily, your quick reactions allowed you to avoid the explosion. You took no damage."

creeper_dodge_failure = "Oh no! You took the wrong action and got caught in the blast!"

creeper_dodge_slow = "Oh no! You were too slow and got caught in the blast!"
