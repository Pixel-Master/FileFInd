# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2023 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Main Source File, execute this for running File Find

# Imports
import logging

# PyQt6 Gui Imports
from PyQt6.QtWidgets import QApplication

# Projects Library
import FF_Files
import FF_Main_UI

if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.DEBUG,
                        format='File Find [%(pathname)s] at %(asctime)s, %(levelname)s: %(message)s',
                        force=True)

    logging.info(f"Launching File Find with Version {FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]...\n")

    # Creating QApplication
    app = QApplication([])

    # File Operation
    FF_Files.setup()
    FF_Files.cache_test(is_launching=True)

    # Launches the Main Window
    FF_Main_UI.Main_Window()

    app.setQuitOnLastWindowClosed(False)
    app.exec()
    logging.info("Closed.")
