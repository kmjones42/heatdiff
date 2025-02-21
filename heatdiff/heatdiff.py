import argparse
import functools
import operator
import os
from contextlib import ExitStack
from typing import List, BinaryIO

from rich.segment import Segment
from rich.style import Style

from textual.app import App
from textual.containers import Container, Horizontal, Vertical
from textual.geometry import Size
from textual.scroll_view import ScrollView
from textual.strip import Strip
from textual.widgets import Button, Label, RadioButton, RadioSet, Static
from textual.widget import Widget

class HeatDiffContent(ScrollView):

    def __init__(self, files: List[BinaryIO]):
        super().__init__()
        self.files = files
        self.files[0].seek(0, os.SEEK_END)
        self.virtual_size = Size(10 + len(self.files) * 3 , self.files[0].tell())
    
    def render_line(self, y: int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        y += scroll_y
        file_vals = []
        for file in self.files:
            file.seek(y)
            file_vals.append(file.read(1).hex())
        
        address_segment = Segment(f"0x{y:04x}", Style(color="red"))  if functools.reduce(operator.eq, file_vals) else Segment(f"0x{y:04x}")
        segments = [address_segment]
        
        for val in file_vals:
            segments.append(Segment(" "))
            segments.append(Segment(val))

        return Strip(segments)


class FileSelector(Container):

    def compose(self):
        yield Static("Test")

class Settings(Widget):

    def compose(self):
        with Vertical():
            yield Label("Settings:", id="settings-label")
            with Horizontal():
                yield Label("Size:")
                with RadioSet(id="size-select"):
                    yield RadioButton("4")
                    yield RadioButton("8", value=True)
                    yield RadioButton("16")
                    yield RadioButton("32")
            with Horizontal():
                yield Label("Display:")
                with RadioSet(id="display-select"):
                    yield RadioButton("hex", value=True)
                    yield RadioButton("bin")


class CollapsibleSidebar(Container):

    def __init__(self):
        super().__init__()
        self.collapsed = True


    def compose(self):
        yield Button("❮", id="toggle-btn")
        # yield Static("Collapsible Content", id="content")
        with Vertical():
            yield FileSelector()
            yield Static("Hello", id="content")
            yield Settings(id="settings")

    def on_mount(self):
        self.styles.width = 3
        self.query_one("#content").styles.width = 0

    def on_button_pressed(self, event: Button.Pressed):
        self.toggle_sidebar()

    def toggle_sidebar(self):
        self.collapsed = not self.collapsed

        content = self.query_one("#content")
        button = self.query_one("#toggle-btn")
        if self.collapsed:
            content.styles.animate("width", value=0, duration=0.5)
            self.styles.animate("width", value=3, duration=0.5)
            button.label = "❮"
        else:
            content.styles.animate("width", value=30, duration=0.5)
            self.styles.animate("width", value=(33), duration=0.5)
            button.label = "❯"

class HeatDiffApp(App):
    CSS="""
    CollapsibleSidebar {
        layout: horizontal;
        align: right middle;
    }

    #toggle-btn {
        width: 3;
        min-width: 3;
        max-width: 3;
        height: 100%;
        dock: left;
    }

    #content {
        background: #444;
        color: white;
    }

    #settings {
        height: 50%;
        align: center bottom;
    }
    """

    def __init__(self, files):
        super().__init__()
        self.files = files

    def compose(self):
        with Horizontal():
            yield HeatDiffContent(self.files)
            yield CollapsibleSidebar()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    with ExitStack() as stack:
        files = [stack.enter_context(open(fname, "rb")) for fname in args.files]
        HeatDiffApp(files).run()
