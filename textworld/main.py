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
    car = Location("John's Car")
    car.is_container = True

    the_forest = Location("The Forest")
    the_forest.is_container = True

    car.exits = [
        Portal("The Forest", destination=the_forest),
        Portal("The Road (North)", destination=car),
        Portal("The Road (South)", destination=car),
    ]

    the_forest = Location("The Forest")
    the_forest.is_container = True
    the_forest.exits = [
        Portal("Deeper into the Forest", destination=the_forest),
        Portal("The Car", destination=car),
    ]

    john = Actor('John Ward')
    john.location = car

    john.needs = [
        Need("Hunger", value=100, max_value=100, decay=0.1),
        Need("Bladder", value=100, max_value=100, decay=0.03),
        Need("Happiness", value=100, max_value=100, decay=0.07),
        Need("Faith", value=100, max_value=100, decay=0.00),
        Need("Sanity", value=100, max_value=100, decay=0.00),
    ]

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

        john.update()
        print("========================")
