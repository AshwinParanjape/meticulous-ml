import sys
class ExitHooks(object):
    def __init__(self):
        self.exit_code = None
        self.exception = None

    def hook(self):
        """Replace sys.exit with """
        self._orig_exit = sys.exit
        sys.exit = self.exit
        sys.excepthook = self.exc_handler

    def exit(self, code=0):
        self.exit_code = code
        self._orig_exit(code)

    def exc_handler(self, exc_type, exc_value, exc_traceback):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback


class Tee(object):
    """
    Utility class that imitates a standard python file but writes to two places, stdstream and fileobject

    Based on http://shallowsky.com/blog/programming/python-tee.html
    """
    def __init__(self, stdstream, fileobject):
        """
        :param stdstream: output stream, that gets replaced by the Tee object
        :param fileobject: output file object that needs to be flushed and closed
        """
        self.file = fileobject
        self.stdstream = stdstream
        stdstream = self

    def __del__(self):
        """Close the file and set the stdstream back to the original stdstream"""
        stdstream = self.stdstream
        self.file.close()

    def write(self, data):
        """Write to both the output streams and flush"""
        self.file.write(data)
        self.stdstream.write(data)
        self.flush()

    def flush(self):
        """Flush only the file object"""
        self.file.flush()
