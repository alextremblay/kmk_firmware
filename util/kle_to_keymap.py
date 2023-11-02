"""
This tool takes in a http://www.keyboard-layout-editor.com/ JSON file and outputs a keymap.py file.
Legends on corners are used to indicate layers, and legends on keys are used to indicate keycodes.
This current implementation is designed for QMK-style "TRI-LAYER" keymaps (aka combo layers), 
where the layer names are assumed to be "base", "lower", "raise", and "adjust".
for each key in KLE:
the bottom-left legend is mapped to the "base" layer,
the bottom-right legend is mapped to the "lower" layer,
the top-left legend is mapped to the "raise" layer, 
the top-right legend is mapped to the "adjust" layer,
"""
import json
from pathlib import Path
import tempfile
from textwrap import dedent
from dataclasses import dataclass
import sys
import subprocess

if len(sys.argv) > 1:
    if sys.argv[1] == '-h':
        print(__doc__)
        sys.exit(0)
    json_file = Path(sys.argv[1])
else:
    json_file = Path('kle.json')

assert json_file.exists(), f'File {json_file} does not exist'

def calculate_row_width():
    for row in json.loads(json_file.read_text()):
        if not isinstance(row, list):
            continue
        return len([key for key in row if isinstance(key, str)])
    raise ValueError('Could not determine row width')

row_width = calculate_row_width()

tmpdir = Path('/tmp/kle_to_keymap')
tmpdir.mkdir(exist_ok=True)
tmpdir.joinpath('package.json').write_text(dedent("""
    {
    "name": "kle-parser",
    "version": "1.0.0",
    "main": "index.js",
    "scripts": {
        "index.js": "node index.js"
    },
    "dependencies": {
        "@ijprest/kle-serial": "^0.15.1"
    }
    }
    """))
tmpdir.joinpath('index.js').write_text(dedent("""
    var kle = require("@ijprest/kle-serial");
    var fs = require('fs');
    var data = fs.readFileSync(0, 'utf-8');
    var keyboard = kle.Serial.parse(data);

    console.log(JSON.stringify(keyboard.keys));
    """))

try:
    if not tmpdir.joinpath('node_modules').exists():
        subprocess.run(["npm", "install"], check=True, cwd=tmpdir)
    normalized_json = subprocess.run(
        ["npm", "run", "index.js"],
        input=json_file.read_text(),
        capture_output=True,
        text=True,
        check=True,
        cwd=tmpdir,
    ).stdout
    normalized_json = normalized_json.splitlines()[-1]
except subprocess.CalledProcessError as e:
    print(e.stderr)
    sys.exit(1)

keys = json.loads(normalized_json)

keys = (key['labels'] for key in keys)

def normalize_labels(keys):
    for key in keys:
        # pad each list of labels out to 12 elements
        key.extend([''] * (12 - len(key)))
        # replace each None with an empty string
        key = [x if x is not None else '' for x in key]
        yield key

keys = normalize_labels(keys)

layer_map = {
    # maps layer names to the legend index from which they pull their keys
    # legends are indexed as follows:
    # +-----------+
    # | 0 | 1 | 2 | Top row
    # | 3 | 4 | 5 | Middle row
    # | 6 | 7 | 8 | Bottom row
    # | 9 |10 |11 | Front face
    # +-----------+
    'base': 4, # center legend 
    'lower': 6, # bottom-left legend
    'raise': 2, # top-right legend
    'adjust': 8, # bottom-right legend
}

layers = {
    "base": [],
    "lower": [],
    "raise": [],
    "adjust": [],
}
        

