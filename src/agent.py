"""Agent module contains the player AI."""

from datetime import datetime
from pathlib import Path
from typing import Self

import numpy as np
from alfux.mlp import MLP
from numpy import ndarray
from numpy import random as rng

from board import Board
from interpreter import Interpreter


class Agent:
    """Learn and plays the game."""

    def __init__(
            self: Self,
            mlp: MLP, *,
            learning: bool = True,
            replay_buffer_size: int = 8192,
            replay_batch_size: int = 128,
            relpay_interval: int = 16,
            target_network_update_rate: int = 512,
            initial_temperature: float = 1,
            minimal_temperature: float = 0,
            discount: float = 0.99
    ) -> None:
        """Instanciate the Agent.

        Args:
            mlp (MLP): Neural network.
            traininf (bool): State of training (on or off).
            replay_buffer_size (int): Size of the replay buffer.
            replay_batch_size (int): Size of a replay batch.
            target_network_update_rate (int): Rate of update for the target
                network.
            initial_temperature (float): Starting temperature of the agent.
            initial_discount (float): Statring learning discount.
        """
        self._mlp = mlp
        self._target_mlp = mlp.copy()
        n = mlp.layers[0].W.shape[1] - 1
        self._replay_buffer_state = np.zeros((replay_buffer_size, n))
        self._replay_buffer_action = np.zeros(replay_buffer_size, dtype=int)
        self._replay_buffer_rewards = np.zeros(replay_buffer_size)
        self._replay_buffer_discount = np.zeros(replay_buffer_size)
        self._replay_buffer_next = np.zeros((replay_buffer_size, n))
        self._replay_index = 0
        self._replay_cooldown = 0
        self._buffer_full = False
        self._replay_buffer_size = replay_buffer_size
        self._replay_batch_size = replay_batch_size
        self._replay_interval = relpay_interval
        self._last_state = None
        self._last_action = None
        self._target_netwrok_update_rate = target_network_update_rate
        self._target_network_i = 0
        self._temperature = np.clip(initial_temperature, 0, 1)
        self._min_temp = minimal_temperature
        self._discount = np.clip(discount, 0, 1)
        self._tol = 0.05
        self._learning = learning

    @property
    def learning(self: Self) -> bool:
        """Get learning state.

        Returns:
            bool: True if learning False otherwise.
        """
        return self._learning

    @learning.setter
    def learning(self: Self, value: bool) -> None:
        """Set learning state.

        Args:
            value (bool): New learning state.
        """
        self._learning = value

    @property
    def temperature(self: Self) -> float:
        """Get the agent's temperature.

        Returns:
            float: temperature of the agent.
        """
        return self._temperature

    @temperature.setter
    def temperature(self: Self, value: float) -> None:
        """Set the agent's temperature.

        Args:
            value (float): temperature between 0 and 1.
        """
        self._temperature = np.clip(value, 0, 1)

    def play(self: Self, interpreter: Interpreter, board: Board) -> int:
        """Execute a move in the board.

        Args:
            interpreter (Interpreter): Instance of the environment interpreter.
            board (Board): The environment.
        Returns:
            int: The item on the board after a move.
        """
        self._last_state = interpreter.state(board)
        rewards = self._mlp.eval(np.atleast_2d(self._last_state))
        temp = self._temperature if self._learning else self._min_temp
        if np.random.random_sample(1) < temp:
            self._last_action = np.random.randint(0, 4)
        else:
            print(rewards)
            best = np.max(rewards)
            tol = self._tol * np.max(1, np.abs(best))
            candidates = np.flatnonzero(np.isclose(rewards, best, atol=tol))
            print(candidates, tol)
            print()
            self._last_action = np.random.choice(candidates)
        return self._last_action

    def learn(self: Self, interpreter: Interpreter, board: Board) -> None:
        """Learn from the difference of state after a play.

        Args:
            interpreter (Interpreter): Instance of the environment interpreter.
            board (Board): The environment.
        """
        if not self._learning:
            return
        self._replay_buffer_state[self._replay_index] = self._last_state
        self._replay_buffer_action[self._replay_index] = self._last_action
        self._replay_buffer_rewards[self._replay_index] = interpreter.reward
        discount = self._discount if interpreter.snake_alive else 0
        self._replay_buffer_discount[self._replay_index] = discount
        next_state = interpreter.state(board)
        self._replay_buffer_next[self._replay_index] = next_state
        self._replay_index += 1
        self._replay_index %= self._replay_buffer_size
        if self._replay_cooldown < self._replay_interval:
            self._replay([self._replay_index - 1])
            self._replay_cooldown += 1
        else:
            self._replay_batch()
            self._replay_cooldown = 0
        if self._target_network_i >= self._target_netwrok_update_rate:
            self._target_mlp = self._mlp.copy()
            self._target_network_i = 0
        self._update_temperature()

    def save(self: Self, path: str = None, i: int = None) -> None:
        """Save the agent.

        Args:
            path (str): path of the file.
            i (int): index for multiple file save with the same name
        """
        if not self._learning:
            return
        if path is None:
            path = datetime.now().isoformat(":", "seconds").replace(":", "")
            path = Path("agent_" + path.replace("-", "") + ".json")
        else:
            path = Path(path)
        if i is not None and i > 0:
            path = path.stem + f"({i})" + path.suffix
        self._mlp.save(path)

    def _update_temperature(self: Self) -> None:
        """Updates temperature."""
        if self._temperature > 0:
            self._temperature = np.clip(
                self._temperature - 1e-3, self._min_temp, 1
            )

    def _replay(self: Self, indices: ndarray) -> None:
        """Train on the replay buffer.

        Args:
            indices (ndarray): indices of the random batch to train on.
        """
        states = self._replay_buffer_state[indices]
        actions = self._replay_buffer_action[indices]
        rewards = self._replay_buffer_rewards[indices]
        discounts = self._replay_buffer_discount[indices]
        nexts = self._replay_buffer_next[indices]
        replay_rewards = self._mlp.eval(states)
        next_best_rewards = np.max(self._target_mlp.eval(nexts), axis=1)
        targets = rewards + discounts * next_best_rewards
        replay_rewards[np.arange(len(states)), actions] = targets
        states = np.concatenate([states, np.ones((len(states), 1))], axis=1)
        for _ in self._mlp.update(replay_rewards, states):
            self._target_network_i += 1

    def _replay_batch(self: Self) -> None:
        """Get a random replay batch"""
        if self._buffer_full:
            i = rng.choice(self._replay_buffer_size, self._replay_batch_size)
            self._replay(i)
        elif self._replay_index >= self._replay_batch_size:
            i = rng.choice(self._replay_index, self._replay_batch_size)
            self._replay(i)
        elif self._replay_index == 0:
            self._buffer_full = True
            i = rng.choice(self._replay_buffer_size, self._replay_batch_size)
            self._replay(i)

    @staticmethod
    def load(path: str, **kw: dict) -> 'Agent':
        """Load an agent from a file.

        Args:
            path (str): path of the file.
        KWArgs:
            **kw (dict): Any kwargs of instanciation.
        Returns:
            Agent: The loaded agent.
        """
        return Agent(MLP.loadf(path), **kw)
