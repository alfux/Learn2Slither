"""Agent module contains the player AI."""

from typing import Self

import numpy as np
from alfux.mlp import MLP
from numpy import ndarray
from numpy import random as rng

from board import Board
from interpreter import Interpreter


class Agent:
    """Learn and plays the game."""

    ACTIONS = np.eye(4)

    def __init__(
            self: Self,
            mlp: MLP, *,
            replay_buffer_size: int = 512,
            replay_batch_size: int = 64,
            target_network_update_rate: int = 1000,
            initial_temperature: float = 1,
            initial_discount: float = 0
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
        self._buffer_full = False
        self._replay_buffer_size = replay_buffer_size
        self._replay_batch_size = replay_batch_size
        self._last_state = None
        self._last_action = None
        self._target_netwrok_update_rate = target_network_update_rate
        self._target_network_i = 0
        self._temperature = initial_temperature
        self._discount = initial_discount
        self._neutral_count = 0
        self._max_neutral_count = 100

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
        if np.random.random_sample(1) < self._temperature:
            self._last_action = np.random.randint(0, 4)
        else:
            self._last_action = np.argmax(rewards)
        return self._last_action

    def learn(self: Self, interpreter: Interpreter, board: Board) -> None:
        """Learn from the difference of state after a play.

        Args:
            interpreter (Interpreter): Instance of the environment interpreter.
            board (Board): The environment.
        """
        self._replay_buffer_state[self._replay_index] = self._last_state
        self._replay_buffer_action[self._replay_index] = self._last_action
        self._replay_buffer_rewards[self._replay_index] = interpreter.reward
        discount = self._discount if interpreter.snake_alive else 0
        self._replay_buffer_discount[self._replay_index] = discount
        next_state = interpreter.state(board)
        self._replay_buffer_next[self._replay_index] = next_state
        self._replay_index += 1
        self._replay_index %= self._replay_buffer_size
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
        if self._target_network_i >= self._target_netwrok_update_rate:
            self._target_mlp = self._mlp.copy()
            self._target_network_i = 0
        self._update_temperature(interpreter._last_item)

    def _update_temperature(self: Self, last_reward: float) -> None:
        """Updates temperature.

        Args:
            last_reward (float): Last received reward.
        """
        if self._temperature > 0:
            self._temperature = np.clip(self._temperature - 1e-3, 0, 1)
            self._discount = np.clip(self._discount + 1e-3, 0, 1)
        if last_reward == Board.N:
            self._neutral_count += 1
        else:
            self._neutral_count = 0
        if self._neutral_count > self._max_neutral_count:
            self._temperature = np.clip(self._temperature + 0.1, 0, 1)
            self._discount = np.clip(self._discount - 0.1, 0, 1)
            self._neutral_count = 0

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

    def save(self: Self, path: str) -> None:
        """Save the agent.

        Args:
            path (str): path of the file.
        """
        self._mlp.save(path)

    @staticmethod
    def load(path: str, **kw: dict) -> Agent:
        """Load an agent from a file.

        Args:
            path (str): path of the file.
        KWArgs:
            **kw (dict): Any kwargs of instanciation.
        Returns:
            Agent: The loaded agent.
        """
        return Agent(MLP.loadf(path), **kw)
