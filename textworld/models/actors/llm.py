import json
from time import monotonic

from textworld.models.actors.actor import Actor
from textworld.ollama_utils import OllamaClient

system_chat_template = """
You are an NPC in a text based adventure
Your character's name is "{actor.name}".
Your current location is: {location.name}
Description of {location.name}: {location.description}


Recent activity leading up to this round of actions:

```
{recent_history}
```

This is information about your character:
{actor.private_description}


This is information about other characters currently in the scene:
{local_actors}

Respond to the following statement from the speakers (if any)

Use the following json structure to respond:

```
{{
    "response": $RESPONSE
    "move": <one of: {location.exits_display_raw},null>
}}
```

null means your character will not move.
The only moves that are valid right now are: {location.exits_display_raw}
If a direction you want is not listed, then you are at the edge of the map

where $RESPONSE is the json string you would reply with (in character)

Keep all responses to fewer than 200 characters.
"""

ACTOR_PUBLIC_DESCRIPTION_TEMPLATE = """
Name: {actor.name}
Known Information:
{formatted_public_facts}
{formatted_private_facts}
"""


class LLMActor(Actor):
    action_tick = 10.0

    def __init__(self, name, private_facts, public_facts):
        super().__init__(name, private_facts, public_facts)
        self.tick_remaining = self.action_tick
        self.last_update = monotonic()
        self.name = name
        self.private_facts = private_facts
        self.public_facts = public_facts
        self._history_dirty = False
        self._recent_statements = []

    @property
    def public_description(self):
        formatted_public_facts = "\n".join(f"\t{fact}" for fact in self.public_facts)
        return ACTOR_PUBLIC_DESCRIPTION_TEMPLATE.format(
            actor=self,
            formatted_public_facts=formatted_public_facts,
            formatted_private_facts="",
        )

    @property
    def private_description(self):
        formatted_public_facts = "\n".join(f"\t{fact}" for fact in self.public_facts)
        formatted_private_facts = "\n".join(f"\t{fact}" for fact in self.private_facts)
        return ACTOR_PUBLIC_DESCRIPTION_TEMPLATE.format(
            actor=self,
            formatted_public_facts=formatted_public_facts,
            formatted_private_facts=formatted_private_facts,
        )

    async def update(self):
        # maybe move
        this_update = monotonic()
        self.tick_remaining -= this_update - self.last_update
        self.last_update = this_update
        if self.tick_remaining <= 0 or self._history_dirty:
            self.tick_remaining = self.action_tick
            return await self.act()
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

    async def act(self):
        actions = []
        base_url = "http://192.168.1.14:11434"
        model = "mistral"
        client = OllamaClient(base_url, model)
        speakers = ", ".join([actor.name for actor, _ in self._recent_statements])
        local_actors = (
            "\n---------------\n".join(
                actor.public_description
                for actor in self.location.list_actors()
                if actor is not self
            )
            or "None"
        )
        system_prompt = system_chat_template.format(
            actor=self,
            speakers=speakers,
            location=self.location,
            recent_history="\n".join(self.history),
            local_actors=local_actors,
        )

        if not self._recent_statements:
            prompt = "<Not engaged in conversation>"
        else:
            prompt = "\n".join(
                f"{speaker}: {statement}"
                for speaker, statement in self._recent_statements
            )
            del self._recent_statements[::]

        response = await client.generate(prompt, system_prompt)
        if not response:
            return []

        if response:
            say = response.get("response")
            if say:
                actions.append({"action": "say", "content": response["response"]})
            move = response.get("move")
            if move:
                actions.append({"action": "move", "direction": move})

        with open("output.log", "a") as fd:
            fd.write("\n=========\n")
            fd.write(system_prompt)
            fd.write("\n----------\n")
            fd.write(prompt)
            fd.write("\n----------\n")
            fd.write(json.dumps(response))

        self._history_dirty = False
        return actions
