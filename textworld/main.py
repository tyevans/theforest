from csv import excel


class Component:

    def __init__(self, name):
        self.name = name
        self._components = []

    def __str__(self):
        return self.name

    def attach(self, component: 'Component'):
        self._components.append(component)

    def detach(self, component: 'Component'):
        self._components.remove(component)

    def update(self):
        for component in self._components:
            component.update()


class NeedViolatedError(Exception):
    pass


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
        return f"{super().__str__()}  ({self.value/self.max_value:.2%})"

class Actor(Component):
    location: 'Location'
    needs: list[Need]

    def update(self):
        for need in self.needs:
            need.update()

    @property
    def description(self):
        output = [f"{super().__str__()} {self.location.preposition} {self.location}"]
        output.extend([
            "Needs:",
            *(f"\t{need}" for need in self.needs),
        ])
        return "\n".join(output)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value: 'Location'):
        value.attach(self)
        self._location = value


class Portal(Component):
    destination: 'Location'

    def __init__(self, name, destination):
        super().__init__(name)
        self.destination = destination


class Location(Component):
    is_container: bool = True
    exits: list[Portal]

    def __str__(self):
        formatted = [
            super().__str__(),
            "Exits: ",
            *[f"\t{portal}" for portal in self.exits]
        ]
        return "\n".join(formatted)

    @property
    def preposition(self):
        return "in" if self.is_container else "on"

    @property
    def description(self):
        output = [f"Location: {super().__str__()}"]
        output.extend([
            f"Actors {self.preposition} {super().__str__()}:",
            *(f"\t{actor}" for actor in self._components if isinstance(actor, Actor)),
        ])
        return "\n".join(output)

if __name__ == "__main__":
    dining_room = Location("The Dining Room")
    kitchen = Location("The Kitchen")

    dining_room.exits = [
        Portal(name="Kitchen", destination=kitchen),
    ]
    kitchen.exits = [
        Portal(name="Dining Room", destination=dining_room),
    ]

    # front_porch = Location(name="The Front Porch")
    # front_porch.is_container = False
    # music_room = Location("The Music Room")
    # dining_room = Location("The Dining Room")
    # kitchen = Location("The Kitchen")
    # living_room = Location("The Living Room")
    # mainfloor_hallway = Location("The Main Floor Hallway")
    # mainfloor_bathroom = Location("The Main Floor Bathroom")
    # breakfast_nook = Location("The Breakfast Nook")
    # back_porch = Location("The Back Porch")
    # back_porch.is_container = False
    #
    # front_porch.exits = [
    #     Portal(name="Front Door", destination=music_room),
    # ]
    # music_room.exits = [
    #     Portal(name="Front Door", destination=front_porch),
    #     Portal(name="Dining Room", destination=dining_room),
    #     Portal(name="Hallway", destination=mainfloor_hallway),
    # ]
    # dining_room.exits = [
    #     Portal(name="Kitchen", destination=kitchen),
    #     Portal(name="Music Room", destination=music_room),
    # ]
    #
    # kitchen.exits = [
    #     Portal(name="Dining Room", destination=dining_room),
    #     Portal(name="Living Room", destination=living_room),
    # ]
    #
    # living_room.exits = [
    #     Portal(name="Kitchen", destination=kitchen),
    #     Portal(name="Breakfast Nook", destination=breakfast_nook),
    #     Portal(name="Hallway", destination=mainfloor_hallway),
    # ]
    #
    # mainfloor_hallway.exits = [
    #     Portal(name="Music Room", destination=music_room),
    #     Portal(name="Living Room", destination=living_room),
    #     Portal(name="Bathroom", destination=mainfloor_bathroom),
    # ]
    # mainfloor_bathroom.exits = [
    #     Portal(name="Hallway", destination=mainfloor_hallway),
    # ]
    # breakfast_nook.exits = [
    #     Portal(name="Back Porch", destination=back_porch),
    #     Portal(name="Living Room", destination=living_room),
    # ]

    actor2 = Actor('Max')
    actor2.location = living_room
    actor1 = Actor('Tyler')
    actor1.location = front_porch
    actor1.needs = [
        Need("Hunger", value=100, max_value=100, decay=0.1),
        Need("Bladder", value=100, max_value=100, decay=0.03),
        Need("Happiness", value=100, max_value=100, decay=0.07),
    ]
    print(actor1.description)
    while True:
        cmd = input(">>> ").lower()

        match cmd:
            case "q":
                break
            case "move":
                next_portal = input("Through which portal? ").lower()
                for portal in actor1.location.exits:
                    if portal.name.lower() == next_portal:
                        actor1.location = portal.destination
                print(actor1.description)

            case "look":
                print(actor1.location.description)

        actor1.update()
        print("========================")