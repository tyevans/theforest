from textworld.models.actors.needs import Need
from textworld.models.components import Component

ACTOR_DESCRIPTION_TEMPLATE = """
# {actor}

* Current location: {actor.location}
* Exits: {actor.location.exits_display}
"""


class Actor(Component):
    _location: "Location" = None
    needs: list[Need] = []

    def __init__(self, name, private_facts, public_facts):
        super().__init__(name)
        self.private_facts = private_facts
        self.public_facts = public_facts
        self.queued_actions = []
        self.history = []

    async def update(self):
        for need in self.needs:
            await need.update()
        actions = self.queued_actions[::]
        del self.queued_actions[::]
        return actions

    @property
    def description(self):
        return ACTOR_DESCRIPTION_TEMPLATE.format(actor=self)

    def hear(self, actor, statement):
        if actor == self:
            self.history.append(f"(Said) {actor}: {statement}")
        else:
            self.history.append(f"(Heard) {actor}: {statement}")

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value: "Location"):
        if value is self._location:
            return

        if self._location:
            for actor in self.location.list_actors():
                if actor is self:
                    continue
                actor._history_dirty = True
                for exit in self.location.exits:
                    if exit.destination == value:
                        portal_name = exit.name.lower()
                        break
                else:
                    portal_name = "UNKNOWN"

                actor.history.append(
                    f"Saw {self.name} leave {self.location.name} towards {value.name} (Using: {portal_name})"
                )
                self.history.append(f"Left {actor.name} at {self.location.name}")

            self._location.detach_sync(self)

        value.attach_sync(self)
        self._location = value
        self.history.append(f"Moved to {value.name}")

        for actor in self.location.list_actors():
            if actor is self:
                continue
            actor._history_dirty = True
            actor.history.append(f"Encountered {self.name} in {self.location.name}")
            self.history.append(f"Encountered {actor.name} in {self.location.name}")

    def get_need_value(self, need_name):
        for need in self.needs:
            if need.name.lower() == need_name.lower():
                return need.value
        return None
