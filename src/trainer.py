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
            learning=(not parameters.get("no_learn", False))
        )
        self._board = Board(parameters.get("board_size", None))
        self._interpreter = Interpreter(self._board, -1, 1, -0.25, 0)
        self._running_app = False
        self._play = False
        self._sessions = parameters["sessions"]
        self._iteration = [0]
        self._lengths = [0]
        self._times = [0]
        self._running = False
        self._thread = None

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
        """Current state of sessions' iterations.

        Returns:
            list: every sessions' iterations.
        """
        return self._iteration

    @property
    def lengths(self: Self) -> list:
        """Current state of sessions' lengths.

        Returns:
            list: every sessions' lengths.
        """
        return self._lengths

    @property
    def times(self: Self) -> list:
        """Current state of sessions' times.

        Returns:
            list: every sessions' times.
        """
        return self._times

    def update(self: Self) -> bool:
        """Plays and train.

        Returns:
            bool: True when the session is over.
        """
        if self._interpreter.snake_alive:
            move = self._agent.play(self._interpreter, self._board)
            self._interpreter.add_move(move)
            item = self._board.move(move)
            self._interpreter.interpret(item)
            self._agent.learn(self._interpreter, self._board)
            self._times[-1] += 1
        else:
            self._lengths[-1] = self._board.length
            iteration = self._iteration[-1] + 1
            if iteration >= self._sessions:
                return True
            self._board = Board(self._board.size)
            self._interpreter.board = self._board
            self._iteration.append(iteration)
            self._times.append(0)
            self._lengths.append(0)
        return False

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
