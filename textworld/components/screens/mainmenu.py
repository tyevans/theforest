from textual import events
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

class MainMenuScreen(Screen):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Button("New Game", id="new_game")
        yield Button("Quit", id="quit")
        yield Footer(id="Footer")

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.action_pause()
