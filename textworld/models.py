import json
import random
from pathlib import Path

from textual.widgets import Input

from textworld.errors import NeedViolatedError


def gen_index(width):
    def _inner(x, y):
        return y * width + x

    return _inner


class Component:
    color = "blue"

    def __init__(self, name):
        self.name = name
        self._components = []

    def __str__(self):
        return f"[{self.color}]{self.name}[/{self.color}]"

    def attach(self, component: 'Component'):
        self._components.append(component)

    def detach(self, component: 'Component'):
        self._components.remove(component)

    def update(self):
        for component in self._components:
            component.update()


class Need(Component):

    def __init__(self, name, value: float, max_value: float, decay: float = 0.05):
        super().__init__(name)
        self.value = value
        self.max_value = max_value
        self.decay = decay

    def update(self):
        self.value -= self.decay
        if self.value < 0:
            raise NeedViolatedError(self)

    def __str__(self):
        return f"{super().__str__()}  ({self.value / self.max_value:.2%})"


ACTOR_DESCRIPTION_TEMPLATE = """
# {actor}

* Current location: {actor.location}
* Exits: {actor.location.exits_display}
"""


class Actor(Component):
    _location: 'Location' = None
    needs: list[Need] = []

    def update(self):
        for need in self.needs:
            need.update()

    @property
    def description(self):
        return ACTOR_DESCRIPTION_TEMPLATE.format(actor=self)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value: 'Location'):
        if self._location:
            self._location.detach(self)
        value.attach(self)
        self._location = value

    def get_need_value(self, need_name):
        for need in self.needs:
            if need.name.lower() == need_name.lower():
                return need.value
        return None


class Portal(Component):
    destination: 'Location'

    def __init__(self, name, destination):
        super().__init__(name)
        self.destination = destination


class Location(Component):
    is_container: bool = True
    exits: list[Portal]
    description: str = "A location"
    emoji: str = "🚫"
    color: str = "green"
    x: int = 0
    y: int = 0

    def __init__(self, name, exits: list[Portal] = None, description=None, emoji=None, color=None):
        super().__init__(name)
        self.exits = exits or []
        self.description = description or self.description
        self.emoji = emoji or self.emoji
        self.color = color or self.color

    def __str__(self):
        return f"[{self.color}]{self.name}[/{self.color}]"

    @property
    def exits_display(self):
        return ", ".join(str(exit) for exit in self.exits)

    @property
    def preposition(self):
        return "in" if self.is_container else "on"

    def list_actors(self):
        return [actor for actor in self._components if isinstance(actor, Actor)]

    def get_exit(self, name):
        name = name.lower()
        for portal in self.exits:
            exit_name = portal.name.lower()
            if exit_name == name:
                return portal
        return None

class TheCar(Location):
    color = "white"

    def __init__(self):
        super().__init__("The Car")


class TheWell(Location):
    color = "red"

    def __init__(self):
        super().__init__("The Well")

    @property
    def preposition(self):
        return "at"


class TheHouse(Location):
    color = "yellow"

    def __init__(self):
        super().__init__("The Martin House")

    @property
    def preposition(self):
        return "at"


def generate_forest_tiles(width, height):
    index_gen = gen_index(width)

    total_tiles = width * height
    with open(Path(__file__).parent / 'locations.json') as fd:
        data = json.load(fd)
    defined_locations = [
        Location(entry['name'], [], entry['description'], entry['emoji'], entry['color']) for entry in data]

    if total_tiles < len(defined_locations):
        defined_locations = defined_locations[:total_tiles]
    elif total_tiles > len(defined_locations):
        defined_locations.extend(
            [Location("The Forest") for _ in range(total_tiles - len(defined_locations))]
        )
    tiles = defined_locations[::]
    num_tiles = len(tiles)
    if total_tiles != num_tiles:
        raise Exception("The number of tiles does not match the number of locations")
    random.shuffle(tiles)
    tiles[index_gen(2, 6)] = TheCar()
    tiles[index_gen(2, 3)] = TheWell()
    tiles[index_gen(2, 0)] = TheHouse()

    for x in range(width):
        for y in range(height):
            tile = tiles[y * width + x]
            tile.x = x
            tile.y = y
            if tile.name == "The Forest":
                tile.name = f"The Forest ({x}, {y})"
                tile.emoji = "🌲🌳🌲"
                tile.description = "A random stretch of forest, it's almost pleasant."
            tile.exits = []
            if y > 0:
                tile.exits.append(Portal("North", destination=tiles[(y - 1) * width + x]))
            if y < height - 1:
                tile.exits.append(Portal("South", destination=tiles[(y + 1) * width + x]))
            if x < width - 1:
                tile.exits.append(Portal("East", destination=tiles[y * width + x + 1]))
            if x > 0:
                tile.exits.append(Portal("West", destination=tiles[y * width + x - 1]))

    return tiles


class TheForest(Component):
    update_frequency = 2.

    def __init__(self, width=5, height=8):
        self.next_update = self.update_frequency
        self.width = width
        self.height = height
        super().__init__("The Forest")
        self.locations = generate_forest_tiles(width, height)

        for location in self.locations:
            self.attach(location)

        self.john = Actor("John Ward")
        self.john.needs = [
            Need("Health", value=100, max_value=100, decay=0.0001),
            Need("Faith", value=100, max_value=100, decay=0.0002),
            Need("Sanity", value=100, max_value=100, decay=0.001)
        ]
        self.john.location = self.get_tile_at(2, 6)
        self.attach(self.john)
        self.garcia = Stranger()
        self.garcia.location = self.get_tile_at(2, 3)
        self.attach(self.garcia)

    def get_tile_at(self, x, y):
        return self.locations[y * self.width + x]

    def tick(self, delta_time):
        self.next_update -= delta_time
        if self.next_update <= 0:
            self.next_update += self.update_frequency
            self.update()


class Stranger(Actor):
    move_chance = 0.05

    def __init__(self):
        super().__init__("Stranger")

    def update(self):
        # maybe move
        if len(self.location.list_actors()) == 1 and random.random() < self.move_chance:
            exit = random.choice(self.location.exits)
            self.location = exit.destination
