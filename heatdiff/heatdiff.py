import argparse
import os
from contextlib import ExitStack
from typing import List, BinaryIO

from rich.segment import Segment

from textual.app import App
from textual.geometry import Size
from textual.scroll_view import ScrollView
from textual.strip import Strip


class HeatDiffContent(ScrollView):

    def __init__(self, files: List[BinaryIO]):
        super().__init__()
        self.files = files
        self.files[0].seek(0, os.SEEK_END)
        self.virtual_size = Size(10 + len(self.files) * 3 , self.files[0].tell())
    
    def render_line(self, y: int) -> Strip:
        scroll_x, scroll_y = self.scroll_offset
        y += scroll_y
        segments = [Segment(f"0x{y:04x}")]
        for file in self.files:
            file.seek(y)
            segments.append(Segment(" "))
            segments.append(Segment(file.read(1).hex()))
        return Strip(segments)


class HeatDiffApp(App):

    def __init__(self, files):
        super().__init__()
        self.files = files

    def compose(self):
        yield HeatDiffContent(self.files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()

    with ExitStack() as stack:
        files = [stack.enter_context(open(fname, "rb")) for fname in args.files]
        HeatDiffApp(files).run()
