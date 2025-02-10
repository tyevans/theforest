from textworld.models import Need, Actor, Portal, Location

class TheCar(Location):

    def __init__(self):
        super().__init__("The Car")


class TheWell(Location):

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


def generate_forest_tiles(width, height):
    tiles = [Location("The Forest") for _ in range(width * height)]

    car_pos_y = 6
    car_pos_x = 2
    tiles[car_pos_y * width + car_pos_x] = TheCar()

    well_pos_y = 3
    well_pos_x = 2
    tiles[well_pos_y * width + well_pos_x] = TheWell()

    house_pos_y = 0
    house_pos_x = 2
    tiles[house_pos_y * width + house_pos_x] = TheHouse()

    for x in range(width):
        for y in range(height):
            tile = tiles[y * width + x]
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

class TheForest:

    def __init__(self, width=5, height=8):
        self.locations = generate_forest_tiles(width, height)


if __name__ == "__main__":

    the_forest = TheForest()
    john = Actor("John Ward")
    john.needs = [
        Need("Faith", value=100, max_value=100, decay=0.),
        Need("Sanity", value=100, max_value=100, decay=0.)
    ]

    garcia = Actor("Stranger")
    garcia.needs = []
    for location in the_forest.locations:
        if isinstance(location, TheWell):
            garcia.location = location
            break

    for location in the_forest.locations:
        if isinstance(location, TheCar):
            john.location = location
            break

    print(john.description)
    while True:
        cmd = input(">>> ").lower()
        match cmd:
            case "q":
                break
            case "move":
                next_portal = input("Through which portal? ").lower()
                for portal in john.location.exits:
                    if portal.name.lower() == next_portal:
                        john.location = portal.destination
                print(john.description)

            case "look":
                print(john.location.description)
            case "pray":
                print("You raise your cross. Nothing happens.")

        john.update()