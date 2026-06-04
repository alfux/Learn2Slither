import argparse as arg
import logging
import sys
from argparse import Namespace

from menu import Menu


def get_args(description: str = '') -> Namespace:
    """Manages program arguments.

    Args:
        description (str): is the program helper description.
    Returns:
        Namespace: The arguments.
    """
    av = arg.ArgumentParser(description=description)
    message = "Agent AI model."
    av.add_argument("agent", default=None, nargs='?', help=message)
    av.add_argument("--no-learn", action="store_true")
    av.add_argument("--no-display", action="store_true")
    message = "Number of training sessions."
    av.add_argument("--sessions", default=500, type=int, help=message)
    message = "Dimensions of the board."
    av.add_argument("--board-size", default=10, type=int, help=message)
    av.add_argument("--savepath", default=None, help="Save path")
    message = "Override maximum threads. May cause instabilities. But funny."
    av.add_argument("--max-thread", default=1, type=int, help=message)
    av.add_argument("--debug", action="store_true", help="Traceback mode.")
    return av.parse_args()


def main() -> int:
    """Learn2slither. Train your snake !

    On a display mode run:
        UP arrow to speed up.
        Down arrow to speed down.
        L key to toggle learning on/off.
        P to enter step by step mode.
        S to hot save the agent.
    Returns:
        int: return status 0 (success) 1 (error).
    """
    try:
        av = get_args(main.__doc__)
        fmt = "%(asctime)s | %(levelname)s - %(message)s"
        if av.debug:
            logging.basicConfig(level=logging.DEBUG, format=fmt)
        else:
            logging.basicConfig(level=logging.INFO, format=fmt)
        Menu(**vars(av)).run()
        return 0
    except Exception as err:
        debug = "av" in locals() and hasattr(av, "debug") and av.debug
        logging.critical("Fatal error: %s", err, exc_info=debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
