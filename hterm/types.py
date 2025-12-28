from typing import TypedDict


class CommandItem(TypedDict):
    name: str
    type: str
    content: str


class QuickConfig(TypedDict):
    command: list[CommandItem]
