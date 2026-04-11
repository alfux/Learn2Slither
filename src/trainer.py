"""Trainer trainer module of the application"""

from threading import Thread
from typing import Self


from agent import Agent
from board import Board
from interpreter import Interpreter


class Trainer:
    """Trainer trainer program class"""

    def __init__(self: Self, **parameters: dict) -> None:
        """Instanciate an instance of Trainer.

        KWArgs:
            parameters (dict): Application parameters.
        """
        self._agent = Agent.load(
            parameters["agent"],
            learning=(not parameters.get("no_learn", False)),
            initial_temperature=parameters.get("initial_temperature", 1),
            minimal_temperature=parameters.get("minimal_temperature", 0)
        )
        self._board = Board(parameters.get("board_size", None))
        self._interpreter = Interpreter(self._board, -1, 1, -0.25, -0.01)
        self._running_app = False
        self._play = False
        self._sessions = parameters["sessions"]
        self._iteration = [0]
        self._lengths = [0]
        self._lengths_mean = 0
        self._lengths_max = 0
        self._lengths_last = 0
        self._times = [0]
        self._times_mean = 0
        self._times_max = 0
        self._times_last = 0
        self._running = False
        self._thread = None
        self._stat = parameters.get("display_stat", False)

    @property
    def agent(self: Self) -> Agent:
        """Get the agent.

        Returns:
            Agent: The agent.
        """
        return self._agent

    @property
    def board(self: Self) -> Board:
        """Get the current board.

        Returns:
            Board: The current board.
        """
        return self._board

    @property
    def interpreter(self: Self) -> Interpreter:
        """Get the interpreter.

        Returns:
            Interpreter: The interpreter.
        """
        return self._interpreter

    @property
    def running(self: Self) -> bool:
        """State of background training.

        Returns:
            True: if a background training is running.
        """
        return self._running

    @property
    def iterations(self: Self) -> list:
        """Iterations array.

        Returns:
            list: iteration array.
        """
        return self._iteration

    @property
    def lengths(self: Self) -> list:
        """Lengths array.

        Returns:
            list: lengths array.
        """
        return self._lengths

    @property
    def lengths_mean(self: Self) -> float:
        """Lengths mean.

        Returns:
            float: Lengths mean.
        """
        return self._lengths_mean

    @property
    def lengths_max(self: Self) -> float:
        """Lengths max.

        Returns:
            float: Lengths max.
        """
        return self._lengths_max

    @property
    def lengths_last(self: Self) -> float:
        """Lengths of last death.

        Returns:
            float: Lenghts of last death.
        """
        return self._lengths_last

    @property
    def times_last(self: Self) -> float:
        """Times of last death.

        Returns:
            float: Times of last death.
        """
        return self._times_last

    @property
    def times_mean(self: Self) -> float:
        """times mean.

        Returns:
            float: times mean.
        """
        return self._times_mean

    @property
    def times_max(self: Self) -> float:
        """Times max.

        Returns:
            float: Times max.
        """
        return self._times_max

    @property
    def times(self: Self) -> list:
        """Times array.

        Returns:
            list: times array.
        """
        return self._times

    def update(self: Self) -> int:
        """Plays and train.

        Returns:
            int: 0 when snake moved, 1 when reset, 2 when end of training.
        """
        if self._interpreter.snake_alive:
            move = self._agent.play(self._interpreter, self._board)
            self._interpreter.add_move(move)
            item = self._board.move(move)
            self._interpreter.interpret(item)
            self._agent.learn(self._interpreter, self._board)
            self._times[-1] += 1
            return 0
        else:
            self._lengths[-1] = self._board.length
            self._last_stats()
            iteration = self._iteration[-1] + 1
            if iteration >= self._sessions:
                return 2
            self._board = Board(self._board.size)
            self._interpreter.board = self._board
            self._iteration.append(iteration)
            self._times.append(0)
            self._lengths.append(0)
            return 1

    def train(self: Self, savepath: str, i: int = None) -> None:
        """Trains the model in a single threaded loop, without display.

        Args:
            savepath (str): Path to a save file.
            i (int): Instance index for multithread saves.
        """
        if self._thread is None:
            self._thread = Thread(target=self._train, args=[savepath, i])
            self._running = True
            self._thread.start()
        else:
            print("An instance of background training is already running.")

    def stop(self: Self) -> None:
        """Stop the current threaded training loop."""
        self._running = False

    def save(self: Self, savepath: str = None, index: int = None) -> None:
        """Save the current state of the agent.

        Args:
            savepath (str): path of the file.
            index (int): index for multiple file save with the same name
        """
        self._agent.save(savepath, index)

    def _train(self: Self, savepath: str, i: int) -> None:
        while not self.update() and self._running:
            pass
        self._agent.save(savepath, i)
        self._running = False
        self._thread = None

    def _last_stats(self: Self) -> None:
        """Compute last stats."""
        self._lengths_mean = self._mean(self._lengths_mean, self._lengths)
        if self._board.length > self._lengths_max:
            self._lengths_max = self._board.length
        self._times_mean = self._mean(self._times_mean, self._times)
        if self._times[-1] > self._times_max:
            self._times_max = self._times[-1]
        self._lengths_last = self._board.length
        self._times_last = self._times[-1]

    @staticmethod
    def _mean(prev: float, array: list) -> float:
        """Compute mean from previous mean.

        Args:
            prev (float): previous mean.
            array (list): new array.
        Returns:
            float: new mean.
        """
        return (prev * (len(array) - 1) + array[-1]) / len(array)
