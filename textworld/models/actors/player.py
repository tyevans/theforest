from textworld.models.actors.actor import Actor
from textworld.models.actors.llm import ACTOR_PUBLIC_DESCRIPTION_TEMPLATE


class Player(Actor):

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
