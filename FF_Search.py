# This source file is a part of File Find made by Pixel-Master
#
# Copyright 2022-2023 Pixel-Master
#
# This software is licensed under the "GPLv3" License as described in the "LICENSE" file,
# which should be included with this package. The terms are also available at
# http://www.gnu.org/licenses/gpl-3.0.html

# This file contains the code for the search engine

# Imports
import logging
import os
from fnmatch import fnmatch
from pickle import dump, load
from sys import exit
from time import perf_counter, mktime

# PyQt6 Gui Imports
from PyQt6.QtCore import QThreadPool, pyqtSignal, QObject
from PyQt6.QtWidgets import QFileDialog, QDateEdit, QWidget

# Projects Libraries
import FF_Additional_UI
import FF_Files
import FF_Main_UI
import FF_Search_UI


# Sorting algorithms
class sort:

    # Sort by Size
    @staticmethod
    def size(file):
        return FF_Files.get_file_size(file)

    # Sort by Name
    @staticmethod
    def name(file):
        try:
            return os.path.basename(file)
        except FileNotFoundError:
            return -1

    # Sort by Date Modified
    @staticmethod
    def m_date(file):
        try:
            return os.path.getmtime(file)
        except FileNotFoundError:
            return -1

    # Sort by Date Created
    @staticmethod
    def c_date(file):
        try:
            # Using os.stat because os.path.getctime returns a wrong date
            return os.stat(file).st_birthtime
        except FileNotFoundError:
            return -1


# Class for Generating the terminal command
class generate_terminal_command:
    def __init__(self, name: str, name_contains: str, file_ending: str, fn_match: str):
        self.shell_command = f"find {os.getcwd()}"
        self.name_string = ""
        if name != "":
            self.name_string += f"{name}"
        elif fn_match != "":
            self.name_string = fn_match

        else:
            if name_contains != "":
                self.name_string += f"*{name_contains}*"
            if file_ending != "":
                self.name_string += f"*.{file_ending}"

        if self.name_string != "":
            self.shell_command += f" -name \"{self.name_string}\""

        # Debug
        logging.info(f"Command: {self.shell_command}")

    def __str__(self):
        return self.shell_command


# Loading a saved search
class load_search:
    def __init__(self, parent):
        load_dialog = QFileDialog.getOpenFileName(parent, "Export File Find Search", FF_Files.SAVED_SEARCHES_FOLDER,
                                                  "*.FFSave;")
        load_file = load_dialog[0]

        # Creating Cache File, because of the Reload Button
        if load_file != "":
            with open(load_file, "rb") as OpenedFile:
                saved_file_content = load(OpenedFile)
                if not os.path.exists(
                        os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                     f"loaded from {load_file}.FFSearch".replace("/", "-"))):
                    with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                           f"loaded from {load_file}.FFCache".replace("/", "-")),
                              "wb") as CachedSearch:
                        dump(saved_file_content, file=CachedSearch)
                FF_Search_UI.Search_Window(*[0, 0, 0, 0, saved_file_content, f"loaded from {load_file}", parent])


