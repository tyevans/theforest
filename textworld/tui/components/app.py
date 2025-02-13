from textual.app import App
from textual.widgets import Button

from textworld.tui.components.screens.gamemenu import GameMenuScreen
from textworld.tui.components.screens.mainmenu import MainMenuScreen
from textworld.tui.components.screens.theforestgame import TheForestGameScreen


class TheForestApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]
    CSS = """
        MainMenuScreen {
            align: center middle;
        }
        
        GameMenuScreen {
            align: center middle;
        }
        """

    """The textual interface to the forest."""
    TITLE = "The Forest"

    def on_ready(self) -> None:
        self.push_screen(MainMenuScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        match button_id:
            case "new_game":
                self.start_new_game()
            case "quit":
                self.exit(0)

    def start_new_game(self):
        self.push_screen(TheForestGameScreen())

    def action_show_menu(self):
        self.push_screen(GameMenuScreen())

    def action_dismiss_menu(self):
        self.pop_screen()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )
