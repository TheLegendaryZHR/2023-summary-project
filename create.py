"""create.py

Factory functions for items, creatures
"""

import action
import character
import data

def _action(name: str, data: dict) -> action.Action:
    """Factory function for Action"""
    Action = action.get(name)
    # The ** operator expands a dict into keyword arguments
    # which can be passed into a function or method
    return Action(**data)

def creature(data_: dict) -> character.Creature:
    actions = [_action(name, data_) for name, data in creature_data["actions"]]
    if "Heal" in actions:
        return character.HealingCreature(
            data_["name"],
            data_["base_hp"],
            data_["base_atk"],
            actions,
        )
    else:
        return character.Creature(
            data_["name"],
            data_["base_hp"],
            data_["base_atk"],
            actions,
        )

def armor(data_: dict) -> data.Armor:
    """Factory function for Armor"""
    return Armor(data_["name"], data_["defence"], data_["slot"])

def food(data_: dict) -> data.Food:
    """Factory function for Food"""
    return Food(data_["name"], data_["hprestore"])

def weapon(data_: weapon) -> data.Weapon:
    """Factory function for Weapon"""
    return Weapon(data_["name"], data_["atk"])

def random_item() -> data.Item:
    """returns a randomly generated item"""
    item_types = [data.Armor, data.Food, data.Weapon]
    item_type = random.choice(item_types)
    if item_type == data.Armor:
        return armor(random.choice(data.armor_data))
    elif item_type == data.Food:
        return food(random.choice(data.food_data))
    elif item_type == data.Weapon:
        return weapon(random.choice(data.weapon_data))

def random_creature() -> "Creature":
    """returns a randomly generated creature"""
    creatures = []
    creature_data = random.choice(character.creature_data)
    return creature(creature_data)
