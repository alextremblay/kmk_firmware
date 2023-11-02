import board

from kmk.kmk_keyboard import KMKKeyboard as _KMKKeyboard
from kmk.scanners import DiodeOrientation
import kmk.modules
from kmk.modules.split import Split


class KMKKeyboard(_KMKKeyboard):
    col_pins = (
        board.D9,
        board.D21,
        board.D23,
        board.D20,
        board.D22,
        board.D26,
        board.D27,
        board.D28,
        board.D29,
    )
    row_pins = (
        board.D0,
        board.D1,
        board.D4,
        board.D5,
        board.D6,
        board.D7,
    )
    diode_orientation = DiodeOrientation.COLUMNS
    
    coord_mapping = [
        0,  1,  2,  3,  4,  5,  6,  7,  8,   54,  55,  56,  57,  58,  59,  60,  61,  62,
        9, 10, 11, 12, 13, 14, 15, 16, 17,   63,  64,  65,  66,  67,  68,  69,  70,  71,
        18, 19, 20, 21, 22, 23, 24, 25, 26,   72,  73,  74,  75,  76,  77,  78,  79,  80,
        27, 28, 29, 30, 31, 32, 33, 34, 35,   81,  82,  83,  84,  85,  86,  87,  88,  89,
        36, 37, 38, 39, 40, 41, 42, 43, 44,   90,  91,  92,  93,  94,  95,  96,  97,  98,
        45, 46, 47, 48, 49, 50, 51, 52, 53,   99, 100, 101, 102, 103, 104, 105, 106, 107,
    ]

    modules: list[kmk.modules.Module] = [Split(data_pin=board.D2, data_pin2=board.D3, use_pio=True)]
    i2c = board.I2C()
    
