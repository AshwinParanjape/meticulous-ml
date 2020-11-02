import sys
class ExitHooks(object):
    def __init__(self):
        self.exited = False
        self.raised_exception = False
        self.exit_code = None

    def hook(self):
        """Replace sys.exit and sys.excepthook with our own handlers"""
        self._orig_exit = sys.exit
        sys.exit = self.exit
        sys.excepthook = self.exc_handler

    def exit(self, code=0):
        self.exited = True
        self.exit_code = code
        self._orig_exit(code)

    def exc_handler(self, exc_type, exc_value, exc_traceback):
        self.raised_exception = True
        self.exc_info = {
            'exc_type': exc_type,
            'exc_value': exc_value,
            'exc_traceback': exc_traceback
        }

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

    def close(self):
        """Close the file and set the stdstream back to the original stdstream"""
        stdstream = self.stdstream
        self.file.close()

    def __del__(self):
        """Close the file and set the stdstream back to the original stdstream"""
        self.close()

    def write(self, data):
        """Write to both the output streams and flush"""
        self.file.write(data)
        self.stdstream.write(data)
        self.flush()

    def flush(self):
        """Flush only the file object"""
        self.file.flush()

    def getvalue(self):
        return self.stdstream.getvalue()