# The Search Engine
class search:
    def __init__(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                 data_search_for, data_search_from_valid, data_search_from_unproofed, data_content, data_edits_list,
                 data_sort_by, data_reverse_sort, data_fn_match, parent: QWidget):
        # Debug
        logging.debug("Converting Date-times...")

        """
        Converting Date-times
        Converting the output of QDateEdit into the unix time by first using QDateEdit.date() to get
        something like this: QDate(1,3,2000), after that using QDate.toPyDate to get this: 1-3-2000,
        than we can use .split("-") to convert 1-3-2000 into a list [1,3,2000], after that we use time.mktime
        to get the unix time format that means something like, that: 946854000.0, only to match this with
        os.getctime, what we can use to get the creation date of a file.

        Yes it would be easier if Qt had a function to get the unix time
        """
        unix_time_list = []

        def conv_qdate_to_unix_time(input_edit: QDateEdit, pos: int = 1):
            time_list = str(input_edit.date().toPyDate()).split("-")
            unix_time = mktime(
                (int(time_list[0]), int(time_list[1]), int(time_list[2]) + pos, 0, 0, 0, 0, 0, 0))
            return unix_time

        for time_drop_down in data_edits_list:
            time_to_add_to_time_list = conv_qdate_to_unix_time(time_drop_down,
                                                               data_edits_list.index(time_drop_down) % 2)
            unix_time_list.append(time_to_add_to_time_list)

        # Fetching Errors
        # Name contains and Name can't be used together
        if data_name != "" and data_in_name != "" or data_name != "" and data_filetype != "":
            # Debug
            logging.error("Name Error! File Name and Name contains or File Type can't be used together!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("NAME ERROR!",
                                                          "Name Error!\n\nFile Name and in Name or File Type can't "
                                                          "be used together",
                                                          parent=None)

        # Directory not valid
        elif data_search_from_valid != data_search_from_unproofed and not os.path.isdir(data_search_from_unproofed):
            # Debug
            logging.error("Directory Error! Given directory is not a valid folder!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("Directory Error!",
                                                          "Directory Error!\n\nGiven directory is not a valid folder!",
                                                          parent=None)

        # File Size max must be larger than File Size min
        elif data_file_size_min >= data_file_size_max and not data_file_size_min == data_file_size_max:
            # Debug
            logging.error("Size Error! File Size min is larger than File Size max!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("SIZE ERROR!",
                                                          "Size Error!\n\nFile Size min is larger than File Size max!",
                                                          parent=None)

        # First Date must be earlier than second Date
        elif unix_time_list[0] >= unix_time_list[1] or unix_time_list[2] >= unix_time_list[3]:
            # Debug
            logging.error("Date Error! First Date is later than second Date!")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("DATE ERROR!",
                                                          "Date Error!\n\nFirst Date is later than second Date!",
                                                          parent=None)

        # Search in System Files disabled, but Search path is in library Folder
        elif not data_library and "/Library" in data_search_from_valid or data_search_from_valid.startswith("/System"):
            # Debug
            logging.error("System Files Error! Search in System Files disabled, but Directory is in Library Folder")

            # Show Popup
            FF_Additional_UI.msg.show_critical_messagebox("System Files Error!",
                                                          "System Files Error!\n\nSearch in System Files disabled,"
                                                          " but Search path is in library Folder!",
                                                          parent=None)

        # QMessageBox to confirm searching
        elif not FF_Additional_UI.msg.show_search_question(parent):
            logging.info("Cancelled Searching!")

        # Start Searching
        else:

            # Updating ACTIVE_SEARCH_THREADS
            global ACTIVE_SEARCH_THREADS
            ACTIVE_SEARCH_THREADS += 1

            # Defining menubar log
            self.ui_logger = FF_Main_UI.search_update(lambda: exit(0), data_search_from_valid)

            # Testing Cache
            FF_Files.cache_test(is_launching=False)

            # Starting
            logging.info("Starting Search...")
            logging.debug(f"Running Threads: {ACTIVE_SEARCH_THREADS}")

            # Setting up QThreadPool
            self.ui_logger.update("Setting up Thread...")
            logging.debug("Setting up QThreadPool...")

            # Creating Qt Signal
            class signals_class(QObject):
                finished = pyqtSignal()

            # Defining thread
            self.thread = QThreadPool(parent)

            # Setup pyqt Signal
            self.signals = signals_class()
            # Debug
            self.signals.finished.connect(lambda: logging.info("Finished Search Thread!\n"))
            # Launching UI
            self.signals.finished.connect(lambda: FF_Search_UI.Search_Window(*SEARCH_OUTPUT))
            # Updating Status Indicator
            self.signals.finished.connect(FF_Main_UI.Main_Window.update_search_status_label)

            # Starting the Thread
            self.thread.start(
                lambda: self.searching(data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max,
                                       data_library, data_search_from_valid, data_search_for, data_content,
                                       unix_time_list, data_sort_by, data_reverse_sort, data_fn_match, parent))

            # Debug
            logging.debug("Finished Setting up QThreadPool!")

    # The search engine
    def searching(self, data_name, data_in_name, data_filetype, data_file_size_min, data_file_size_max, data_library,
                  data_search_from, data_search_for, data_content, data_time, data_sort_by, data_reverse_sort,
                  data_fn_match, parent):
        # Debug
        logging.info("Starting Search...")
        self.ui_logger.update("Starting Search...")

        # Creates empty lists for the files
        matched_path_list = []
        found_path_list = []

        # Saving time before scanning
        time_before_start = perf_counter()

        # Lower Arguments
        data_name = data_name.lower()
        data_in_name = data_in_name.lower()
        data_filetype = data_filetype.lower()

        # Checking if data_time is needed
        DEFAULT_TIME_INPUT_LIST = [946681200.0, 946767600.0, 946681200.0, 946767600.0]
        if data_time == DEFAULT_TIME_INPUT_LIST:
            data_time_needed = False
        else:
            data_time_needed = True

        # Checking if data_search_for is needed
        if data_search_for == "All Files and Folders":
            data_search_for_needed = False
        else:
            data_search_for_needed = True

        # Loading excluded files
        with open(os.path.join(FF_Files.FF_LIB_FOLDER, "Settings"), "rb") as ExcludedFile:
            data_excluded_files = load(ExcludedFile)["excluded_files"]

        if not data_excluded_files:
            data_excluded_files_needed = False

        else:
            data_excluded_files_needed = True

        # Debug
        logging.info("Starting Scanning...")
        self.ui_logger.update("Scanning...")

        '''Checking, if Cache File exist, if not it goes through every file in the directory and saves it. If It
        exist it loads the Cache File in to found_path_list '''
        if os.path.exists(
                os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache")):
            logging.info("Scanning using cached Data..")
            with open(
                    os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache"),
                    "rb") as SearchResults:
                found_path_list = load(SearchResults)

        else:
            for (roots, dirs, files) in os.walk(data_search_from):
                for file in files:
                    found_path_list.append(os.path.join(roots, file))
                for directory in dirs:
                    found_path_list.append(os.path.join(roots, directory))

        # Saves time
        time_after_searching = perf_counter() - time_before_start

        # Debug
        logging.info("Starting Indexing...")
        self.ui_logger.update("Indexing...")

        # Applies filters, when they don't match the function returns False, else True
        def check_file(found_file):

            # Looks for basename to be faster
            basename = os.path.basename(found_file)
            lower_basename = os.path.basename(found_file).lower()

            # Name
            if data_name != "":
                if data_name != lower_basename:
                    return False

            # In name
            if data_in_name != "":
                if not (data_in_name in lower_basename):
                    return False

            # File Ending
            if data_filetype != "":
                if not lower_basename.endswith(f".{data_filetype}"):
                    return False

            # Fn match
            if data_fn_match != "":
                if not fnmatch(basename, data_fn_match):
                    return False

            # Search in System Files
            if not data_library:
                if "/Library" in found_file or found_file.startswith("/System"):
                    return False

            # Search for Folders and Files
            if data_search_for_needed:
                # Checks for Directories
                if data_search_for == "only Files":
                    if os.path.isdir(found_file):
                        return False
                # Checks for Files
                elif data_search_for == "only Folders":
                    if os.path.isfile(found_file):
                        return False

            # Search for Date Modified, Created
            # Checking if File Date is between Filter Dates
            if data_time_needed:
                # Using os.stat because os.path.getctime returns a wrong date
                try:
                    file_c_time = os.stat(found_file).st_birthtime
                    file_m_time = os.path.getmtime(found_file)
                except FileNotFoundError:
                    return False
                # Checking for file time and which values in data_time are modified
                if data_time[0] <= file_c_time <= data_time[1] != DEFAULT_TIME_INPUT_LIST[1]:
                    pass
                elif data_time[0] != DEFAULT_TIME_INPUT_LIST[0] and data_time[1] != DEFAULT_TIME_INPUT_LIST[1]:
                    return False
                if data_time[2] <= file_m_time <= data_time[3] != DEFAULT_TIME_INPUT_LIST[3]:
                    pass
                elif data_time[3] != DEFAULT_TIME_INPUT_LIST[3] and data_time[2] != DEFAULT_TIME_INPUT_LIST[2]:
                    return False

            # Filter File Size
            if data_file_size_min != "" and data_file_size_max != "":
                if not (float(data_file_size_max) * 1000000) \
                       >= int(FF_Files.get_file_size(found_file)) \
                       >= (float(data_file_size_min) * 1000000):
                    return False

            # Contains
            if data_content != "":
                does_contain = False
                try:
                    with open(found_file, "r") as ContentFile:
                        for line in ContentFile:
                            if data_content in line:
                                does_contain = True
                                break
                    if not does_contain:
                        return False
                except (UnicodeDecodeError, FileNotFoundError, OSError):
                    return False
                else:
                    if not does_contain or os.path.isdir(found_file):
                        return False

            # Filter some unnecessary System Files
            if basename == ".DS_Store" or basename == ".localized" or basename == "desktop.ini" \
                    or basename == "Thumbs.db":
                return False

            # Excluded Files
            if data_excluded_files_needed:
                for excluded_file in data_excluded_files:
                    if found_file.startswith(excluded_file):
                        return False

            # Return True to add the File to matched_path_list
            return True

        # Looping through every file
        for scanned_file in found_path_list:
            add_file = check_file(scanned_file)
            if add_file:
                matched_path_list.append(scanned_file)

        # Prints out seconds needed
        logging.info(f"Found {len(matched_path_list)} Files and Folders")

        # Saving time
        time_after_indexing = perf_counter() - (time_after_searching + time_before_start)

        # Sorting
        if data_sort_by == "File Name":
            logging.info("Sorting List by Name...")
            self.ui_logger.update("Sorting List by Name...")
            matched_path_list.sort(key=sort.name, reverse=data_reverse_sort)

        elif data_sort_by == "File Size":
            logging.info("Sorting List by Size...")
            self.ui_logger.update("Sorting List by Size...")
            matched_path_list.sort(key=sort.size, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Created":
            logging.info("Sorting List by creation date...")
            self.ui_logger.update("Sorting List by creation date...")
            matched_path_list.sort(key=sort.c_date, reverse=not data_reverse_sort)

        elif data_sort_by == "Date Modified":
            logging.info("Sorting List by modification date...")
            self.ui_logger.update("Sorting List by modification date...")
            matched_path_list.sort(key=sort.m_date, reverse=not data_reverse_sort)

        else:
            logging.info("Skipping Sorting")
            self.ui_logger.update("Skipping Sorting...")
            if data_reverse_sort:
                logging.debug("Reversing Results...")
                matched_path_list = list(reversed(matched_path_list))

        # Caching Results with pickle
        # Testing if cache file exist, if it doesn't exist it caches scanned files
        if not os.path.exists(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER,
                                           data_search_from.replace("/", "-") + ".FFCache")):
            # Debug and menubar logg
            logging.info("Saving Search Results...")
            self.ui_logger.update("Saving Search Results...")

            # Creating file
            with open(os.path.join(FF_Files.CACHED_SEARCHES_FOLDER, data_search_from.replace("/", "-") + ".FFCache"),
                      "wb") as resultFile:
                # Dumping with pickle
                dump(list(found_path_list), resultFile)

        else:
            logging.info("Cache file already exist, skipping caching...")

        # Calculating time
        time_after_sorting = perf_counter() - (time_after_indexing + time_after_searching + time_before_start)
        time_total = perf_counter() - time_before_start

        # Debug
        logging.info("Finished Searching!")
        self.ui_logger.update("Building UI...")

        global SEARCH_OUTPUT
        SEARCH_OUTPUT = [time_total, time_after_searching, time_after_indexing, time_after_sorting, matched_path_list,
                         data_search_from, parent]

        # Starting the UI with the emitted signal
        self.signals.finished.emit()

        # Updating Thread count
        global ACTIVE_SEARCH_THREADS
        ACTIVE_SEARCH_THREADS -= 1


# Global Variables for Search Threads
SEARCH_OUTPUT: [float, float, float, float, list, str, QWidget] = []

ACTIVE_SEARCH_THREADS: int = 0
