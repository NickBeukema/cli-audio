import os

from file.MusicFile import MusicFile

class MusicLibrary:
  """MusicLibrary 

  Description:
    Contains a few file directory helpers, along with the ability
    to maintain a library of files, saving them to a file,
    and loading them upon subsequent creations

  """

  LIB_SAVE_DIR = ".music-lib"
  LIB_SAVE_FILENAME = "library-save"

  def __init__(self):
    self.songLibrary = []

    if not os.path.exists(MusicLibrary.LIB_SAVE_DIR):
      os.makedirs(MusicLibrary.LIB_SAVE_DIR)
      f = self._openSaveFile("w+")
      f.close()
    else:
      self._loadSaveFile()


  def getList(self):
    """Getter for the songLibrary list

    Args:
      None
    
    Returns:
      List: The current list of files within the library
    """

    return self.songLibrary

  def getCurrentDirectoryFiles(self, path):
    """Given a directory, returns all files within it

    Args:
      path (str): A path of a directory 
    
    Returns:
      List: The list of files within the given directory
    """
    files = os.listdir(path)

    # Make sure to prepend the directory passed to each file so
    # that the correct relative path is provided to the caller
    fileListing = list(map(lambda file: (file, os.path.isdir(path + "/" + file)) ,files))
    fileListing.append(("..", True))
    return fileListing

  def registerSong(self, path):
    """Registers a song with the library, making sure to check
       if it already exists

    Args:
      path (str): A path of a music file
    
    Returns:
      None
    """

    musicFile = MusicFile(path)

    if musicFile.getAbsolutePath() not in list(map(lambda f: f.getAbsolutePath(), self.songLibrary)):
      self.songLibrary.append(musicFile)
      self._writeLibraryToFile()


  def _openSaveFile(self, mode):
    """Private method to open the save file in a designated mode
       (eg: r, w+, etc)
    Args:
      mode (str): mode to open the file in
    
    Returns:
      File: the open file, make sure to close it!
    """

    return open(MusicLibrary.LIB_SAVE_DIR + "/" + MusicLibrary.LIB_SAVE_FILENAME, mode)

  def _loadSaveFile(self):
    """Private method to load the save file into the library, by
       opening the file and loading each relative path into 
       the system by calling registerSong

    Args:
      None
    
    Returns:
      None
    """

    f = self._openSaveFile("r")
    contents = f.read()
    f.close

    # Split on new line and filter out any blanks
    lines = list(filter(None, contents.split("\n")))

    # For each line, split on comma and grab first element, being 
    # the relative filepath
    for line in lines:
      lineContents = line.split(",")

      relativeFilepath = lineContents[0]

      # Check to make sure the file still exists, this
      # is handy in case the file has been moved since
      # opening
      if os.path.exists(relativeFilepath):

        # Add in the song, just as it would be loaded from
        # the frontend
        self.registerSong(relativeFilepath)
  

  def _writeLibraryToFile(self):
    """Private method to write the current library to the save file

    Args:
      None
    
    Returns:
      None
    """
    file = self._openSaveFile("w+")

    for musicFile in self.songLibrary:
      lineContents = musicFile.getRelativeFilepath() + "," + musicFile.getAbsolutePath() + "," + musicFile.getFilename()
      file.write(lineContents + "\n")

    file.close()