def map_key(lkey, layer, index):
    """Map each key string from KLE into a valid KC keycode"""
    _row_offset = index % row_width
    if _row_offset <= (row_width / 2):
        # left hand
        side = "L"
    else:
        # right hand
        side = "R"
    match lkey:
        case "":
            if layer == 'base':
                return "NO"
            else:
                return "TRNS"
        case "Lower":
            return "MO(1)"
        case "Raise":
            return "MO(2)"
        case "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "0":
            return f"N{lkey}"
        case "Ctrl" | "Control" | "⌃" | "^":
            return f"{side}CTL"
        case "Alt" | "Option" | "Opt" | "⌥":
            return f"{side}ALT"
        case "Shift" | "⇧" | "⇪":
            return f"{side}SFT"
        case "GUI" | "Cmd" | "⌘" | "Win" | "❖":
            return f"{side}GUI"
        case "Hyper" | "⌃⌥⇧⌘" | "✦" | "✧":
            return "HYPR"
        case "Meh" | "⌃⌥⇧" | "◆":
            return "MEH"
        case "App" | "Menu" | "▤" | "☰":
            return "APP"
        case "Tab" | "⇥" | "↹":
            return "TAB"
        case "Bksp" | "⌫":
            return "BSPC"
        case "Del" | "⌦":
            return "DEL"
        case "Enter" | "⏎" | "↩":
            return "ENTER"
        case "Esc" | "⎋":
            return "ESC"
        case "Space" | "␣":
            return "SPC"
        case "PgUp" | "⇞":
            return "PGUP"
        case "PgDn" | "⇟":
            return "PGDN"
        case "Home" | "↖" | "⤒":
            return "HOME"
        case "End" | "↘" | "⤓":
            return "END"
        case "Left" | "←" | "⇠":
            return "LEFT"
        case "Right" | "→" | "⇢":
            return "RIGHT"
        case "Up" | "↑" | "⇡":
            return "UP"
        case "Down" | "↓" | "⇣":
            return "DOWN"
        case "-":
            return "MINS"
        case "=":
            return "EQL"
        case "[":
            return "LBRC"
        case "]":
            return "RBRC"
        case "\\":
            return "BSLS"
        case ";":
            return "SCLN"
        case "'":
            return "QUOT"
        case ",":
            return "COMM"
        case ".":
            return "DOT"
        case "`":
            return "GRV"
        case "/":
            return "SLSH"
        case "PrtSc":
            return "PSCR"
        case "Reset":
            return "RST"
        # TODO: handle numpad keys... how would i even mark these in KLE?
        # ANSI Shifted Symbols
        case "~":
            return "TILD"
        case "!":
            return "EXLM"
        case "@":
            return "AT"
        case "#":
            return "HASH"
        case "$":
            return "DLR"
        case "%":
            return "PERC"
        case "^":
            return "CIRC"
        case "&":
            return "AMPR"
        case "*":
            return "ASTR"
        case "(":
            return "LPRN"
        case ")":
            return "RPRN"
        case "_":
            return "UNDS"
        case "+":
            return "PLUS"
        case "{":
            return "LCBR"
        case "}":
            return "RCBR"
        case "|":
            return "PIPE"
        case ":":
            return "COLN"
        case '"':
            return "DQUO"
        case "<":
            return "LABK"
        case ">":
            return "RABK"
        case "?":
            return "QUES"

        # Media Keys
        case "Mute" | "🔇":
            return "MUTE"
        case "Vol-" | "🔉":
            return "VOLD"
        case "Vol+" | "🔊":
            return "VOLU"
        case "Play" | "▶" | "⏯":
            return "MPLY"
        case "Stop" | "⏹":
            return "MSTP"
        case "Prev" | "⏮":
            return "MPRV"
        case "Next" | "⏭":
            return "MNXT"
        case "Rew" | "⏪":
            return "MREW"
        case "Ffwd" | "⏩":
            return "MFFD"
        case "Eject" | "⏏":
            return "EJCT"
        case "🔅":
            return "BRID"
        case "🔆":
            return "BRIU"
        case _:
            # as a fallback, and KMK keycode can be specficied directly
            return lkey.upper()


for index, labels in enumerate(keys):
    for layer in layer_map:
        key = labels[layer_map[layer]]
        key = map_key(key, layer, index)
        layers[layer].append(key)

# Now we render this data into a keymap.py file
layers_s = "\n"
for layer in layers:
    layers_s += f"        [ # {layer}\n"
    for index, key in enumerate(layers[layer]):
        _row_offset = index % row_width
        if _row_offset == 0:
            layers_s += "            "
        if _row_offset == (row_width / 2):
            layers_s += "            "
        if key == "TRNS":
            layers_s += "___,      "
        else:
            layers_s += "{:10}".format(f"KC.{key}, ")
        if _row_offset == row_width-1:
            layers_s += "\n"
    layers_s += "        ],\n"
keymap_s = f"""
from kmk.keys import KC

___ = KC.TRNS

def get_keymap():
    return [
        # fmt: off
        {layers_s}
        # fmt: on
    ]
"""
Path('keymap.py').write_text(keymap_s)
print("Done!")
