from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Label

from textworld.formatting import wordwrap


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

    def clear(self):
        self.lines = []

    def watch_lines(self):
        label = self.query_one("#GameLogLabel", Label)
        label.update("\n".join(wordwrap(line) for line in self.lines))

    def set_lines(self, lines):
        self.lines = lines[::-1]

    def compose(self) -> ComposeResult:
        yield VerticalScroll(Label(id="GameLogLabel"), id="GameLogScroll")
