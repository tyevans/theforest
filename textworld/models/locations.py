from textworld.models.actors.actor import Actor
from textworld.models.components import Component


class Portal(Component):
    destination: "Location"

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

    def __init__(
        self, name, exits: list[Portal] = None, description=None, emoji=None, color=None
    ):
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
    def exits_display_raw(self):
        return ", ".join(f'"{exit.name.lower()}"' for exit in self.exits)

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

    async def update(self):
        downstream_actions = await super().update()
        for actor, action in downstream_actions:
            if action["action"] == "move":
                portal = self.get_exit(action["direction"])
                if portal:
                    for other_actor in actor.location.list_actors():
                        if other_actor is actor:
                            actor.history.append(
                                f"Moved through portal '{action['direction']}'"
                            )
                        else:
                            other_actor.history.append(
                                f"Saw {actor.name} through portal '{action['direction']}'"
                            )
                    actor.location = portal.destination
            elif action["action"] == "say":
                local_actors = self.list_actors()
                for other_actor in local_actors:
                    other_actor.hear(actor, action["content"])
        return []


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
