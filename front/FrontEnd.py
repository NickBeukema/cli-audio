import curses
import curses.textpad

from error.CliAudioFileException import CliAudioFileException
from error.CliAudioScreenSizeException import CliAudioScreenSizeException

from library.MusicLibrary import MusicLibrary

import os

class FrontEnd:

    MIN_HEIGHT=20
    MIN_WIDTH=95

    def __init__(self, player, file):
        self.player = player
        self.library = MusicLibrary()

        # Save off file to process through the
        # default music playing pipeline
        self.initialFile = file


        try:
            curses.wrapper(self.menu)

        except CliAudioScreenSizeException:

            # Alert user if the screen size is too small
            screen_size =  str(FrontEnd.MIN_WIDTH) + "x" + str(FrontEnd.MIN_HEIGHT)
            print("Screen size too small, the minimum dimensions supported are " + screen_size)

    def menu(self, args):
        self.stdscr = curses.initscr()


        height,width = self.stdscr.getmaxyx()

        # Raise custom exception if screen size is too small
        if height < FrontEnd.MIN_HEIGHT or width < FrontEnd.MIN_WIDTH:
            raise CliAudioScreenSizeException


        self.stdscr.border()
        self.stdscr.addstr(0,0, "cli-audio",curses.A_REVERSE)
        self.stdscr.addstr(5,10, "c - Change current song")
        self.stdscr.addstr(6,10, "p - Play/Pause")
        self.stdscr.addstr(7,10, "l - Library")
        self.stdscr.addstr(9,10, "ESC - Quit")

        # Funnel the initial file chosen into the
        # song choosing process
        self.chooseSong(self.initialFile)

        self.stdscr.refresh()

        while True:
            c = self.stdscr.getch()

            if c == 27:
                self.quit()

            elif c == ord('p'):
                self.player.pause()

            elif c == ord('c'):
                self.changeSong()
                self.stdscr.touchwin()
                self.stdscr.refresh()

            elif c == ord('l'):
                self.openLibrary()

    def chooseSong(self, filepath):
        """Checks the given filepath, if it is a directory, open up
           the directory in a new window, otherwise play the song!

        Args:
            filepath (str): The desired path to open
        
        Returns:
            None
        """

        # If the file is a directory, follow through
        # the directory workflow and open a window
        # with all files within that directory
        if os.path.isdir(filepath):

            self.player.stop()
            self.openDirectoryView(filepath)


        # Otherwise try to play the file
        else:
            self.player.stop()

            try:

                self.player.play(filepath)
                self.updateSong()

                self.library.registerSong(filepath)

            # Catch custom exception and display the error to the user
            # This will happen if anything other than a .wav file is chosen
            except CliAudioFileException:
                self.updatePlayText("Error loading " + self.player.getCurrentSong())


    def openLibrary(self):
        """Function that opens up a new window to display the current
           library. Gives the option to press up and down to select
           the different files

        Args:
            None
        
        Returns:
            None
        """

        # Pull library from our module
        library = self.library.getList()

        selectedIndex = 0
        libraryWindow = curses.newwin(15, 40, 3, 50)
        libraryWindow.border()
        libraryWindow.addstr(0,0, "Music Library", curses.A_REVERSE)

        # Draw out the library onto the window
        self.drawLibraryListing(libraryWindow, library, selectedIndex)

        while True:
            c = self.stdscr.getch()

            # Pressing Enter
            if c == 10:

                # Get selected file
                selectedFile = library[selectedIndex]

                # Clear window and refresh
                libraryWindow.clear()
                libraryWindow.refresh()
                del libraryWindow

                # Pass file into choose song workflow
                self.chooseSong(selectedFile.getRelativeFilepath())
                self.stdscr.refresh()
                break

            # Pressing Up
            elif c == 259:

                # Decrement and redraw listing
                if selectedIndex != 0:
                    selectedIndex -= 1
                    self.drawLibraryListing(libraryWindow, library, selectedIndex)

            # Pressing Down
            elif c == 258:

                # Increment and redraw listing
                if selectedIndex < len(library) - 1:
                    selectedIndex += 1
                    self.drawLibraryListing(libraryWindow, library, selectedIndex)

            # Pressing Escape
            elif c == 27:

                # Clear window
                libraryWindow.clear()
                libraryWindow.refresh()
                del libraryWindow

                self.stdscr.refresh()
                break

    def drawLibraryListing(self, window, files, currentSelected):
        listOfStrings = list(map(lambda file: file.getFilename(), files))
        self.drawListToWindow(window, listOfStrings, currentSelected)

    def openDirectoryView(self, fileDir):
        """Function that opens up a new window to display the given
           directory. Gives the option to press up and down to select
           the different files. Upon selectin of another directory,
           that one is then opened. Also allows for the ".." selection
           to go up a directory

        Args:
            fileDir (str): The starting directory
        
        Returns:
            None
        """

        # Use helper method to get all files within the directory
        allFiles = self.library.getCurrentDirectoryFiles(fileDir)
        selectedIndex = 0

        changeWindow = curses.newwin(15, 40, 3, 50)
        changeWindow.border()
        changeWindow.addstr(0,0, "Choose a file", curses.A_REVERSE)

        fullDirPath = fileDir

        # Draw all files within a directory
        self.drawDirectoryListing(changeWindow, allFiles, selectedIndex)

        while True:
            c = self.stdscr.getch()

            # On Enter
            if c == 10:

                # Get currently selected file
                newFile = allFiles[selectedIndex]

                # File is a tuple, the second indicy designates if it's a
                # directory
                if newFile[1]:

                    # We need to append the selected file to to current to maintain
                    # relative access. This gets a little messy if the user
                    # traverses up and down multiple times
                    fullDirPath += "/" + newFile[0]

                    # Get new directory
                    allFiles = self.library.getCurrentDirectoryFiles(fullDirPath)

                    selectedIndex = 0

                    # Draw the directory out
                    self.drawDirectoryListing(changeWindow, allFiles, selectedIndex)
                
                # Otherwise if it is a file
                else:

                    # Clear window
                    changeWindow.clear()
                    changeWindow.refresh()
                    del changeWindow
                    fullPath = fullDirPath + "/" + newFile[0]

                    # Funnel song through choose song workflow
                    self.chooseSong(fullPath)

                    break


            # On Up
            elif c == 259:

                # Decrement and redraw listing
                if selectedIndex != 0:
                    selectedIndex -= 1
                    self.drawDirectoryListing(changeWindow, allFiles, selectedIndex)

            # On Down
            elif c == 258:

                # Increment and redraw listing
                if selectedIndex < len(allFiles) - 1:
                    selectedIndex += 1
                    self.drawDirectoryListing(changeWindow, allFiles, selectedIndex)

            # On Escape
            elif c == 27:

                # Clear window
                changeWindow.clear()
                changeWindow.refresh()

                del changeWindow
                self.stdscr.refresh()
                break


    def drawDirectoryListing(self, window, files, currentSelected):
        """Helper method appends ">" to the end of the filename if
           the file ends up being a directory

        Args:
            window (curses window): The window to draw the strings to
            list (List): List of tuples with file info within them
            currentSelected (int): The index of the list in which to highlight
        """

        listOfStrings = list(map(lambda file: file[0] + (" >" if file[1] else ""), files))
        self.drawListToWindow(window, listOfStrings, currentSelected)

    def drawListToWindow(self, window, list, currentSelected):
        """Helper method that draws a list of strings to a provided
           window. Also will highlight the provided currentSelected.
           Current limitation is the window will only draw 10 items,
           this could be improved upon.

        Args:
            window (curses window): The window to draw the strings to
            list (List): List of strings to draw to the window
            currentSelected (int): The index of the list in which to highlight
        
        Returns:
            None
        """

        # Clear out the window
        for idx in range(1,14):
            window.addstr(idx, 3, "                             ")

        for idx, text in enumerate(list):

            # Currently limited to 10 items for display purposes
            if idx > 10:
                break

            # Starts two down
            displayIndex = idx + 2

            # If currently selected, output in reverse color
            if currentSelected == idx:
                window.addstr(displayIndex, 3, text, curses.A_REVERSE)
            else:
                window.addstr(displayIndex, 3, text)

        self.stdscr.refresh()
        window.refresh()


    def updateSong(self):
        self.updatePlayText("Now playing: " + self.player.getCurrentSong())

    def updatePlayText(self, text):
        self.stdscr.addstr(15,10, "                                                       ")
        self.stdscr.addstr(15,10, text)

    def changeSong(self):
        changeWindow = curses.newwin(5, 40, 5, 50)
        changeWindow.border()
        changeWindow.addstr(0,0, "What is the file path?", curses.A_REVERSE)
        self.stdscr.refresh()
        curses.echo()

        path = changeWindow.getstr(1,1, 30)
        decoded_path = path.decode(encoding="utf-8")

        curses.noecho()
        del changeWindow
        self.stdscr.touchwin()
        self.stdscr.refresh()

        self.chooseSong(decoded_path)


    def quit(self):
        self.player.stop()
        exit()
