import argparse as arg
import logging
import sys
from argparse import Namespace

from display import Display
from learn2slither import Learn2Slither
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
    av.add_argument("--sessions", default=1000, type=int, help=message)
    message = "Dimensions of the board."
    av.add_argument("--board-size", default=10, type=int, help=message)
    av.add_argument("--debug", action="store_true", help="Traceback mode.")
    return av.parse_args()


def main() -> int:
    """Test main.

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
        Menu().run()
        quit()
        if len(sys.argv) == 1:
            Menu().run()
        else:
            l2s = Learn2Slither(**vars(av))
            if av.no_display:
                l2s.train()
                l2s.agent.save()
            else:
                Display(l2s).run()
        return 0
    except Exception as err:
        debug = "av" in locals() and hasattr(av, "debug") and av.debug
        logging.critical("Fatal error: %s", err, exc_info=debug)
        return 1


if __name__ == "__main__":
    sys.exit(main())
