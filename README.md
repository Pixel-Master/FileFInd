## !! The Development for the tkinter version has stopped File Find switched to PyQT5 see: https://github.com/Pixel-Master/File-Find/tree/main !!

<p align="center">
  <img src="https://github.com/Pixel-Master/File-Find/blob/main/assets/icon.png?raw=true" height="128">
  <h1 align="center">File-Find for macOS</h1>


<h3 align="center">A macOS UI Utility that helps you find Files easier.</h3>

## Features
- Choose Filter which Files to include:
	* Name
	* In Name
	* File Ending
	* Search for Library Files
	* Directory to search in
	* File Size
	* Search for Folders
- Search for Files and export Searches

- Choose options for Files:
	* Show in Finder
	* Open
	* Copy Path/File
- Sort Results:
	* Size
	* File Name
	* Modified
	* Created
- Reverse Results

- Generate Shell command from Filters, supports:
	* Name
	* In Name
	* File Ending

## FAQ
Q: **What is File-Find and how does it work?**

A: File-Find is an open-source macOS Utility, that makes it easy to find Files. To search fill in the filters you need and leave the filters you don't need empty.

Q: **Why does File-Find crash when searching?**

A: File-Find is only using one thread. That's why it looks like File-Find "doesn't react".


## Download
### **[Version 1.0:](https://github.com/Pixel-Master/File-Find/releases/tag/v1.0.0)**
#### Changelog:

- Release

#### Downloads:

- [Mac](https://github.com/Pixel-Master/File-Find-Bot/releases/download/v1.0.0/File-Find.app.zip)
- [Building from Source](https://gitlab.com/Pixel-Mqster/File-Find/-/blob/main/README.md#running-from-source)


## Running from Source

### Note:

**File Find won't work properly on Linux or Windows, because the UI displays different depending on the OS and some Features are rel** 


### Dependencies (when running from source)
- [Python](https://python.org/) 3.6 or higher
- [Pyperclip](https://pyperclip.readthedocs.io/en/latest/) 

Install pyperclip with pip:

`pip3 install pyperclip`

### Running
1. Install dependencies
2. Run:

`python3 File-Find.py` 

## Roadmap
1. [ ] UI:
   1. [x] Filter UI
   2. [ ] Help UI
   3. [x] Search Result UI
2. [ ] Exporting and Importing Searches:
   1. [ ] Importing
   2. [x] Exporting 
3. [x] Caching:
	1. [x] Creating Caches
	2. [x] Using Caches
	3. [x] Deleting Caches
4. [ ] Multithreading:
	1. [ ] UI using different thread as Search engine
	2. [ ] Searching trough different threads
	3. [ ] Indexing trough different threads
5. [x] Sorting:
   1. [x] Size
   2. [x] File Name
   3. [x] Modified
   4. [x] Created
   5. [x] Reverse
6. [ ] Filter:
    1. [x] Name
    2. [x] In Name
    3. [x] File Ending
    4. [x] Search for Library Files
    5. [x] Directory to search in
    6. [x] Search for Folders
    7. [ ] Search for Alias
    8. [ ] Changeable:
         1. [x] Size
         2. [ ] Date Created
         3. [ ] Date Created
         4. [ ] Content
         5. [x] UI
         6. [ ] Included in Search
7. [ ] Compatible with Linux and Windows?
