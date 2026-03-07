"""Agent module contains the player AI."""

from typing import Self

import numpy as np
from alfux.mlp import MLP


class Agent:
    """Learn and plays the game."""

    ACTIONS = np.eye(4)

    def __init__(self: Self, mlp: MLP, *, training: bool = True) -> None:
        """Instanciate the Agent.

        Args:
            mlp (MLP): Neural network.
            traininf (bool): State of training (on or off).
        """
        self._mlp = mlp
        self._last_context = None
        self._last_action = None
        self._last_rewards = None
        self._training = training

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
        target = reward + discount * np.max(self._mlp.eval(new_context))
        # Add a learning rate ?
        # Implement replay buffer
        # Implement target network
        self._last_rewards[0, self._last_action] = target
        for cost in self._mlp.update(self._last_rewards, self._last_context):
            # print(cost)
            pass

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
