"""Agent module contains the player AI."""

from typing import Self

import numpy as np
from alfux.mlp import MLP
from numpy import ndarray


class Agent:
    """Learn and plays the game."""

    ACTIONS = np.eye(4)

    def __init__(
            self: Self,
            mlp: MLP, *,
            training: bool = True,
            replay_buffer_size=1000,
            replay_batch_ratio=0.1,
            target_network_update_rate=100
    ) -> None:
        """Instanciate the Agent.

        Args:
            mlp (MLP): Neural network.
            traininf (bool): State of training (on or off).
        """
        self._mlp = mlp
        self._target_mlp = mlp.copy()
        n = mlp.layers[0].W.shape[1]
        self._replay_buffer_state = np.zeros((replay_buffer_size, n))
        self._replay_buffer_rewards = np.zeros((replay_buffer_size, 4))
        self._replay_buffer_next = np.zeros((replay_buffer_size, n))
        self._replay_index = 0
        self._replay_buffer_size = replay_buffer_size
        self._replay_batch_size = int(replay_batch_ratio * replay_buffer_size)
        self._last_context = None
        self._last_action = None
        self._last_rewards = None
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

    def play(self: Self, view: list, temperature: float = 0) -> int:
        """Execute a move in the board.

        Args:
            view (list): Snake's vision.
            temperature (float): ratio of random action.
        Returns:
            int: The item on the board after a move.
        """
        self._last_context = np.atleast_2d(np.concatenate(view))
        self._last_rewards = self._mlp.eval(self._last_context)
        print("\r", self._last_rewards, end="                  ")
        if np.random.random_sample(1) < temperature:
            self._last_action = np.random.randint(0, 4)
        else:
            self._last_action = np.argmax(self._last_rewards)
        return self._last_action

    def learn(
        self: Self, view: list, reward: float, discount: float
    ) -> None:
        """Learn from success or mistake represented by reward.

        Args:
            view (list): Snake's vision.
            reward (float): Success or mistake indicator.
            discount (float): Influence of next steps in the reward.
        """
        if not self._training:
            return
        new_context = np.atleast_2d(np.concatenate(view))
        target = reward + discount * np.max(self._target_mlp.eval(new_context))
        self._last_rewards[0, self._last_action] = target
        self._last_context = np.concatenate(
            [self._last_context, [[1]]], axis=1
        )
        for _ in self._mlp.update(self._last_rewards, self._last_context):
            pass
        i = np.random.choice(self._replay_buffer_size, self._replay_batch_size)
        replay_rewards = self._replay_buffer_rewards[i]
        replay_context = self._replay_buffer_state[i]
        for _ in self._mlp.update(replay_rewards, replay_context):
            pass
        self._replay_buffer_rewards[self._replay_index] = self._last_rewards
        self._replay_buffer_state[self._replay_index] = self._last_context
        self._replay_index = self._replay_index + 1
        self._replay_index %= self._replay_buffer_size
        if self._target_network_i >= self._target_netwrok_update_rate:
            self._target_mlp = self._mlp.copy()
            self._target_network_i = 0
        else:
            self._target_network_i += 1

    def _train(self: Self, sarn: list)

    # Add a learning rate ?

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
