import json
from time import monotonic

from textworld.errors import NeedViolatedError
from textworld.models.components import Component
from textworld.ollama_utils import OllamaClient

ACTOR_DESCRIPTION_TEMPLATE = """
# {actor}

* Current location: {actor.location}
* Exits: {actor.location.exits_display}
"""


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


class Actor(Component):
    _location: 'Location' = None
    needs: list[Need] = []

    def __init__(self, name: str):
        super().__init__(name)
        self.queued_actions = []
        self.history = []

    def update(self):
        for need in self.needs:
            need.update()
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
    def location(self, value: 'Location'):
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

                actor.history.append(f"Saw {self.name} leave {self.location.name} towards {value.name} (Using: {portal_name})")
                self.history.append(f"Left {actor.name} at {self.location.name}")

            self._location.detach(self)

        value.attach(self)
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


class Player(Actor):
    npc_description = ("An unknown person in the forest.  "
                       "no one has every seen them before.  "
                       "they appear to be a catholic priest")


system_chat_template = """
You are an NPC in a text based adventure
Your character's name is "{actor.name}".
Your current location is: {location.name}
Description of {location.name}: {location.description}


Recent activity leading up to this round of actions:

```
{recent_history}
```

your character is described as:
{actor.npc_description}

Other characters currently in the scene:
{local_actors}

Respond to the following statement from the characters "{speakers}" (if any)

Use the following json structure to respond:

```
{{
    "response": $RESPONSE
    "move": <one of: {location.exits_display_raw}>
}}
```

where $RESPONSE is the json string you would reply with (in character)
"""


class LLMActor(Actor):
    move_chance = 0.05
    action_tick = 20.

    def __init__(self, name, npc_description):
        super().__init__("Stranger")
        self.tick_remaining = self.action_tick
        self.last_update = monotonic()
        self.name = name
        self.npc_description = npc_description
        self._history_dirty = False
        self._recent_statements = []

    def update(self):
        # maybe move
        this_update = monotonic()
        self.tick_remaining -= (this_update - self.last_update)
        self.last_update = this_update
        if self.tick_remaining <= 0 or self._history_dirty:
            self.tick_remaining = self.action_tick
            return self.act()
        return []

    def move(self, portal):
        self._history_dirty = True
        for exit_portal in self.location.exits:
            if exit_portal.name.lower() == portal.lower():
                self.location = exit_portal.destination

    def hear(self, actor, statement):
        if actor is self:
            self.history.append(f"{actor.name} (self) said: {statement}")
        else:
            self._history_dirty = True
            self.history.append(f"{actor.name} said: {statement}")
            self._recent_statements.append((actor, statement))

    def act(self):
        actions = []
        base_url = 'http://192.168.1.14:11434'
        model = 'mistral'
        client = OllamaClient(base_url, model)
        speakers = ", ".join([actor.name for actor, _ in self._recent_statements])
        local_actors = ", ".join(actor.name for actor in self.location.list_actors() if actor is not self) or "None"
        system_prompt = system_chat_template.format(actor=self, speakers=speakers, location=self.location,
                                                    recent_history="\n".join(self.history), local_actors=local_actors)

        if not self._recent_statements:
            prompt = "<Not engaged in conversation>"
        else:
            prompt = "\n".join(f"{speaker}: {statement}" for speaker, statement in self._recent_statements)
            del self._recent_statements[::]

        response = client.generate(prompt, system_prompt)
        if not response:
            return []

        if response:
            say = response.get("response")
            if say:
                actions.append({"action": "say", "content": response["response"]})
            move = response.get("move")
            if move:
                actions.append({"action": "move", "direction": move})

        with open("output.log", 'a') as fd:
            fd.write("\n=========\n")
            fd.write(system_prompt)
            fd.write("\n----------\n")
            fd.write(prompt)
            fd.write("\n----------\n")
            fd.write(json.dumps(response))

        self._history_dirty = False
        return actions
