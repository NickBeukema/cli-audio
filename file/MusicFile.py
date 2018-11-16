import os

class MusicFile:
  """MusicFile

  Description:
    A basic wrapper for a file, containing
    filename, relative path, and absolute path

  """

  def __init__(self, relativeFilepath):
    self.relativeFilepath = relativeFilepath
    self.absoluteFilepath = os.path.realpath(relativeFilepath)
    self.filename = os.path.basename(relativeFilepath)

  def getAbsolutePath(self):
    """A getter for absoluteFilepath

    Args:
      None

    Returns:
      str: The absolute filepath of the file

    """
    return self.absoluteFilepath

  def getFilename(self):
    """A getter for filename

    Args:
      None

    Returns:
      str: The base filename

    """
    return self.filename

  def getRelativeFilepath(self):
    """A getter for relativeFilepath

    Args:
      None

    Returns:
      str: The relative filepath of the file

    """
    return self.relativeFilepath