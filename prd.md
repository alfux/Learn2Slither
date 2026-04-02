# Product Requirement Document

## Board

- [x] Board size 10 by 10 (Bonus for changeable board size) 
- [x] Two green apples in a random cell of the board.
- [x] One red apple in a random cell of the board.
- [x] The snake starts with a length of 3 cells, also placed randomly and contiguously on the board.
- [x] If the snake hits a wall, game over this training session ends.
- [x] If the snake collides with its own tail, game over this taining session ends.
- [x] The snake eats a green apple, snake's lenght increase by 1. A new green apple appears on the board.
- [x] The snake eats a red apple, snake's length is reduced by 1. A new red apple appears on the board.
- [x] If the snake's length drops to 0, game over this training session ends.

### Training sessions

An untrained agent will quickly fail. A unique training session can’t be enough to learn: the agent will face hundreds or thousands of training sessions to increase  its skills.

- [x] The main program will offer a command line parameter to define how many training sessions should be executed.
- [x] Graphical interface displaying the board and its items through time. Each choice of the agent updates the board.
- [x] The display speed can be configured, with at least one human-readable speed.
- [x] Step by step mode.

## State

### Snake vision

- [x] The snake can only see in the 4 directions from its head.
- [x] The terminal must show his 4 direction vision as follows:
          W 
          0
          0
          G
          R
          0
          0
          0
W000000000HW
          S
          0
          W
    - W = Wall
    - H = Snake head
    - S = Snake body segment
    - G = Green apple
    - R = Red apple
    - 0 = Empty space

## Action

- [x] Your agent can only perform 4 actions (UP, LEFT, DOWN, RIGHT).
- [x] This "vision" constitue the only information available to the agent.
- [x] Board and environment is displayed in a dedicated window.
- [x] Vision and actions are displayed in the terminal.

## Rewards

- [x] The goal of the snake is to reach at least a length of 10 cells, and stay alive as long as possible.
- [x] The agent must learn from its actions and environment.

## Q-learning

- [x] The model uses a Q-function to evaluate the quality of an action in a specific state.
- [x] The Q-function is implemented with Q-values in a Q-table or a Neural Network.
- [x] The training algorithm updates the Q-function to improve performance based on the reward system.
- [x] To discover new paths, the agent must sometimes take random actions.
- [x] The training repeats iteratively and iterations are configurable.
- [x] At any time it is possible to export a file describing the current learning state of the agent. (Save)
- [x] A file can be imported by the agent to restore its learning. (Import)
- [] A configuration switch must be available to stop the agent from learning. In this state, it must ignore rewards.
- [x] It is possible to remove graphical display and terminal states in order to speed up the training.

## Technical structure

The program must be modular and have three distinct parts:

- [x] Environment (Board).
- [x] Interpreter (Vision / Rewards).
- [x] Agent (Decision / Learning).

## Turn-in and Peer-Evaluation

- [ ] Have a "models" folder with different trained models inside.
- [ ] Training must be done before evaluation. At least three models with 1, 10 and 100 training sessions.
- [x] Snake with length 10 or more at the end of a session and big lifetime.

## Bonus

- [x] Higher length up to 35.
- [ ] Visualy stunning display with lobby, configuration panel, results and statistics.
- [x] Possibility to change the board size with the same trained models.