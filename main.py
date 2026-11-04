import sys
import os

data_folder = os.path.join(os.path.dirname(__file__), "mark_setting", "data")
sys.path.append(data_folder)

from gui.bus_gui import run

run()

