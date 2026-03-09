"""Agent module contains the player AI."""

from typing import Self

import numpy as np
from alfux.mlp import MLP
from numpy import ndarray
from numpy import random as rng


class Agent:
    """Learn and plays the game."""

    ACTIONS = np.eye(4)

    def __init__(
            self: Self,
            mlp: MLP, *,
            training: bool = True,
            replay_buffer_size=64,
            replay_batch_ratio=0.1,
            target_network_update_rate=1000
    ) -> None:
        """Instanciate the Agent.

        Args:
            mlp (MLP): Neural network.
            traininf (bool): State of training (on or off).
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
        self._replay_batch_size = int(replay_batch_ratio * replay_buffer_size)
        self._replay_batch_size = max(1, self._replay_batch_size)
        self._last_state = None
        self._last_action = None
        self._training = training
        self._target_netwrok_update_rate = target_network_update_rate
        self._target_network_i = 0

    @property
    def training(self: Self) -> bool:
        """Get training state.

        Returns:
            bool: Training state.
        """
        return self._training

    @training.setter
    def training(self: Self, value: bool) -> None:
        """Set training state.

        Args:
            value (bool): New training state.
        """
        self._training = value

    def play(self: Self, state: list, temperature: float = 0) -> int:
        """Execute a move in the board.

        Args:
            state (list): Snake's vision.
            temperature (float): ratio of random action.
        Returns:
            int: The item on the board after a move.
        """
        self._last_state = np.atleast_2d(np.concatenate(state))
        rewards = self._mlp.eval(self._last_state)
        print("\r", rewards, end=" ")
        if np.random.random_sample(1) < temperature:
            self._last_action = np.random.randint(0, 4)
        else:
            self._last_action = np.argmax(rewards)
        return self._last_action

    def learn(
        self: Self, next_state: list, reward: float, discount: float
    ) -> None:
        """Learn from success or mistake represented by reward.

        Args:
            next_state (list): Snake's vision after a play.
            reward (float): Success or mistake indicator.
            discount (float): Influence of next steps in the reward.
        """
        if not self._training:
            return
        self._last_state = self._last_state.flatten()
        self._replay_buffer_state[self._replay_index] = self._last_state
        self._replay_buffer_action[self._replay_index] = self._last_action
        self._replay_buffer_rewards[self._replay_index] = reward
        self._replay_buffer_discount[self._replay_index] = discount
        next_state = np.concatenate(next_state)
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
        if self._target_network_i >= self._target_netwrok_update_rate:
            self._target_mlp = self._mlp.copy()
            self._target_network_i = 0

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
    def load(path: str, *, training: bool = True) -> Agent:
        """Load an agent from a file.

        Args:
            path (str): path of the file.
            discount (float): Weight of the next step on the reward.
            traininf (bool): State of training (on or off).
        Returns:
            Agent: The loaded agent.
        """
        return Agent(MLP.loadf(path), training=training)
