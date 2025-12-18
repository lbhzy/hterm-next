
COLOR_MAP = {
    "color_01": "black",
    "color_02": "red",
    "color_03": "green",
    "color_04": "brown",
    "color_05": "blue",
    "color_06": "magenta",
    "color_07": "cyan",
    "color_08": "white",

    "color_09": "brightblack",
    "color_10": "brightred",
    "color_11": "brightgreen",
    "color_12": "brightbrown",
    "color_13": "brightblue",
    "color_14": "brightmagenta",
    "color_15": "brightcyan",
    "color_16": "brightwhite",
}

GOGH_THEME = {
    "name": "3024 Day",
    "author": "",
    "variant": "",
    "color_01": "#090300",
    "color_02": "#DB2D20",
    "color_03": "#01A252",
    "color_04": "#FDED02",
    "color_05": "#01A0E4",
    "color_06": "#A16A94",
    "color_07": "#B5E4F4",
    "color_08": "#A5A2A2",
    "color_09": "#5C5855",
    "color_10": "#E8BBD0",
    "color_11": "#3A3432",
    "color_12": "#4A4543",
    "color_13": "#807D7C",
    "color_14": "#D6D5D4",
    "color_15": "#CDAB53",
    "color_16": "#F7F7F7",
    "background": "#F7F7F7",
    "foreground": "#4A4543",
    "cursor": "#4A4543",
    "hash": "bd77249fbed09b950664ad60f037964b937460a870636673ceece963d62c42be"
}

def convert(data: dict) -> dict:
    """Gogh 格式配色方案转换成此项目格式"""
    theme = {
        "name": data.get("name", "Unnamed"),
        "background": data.get("background"),
        "foreground": data.get("foreground"),
        "cursor": data.get("cursor"),
    }

    for gogh_key, key in COLOR_MAP.items():
        if gogh_key in data:
            theme[key] = data[gogh_key]

    return theme


if __name__ == "__main__":
    theme = convert(GOGH_THEME)

    print("{")
    for k, v in theme.items():
        print(f"    {k!r}: {v!r},")
    print("}")
