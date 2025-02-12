from textworld.errors import NeedViolatedError


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
        return f"{super().__str__()}  ({self.value/self.max_value:.2%})"

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


class Portal(Component):
    destination: 'Location'

    def __init__(self, name, destination):
        super().__init__(name)
        self.destination = destination


class Location(Component):
    is_container: bool = True
    exits: list[Portal]
    color: str = "green"
    x: int = 0
    y: int = 0

    def __init__(self, name, exits: list[Portal] = None):
        self.exits = exits or []
        super().__init__(name)

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

    @property
    def description(self):
        output = [f"Location: {super().__str__()}"]
        output.extend([
            f"Actors {self.preposition} {super().__str__()}:",
            *(f"\t{actor}" for actor in self._components if isinstance(actor, Actor)),
        ])
        return "\n".join(output)
