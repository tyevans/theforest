import json
import random
from pathlib import Path

from textworld.models.actors import Player, Need, LLMActor
from textworld.models.components import Component

from textworld.models.locations import Location, TheCar, TheWell, TheHouse, Portal


def gen_index(width):
    def _inner(x, y):
        return y * width + x

    return _inner


def generate_forest_tiles(width, height):
    index_gen = gen_index(width)

    total_tiles = width * height
    with open(Path(__file__).parent.parent / 'locations.json') as fd:
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
    update_frequency = 1.

    def __init__(self, width=5, height=8):
        self.next_update = self.update_frequency
        self.width = width
        self.height = height
        super().__init__("The Forest")
        self.locations = generate_forest_tiles(width, height)

        for location in self.locations:
            self.attach(location)

        self.john = Player("John Ward")
        self.john.needs = [
            Need("Health", value=100, max_value=100, decay=0.0001),
            Need("Faith", value=100, max_value=100, decay=0.0002),
            Need("Sanity", value=100, max_value=100, decay=0.001)
        ]
        self.john.location = self.get_tile_at(2, 4)
        self.attach(self.john)
        self.garcia = LLMActor("Father Garcia", "An old hispanic priest.  "
                                           "Is new to the forest and is looking "
                                           "for a demonically possessed boy (Michael) that escaped during exorcism."
                                           "Does not know who John is, but is intrigued. speaks in English.  Real name is Father Garcia (if asked).  he is eager to assist John and do anything asked.")

        self.garcia.location = self.get_tile_at(2, 3)
        self.attach(self.garcia)

        self.michael = LLMActor(
            "Michael",
            "A demonically possessed child.  He escaped into the forest while Father Garcia was attempting "
            "to exorcise the demon in Michael.  Michael is a foul and corrupted soul.  He cusses and acts crass at all times trying to shock and weaken those around him",
        )
        self.michael.location = self.get_tile_at(3, 3)
        self.attach(self.michael)

    def get_tile_at(self, x, y):
        return self.locations[y * self.width + x]

    def tick(self, delta_time):
        self.next_update -= delta_time
        if self.next_update <= 0:
            self.next_update += self.update_frequency
            self.update()
