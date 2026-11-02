import sys

from Controllers.SpeedReaderController import SpeedReaderController
from Core.single_instance import SingleInstance, Win32Api


def main(argv, guard, make_app):
    """Run one SpeedReader; a later launch only wakes the running one, then exits."""
    if not guard.acquire():
        return
    app = make_app()
    guard.listen(lambda: app.main_frame.callbacks.post(app.show_window))
    app.open_from_args(argv)
    app.mainloop()


if __name__ == "__main__":
    main(sys.argv, SingleInstance(Win32Api()), SpeedReaderController)
