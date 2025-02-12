from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Label


class GameLog(Widget):
    CSS = """
    GameLogScroll {
        height: 100%;
    }
    """
    classes = "box"
    lines = reactive([])

    def write_line(self, line):
        self.lines = self.lines + [line]

    def watch_lines(self):
        label = self.query_one("#GameLogLabel", Label)
        label.update("\n----------------\n".join(self.lines))

    def compose(self) -> ComposeResult:
        yield VerticalScroll(Label(id="GameLogLabel"), id="GameLogScroll")
