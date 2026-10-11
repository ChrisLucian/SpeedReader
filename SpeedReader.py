import sys

from Controllers.SpeedReaderController import SpeedReaderController

if __name__ == "__main__":
    app = SpeedReaderController()
    app.open_from_args(sys.argv)
    app.mainloop()
