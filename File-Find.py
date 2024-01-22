# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2024 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# Main Source File, execute this for running File Find

# Imports
import logging
import gc

# PyQt6 Gui Imports
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QFileOpenEvent
from PyQt6.QtWidgets import QApplication

# Projects Library
import FF_Files
import FF_Main_UI
import FF_Search

if __name__ == "__main__":
    # Setup Logging
    logging.basicConfig(level=logging.DEBUG,
                        format='File Find [%(pathname)s] at %(asctime)s, %(levelname)s: %(message)s',
                        force=True)

    logging.info(f"Launching File Find with Version {FF_Files.VERSION_SHORT}[{FF_Files.VERSION}]...\n")

    # Creating QApplication
    class CreateApp(QApplication):

        def event(self, event: QEvent) -> bool:
            # Executed when an event is received.
            # 116 is the event number of the QFIleOpenEvent
            file_open_event_number = 116

            # HANDLE FILEOPEN EVENT (TRIGGERED BY MACOS WHEN DOUBLE-CLICKING A FILE)
            # Testing if the event is triggered by an opened file
            if event.type() == file_open_event_number:
                # Getting the path of the file
                path = QFileOpenEvent.url(event).path()

                # If the opened file is a file find search
                if path.endswith("FFSave"):
                    # Debug
                    logging.info(f"Opening {path}...")
                    FF_Search.LoadSearch.open_file(path, None)

            return super().event(event)

    app = CreateApp([])

    # Turning of automatic garbage collection because
    gc.disable()

    # File Operation
    FF_Files.setup()
    FF_Files.cache_test(is_launching=True)

    # Launches the Main Window
    FF_Main_UI.MainWindow()

    app.setQuitOnLastWindowClosed(False)

    # Main loop for User-Interface
    app.exec()

    # Debug
    logging.info("Closed.")
