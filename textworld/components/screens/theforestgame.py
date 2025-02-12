from time import monotonic

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, Static, Header, Log, Input

from textworld.components.boxlabel import BoxLabel
from textworld.components.gamelog import GameLog
from textworld.components.minimap import MiniMap
from textworld.components.playerstatus import PlayerStatus
from textworld.models import TheForest, Location
from textworld.settings import AppSettings


def create_the_forest():
    settings = AppSettings()
    the_forest = TheForest(settings.map_width, settings.map_height)
    return the_forest


class TheForestGameScreen(Screen):
    """
    This is the game itself.

    handles time management and global world state.
    """
    DEFAULT_CSS = """
    .container {
        width: 100%;
        height: 100%;
        layout: grid;
        grid-size: 2 1;
        grid-columns: 2fr 1fr;
    }
    
    .column-left {
        layout: grid;
        grid-size: 1 2;
        grid-rows: 12fr 1fr;
    }

    .column-right {
        layout: grid;
        grid-size: 1 3;
        grid-rows: 8fr 8fr 1fr;
    }
    
    .box {
        height: 100%;
        border: solid green;
    }
    """
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "pause", "Pause"),
        ("left", "left", "Left"),
        ("right", "right", "Right"),
        ("up", "up", "Up"),
        ("down", "down", "Down"),
    ]

    start_time = reactive(monotonic)
    runtime = reactive(0.0)
    paused = reactive(False)

    def on_mount(self) -> None:
        """Called when the game screen loads.  schedules screen updates for 12fps."""
        self.set_interval(1 / 12, self.update_runtime)
        self.simulation = create_the_forest()

    def update_runtime(self):
        if not self.paused:
            self.runtime = monotonic() - self.start_time

    def watch_runtime(self, runtime: float) -> None:
        """Called when the time attribute changes."""
        self.simulation.tick(self.runtime)
        mini_map = self.query_one(MiniMap)
        mini_map.update(simulation=self.simulation)

        player_status = self.query_one(PlayerStatus)
        player_status.update(simulation=self.simulation)

    def watch_paused(self, paused: bool):
        if not paused:
            self.start_time = monotonic()


    def set_john_location(self, location: Location):
        if self.paused:
            return
        self.simulation.john.location = location
        env_text = self.query_one("#EnvironmentalText", BoxLabel)
        env_text.update(location.description)

    def action_left(self):
        portal = self.simulation.john.location.get_exit("west")
        if portal:
            self.set_john_location(portal.destination)

    def action_right(self):
        portal = self.simulation.john.location.get_exit("east")
        if portal:
            self.set_john_location(portal.destination)

    def action_up(self):
        portal = self.simulation.john.location.get_exit("north")
        if portal:
            self.set_john_location(portal.destination)

    def action_down(self):
        portal = self.simulation.john.location.get_exit("south")
        if portal:
            self.set_john_location(portal.destination)

    def action_pause(self):
        self.paused = not self.paused

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                GameLog(),
                Input(placeholder=">>>", classes='box'),
                classes='box column-left'
            ),
            Vertical(
                MiniMap(id="MiniMap", classes='box'),
                BoxLabel(id="EnvironmentalText"),
                PlayerStatus(id="PlayerStatus", classes='player_status'),
                classes='box column-right'
            ),
            classes='container'
        )
        yield Footer()

    def on_input_submitted(self, data):
        if self.paused:
            return

        log = self.query_one(GameLog)
        log.write_line(data.value)

        cmd = data.value
        john = self.simulation.john

        if cmd.startswith("move"):
            next_portal = cmd[5:].lower()
            for portal in john.location.exits:
                if portal.name.lower() == next_portal:
                    john.location = portal.destination
                    self.set_john_location(portal.destination)

        elif cmd == "look":
            log.write_line(john.location.description)
        elif cmd.startswith("say"):
            actors = john.location.list_actors()
            log.write_line(f"John says '{cmd[4:]}'")
            if len(actors) == 1:
                log.write_line("There is no one around to talk to you.")
            elif len(actors) == 2:
                for _actor in actors:
                    if _actor != john:
                        log.write_line(f"{_actor} stares at you.")
            elif len(actors) >= 3:
                log.write_line("There is more than one actor around to talk to you.")
        elif cmd == "pray":
            log.write_line("You raise your cross. Nothing happens.")
        else:
            log.write_line("Unknown command.")

        user_input = self.query_one(Input)
        user_input.value = ""
