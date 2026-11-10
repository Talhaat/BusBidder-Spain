import sys
import os
import logging

# Let Python find the program code in the busbidder/ folder
code_folder = os.path.join(os.path.dirname(__file__), "busbidder")
sys.path.append(code_folder)

# Write important events and rejected data rows to busbidder.log
log_path = os.path.join(os.path.dirname(__file__), "busbidder.log")
logging.basicConfig(filename=log_path, level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

from gui.bus_gui import run

run()

