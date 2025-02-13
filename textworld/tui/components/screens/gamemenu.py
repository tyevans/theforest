from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header


class GameMenuScreen(Screen):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("escape", "dismiss_menu", "Close Menu"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(id="Header")
        yield Button("New Game", id="new_game")
        yield Button("Quit", id="quit")
        yield Footer(id="Footer")
