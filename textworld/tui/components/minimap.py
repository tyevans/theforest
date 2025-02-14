from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from textworld.map import generate_map_table
from textworld.models.locations import Location


class MiniMap(Widget):
    can_focus = True
    location = reactive(Location(name="UNK"))

    def update(self, simulation):
        self.simulation = simulation
        self.location = self.simulation.player.location
        map_grid = self.query_one("#MapGrid", Label)
        map_grid.update(generate_map_table(simulation, self.location))

    def watch_location(self, value):
        label = self.query_one("#LocationLabel", Label)
        label.update(f"Location: {value}")

        exits_label = self.query_one("#ExitsLabel", Label)
        exits_label.update(f"Exits: {value.exits_display}")

    def compose(self):
        yield Label(id="LocationLabel")
        yield Label(id="ExitsLabel")
        yield Label(id="MapGrid")
