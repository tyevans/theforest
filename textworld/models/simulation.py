import random
from functools import cached_property

from textworld.assets import load_json_asset
from textworld.models.actors.llm import LLMActor
from textworld.models.actors.needs import Need
from textworld.models.actors.player import Player
from textworld.models.components import Component
from textworld.models.locations import Location, TheCar, TheWell, TheHouse, Portal


def gen_index(width):
    def _inner(x, y):
        return y * width + x

    return _inner


def generate_forest_tiles(width, height):
    location_data = load_json_asset("drugs.locations.json")
    total_tiles = width * height
    tiles = [
        Location(
            entry["name"], [], entry["description"], entry["emoji"], entry["color"]
        )
        for entry in location_data
    ]

    if total_tiles < len(tiles):
        tiles = tiles[:total_tiles]
    elif total_tiles > len(tiles):
        tiles.extend([Location("The Forest") for _ in range(total_tiles - len(tiles))])
    random.shuffle(tiles)

    for x in range(width):
        for y in range(height):
            print("Here!")
            tile = tiles[y * width + x]
            tile.x = x
            tile.y = y
            if tile.name == "The Forest":
                tile.name = f"The Forest ({x}, {y})"
                tile.emoji = "🌲🌳🌲"
                tile.description = "A random stretch of forest, it's almost pleasant."
            tile.exits = []
            if y > 0:
                tile.exits.append(
                    Portal("North", destination=tiles[(y - 1) * width + x])
                )
            if y < height - 1:
                tile.exits.append(
                    Portal("South", destination=tiles[(y + 1) * width + x])
                )
            if x < width - 1:
                tile.exits.append(Portal("East", destination=tiles[y * width + x + 1]))
            if x > 0:
                tile.exits.append(Portal("West", destination=tiles[y * width + x - 1]))

    return tiles


class Simulation(Component):
    update_frequency = 1.0

    def __init__(self, width=5, height=8):
        self.next_update = self.update_frequency
        self.width = width
        self.height = height
        super().__init__("The Game")

        self.locations = generate_forest_tiles(width, height)
        for location in self.locations:
            self.attach_sync(location)

        character_data = load_json_asset("drugs.characters.json")
        for c_data in character_data:
            actor = LLMActor(
                c_data["name"],
                c_data["private_facts"],
                c_data["public_facts"],
            )
            actor.location = self.get_tile_at(
                random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            )
            self.attach(actor)

    @cached_property
    def player(self):
        player = Player(
            "John Ward",
            private_facts=[],
            public_facts=[
                "John Ward is a priest",
                "John Ward is 6 feet tall",
                "John Ward is White",
                "John Ward is muscular",
            ],
        )
        player.needs = [
            Need("Health", value=100, max_value=100, decay=0.0001),
            Need("Faith", value=100, max_value=100, decay=0.0002),
            Need("Sanity", value=100, max_value=100, decay=0.001),
        ]
        player.location = self.get_tile_at(4, 1)
        self.attach(player)
        return player

    def get_tile_at(self, x, y):
        return self.locations[y * self.width + x]

    async def tick(self, delta_time):
        self.next_update -= delta_time
        if self.next_update <= 0:
            self.next_update += self.update_frequency
            await self.update()
