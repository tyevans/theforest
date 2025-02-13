from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Label, Static


class PlayerStatus(HorizontalGroup):
    health = reactive(100)
    sanity = reactive(100)
    faith = reactive(100)

    def update(self, simulation) -> None:
        self.health = simulation.john.get_need_value('health')
        self.sanity = simulation.john.get_need_value('sanity')
        self.faith = simulation.john.get_need_value('faith')

    def watch_health(self, value):
        health_color = "green"
        self.query_one("#HealthLabel", Label).update(f"⚕️ [{health_color}]Health: {self.health:.2f}[/{health_color}] | ")

    def watch_sanity(self, value):
        sanity_color = "green"
        self.query_one("#SanityLabel", Label).update(f"😵‍💫 [{sanity_color}]Sanity: {self.sanity:.2f}[/{sanity_color}] | ")

    def watch_faith(self, value):
        faith_color = "green"
        self.query_one("#FaithLabel", Label).update(f"✝️ [{faith_color}]Faith: {self.faith:.2f}[/{faith_color}]")

    def compose(self):
        yield Label(id="HealthLabel")
        yield Label(id="SanityLabel")
        yield Label(id="FaithLabel")
