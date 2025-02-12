import random
from rich import print

from textworld.map import print_map
from textworld.models import Need, Actor, Portal, Location, Component


class TheCar(Location):

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

    def __init__(self):
        super().__init__("The Martin House")

    @property
    def preposition(self):
        return "at"

def gen_index(width):
    def _inner(x, y):
        return y * width + x
    return _inner

def generate_forest_tiles(width, height):
    index_gen = gen_index(width)

    tiles = [Location("The Forest") for _ in range(width * height)]

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
            tile.exits = []
            if y > 0:
                tile.exits.append(Portal("North", destination=tiles[(y-1) * width + x]))
            if y < height - 1:
                tile.exits.append(Portal("South", destination=tiles[(y+1) * width + x]))
            if x < width - 1:
                tile.exits.append(Portal("East", destination=tiles[y * width + x + 1]))
            if x > 0:
                tile.exits.append(Portal("West", destination=tiles[y * width + x - 1]))

    return tiles

class TheForest(Component):

    def __init__(self, width=5, height=8):
        self.width = width
        self.height = height
        super().__init__("The Forest")
        self.locations = generate_forest_tiles(width, height)

        for location in self.locations:
            self.attach(location)

    def get_tile_at(self, x, y):
        return self.locations[y * self.width + x]

class Stranger(Actor):
    move_chance = 0.0

    def __init__(self):
        super().__init__("Stranger")

    def update(self):
        # maybe move
        if random.random() < self.move_chance:
            exit = random.choice(self.location.exits)
            self.location = exit.destination


if __name__ == "__main__":
    width = 5
    height = 8

    index_gen = gen_index(width)
    the_forest = TheForest(width, height)
    john = Actor("John Ward")
    john.needs = [
        Need("Faith", value=100, max_value=100, decay=0.),
        Need("Sanity", value=100, max_value=100, decay=0.)
    ]
    john.location = the_forest.locations[index_gen(2, 6)]
    the_forest.attach(john)

    garcia = Stranger()
    garcia.location = the_forest.locations[index_gen(2, 3)]
    the_forest.attach(garcia)

    print(john.description)
    while True:
        cmd = input(">>> ").lower()
        if cmd == "q":
            break
        elif cmd.startswith("move"):
            next_portal = cmd[5:]
            for portal in john.location.exits:
                if portal.name.lower() == next_portal:
                    john.location = portal.destination
            print(john.description)

        elif cmd == "look":
            print(john.location.description)
        elif cmd.startswith("say"):
            actors = john.location.list_actors()
            print(f"John says '{cmd[4:]}'")
            if len(actors) == 1:
                print("There is no one around to talk to you.")
            elif len(actors) == 2:
                for _actor in actors:
                    if _actor != john:
                        print(f"{_actor} stares at you.")
            elif len(actors) >= 3:
                print("There is more than one actor around to talk to you.")
        elif cmd == "pray":
            print("You raise your cross. Nothing happens.")

        elif cmd == "map":
            print_map(the_forest)
            continue
        else:
            print("Unknown command.")
            continue

        the_forest.update()
        print("======================")
