print("Starting...")

from kb import KMKKeyboard
from kmk.modules.layers import Layers
from kmk.extensions.display import Display, TextEntry, SSD1306
from kmk.extensions.media_keys import MediaKeys
from keymap import get_keymap
from kmk.keys import KC, Key

keyboard = KMKKeyboard()

keyboard.debug_enabled = False
keyboard.tap_time = 750

combo_layers = {
    (1, 2): 3,
}
layers = Layers(combo_layers)

display = Display(
    SSD1306(keyboard.i2c, device_address=0x3C),
    width=128,
    height=64,
)

for layer_num, layer in enumerate(['Base', 'Lower', 'Raise', 'Adjust']):
    t = TextEntry(text = f"Layer: {layer}", layer=layer_num)
    display.entries.append(t)

display_state = TextEntry("", y=15)

def update_display_state(msg: str, key: Key, keyboard: KMKKeyboard, *args):
    display_state.text = msg
    display.render(keyboard.active_layers[0])
    return True

display.entries.append(display_state)
keyboard.extensions = [MediaKeys(), display]
keyboard.modules.append(layers)

keyboard.keymap = get_keymap()
KC.LSFT.before_press_handler(lambda key, keyboard, *args: update_display_state("Shift", key, keyboard, *args)) # type: ignore
KC.LSFT.before_release_handler(lambda key, keyboard, *args: update_display_state("", key, keyboard, *args)) # type: ignore

if __name__ == '__main__':
    keyboard.go()
