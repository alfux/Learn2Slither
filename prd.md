# Product Requirement Document

## Board

- [x] Board size 10 by 10 (Bonus for changeable board size) 
- [x] Two green apples in a random cell of the board.
- [x] One red apple in a random cell of the board.
- [x] The snake starts with a length of 3 cells, also placed randomly and contiguously on the board.
- [x] If the snake hits a wall, game over this training session ends.
- [x] If the snake collides with its own tail, game over this taining session ends.
- [x] The snake eats a green apple, snake's lenght increase by 1. A new green apple appears on the board.
- [x] The snake eats a red apple,, snake's length is reduced by 1. A new red apple appears on the board.
- [x] If the snake's length drops to 0, game over this training session ends.

### Training sessions

An untrained agent will quickly fail. A unique training session can’t be enough to learn: the agent will face hundreds or thousands of training sessions to increase  its skills.

- [ ] The main program will offer a command line parameter to define how many training sessions should be executed.
- [ ] Graphical interface displaying the board and its items through time. Each choice of the agent updates the board.
- [ ] The display speed can be configured, with at least one human-readable speed.
- [ ] Step by step mode.

## State

### Snake vision

- [ ] The snake can only see in the 4 directions from its head.
- [ ] The terminal must show his 4 direction vision as follows:
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

- [ ] Your agent can only perform 4 actions (UP, LEFT, DOWN, RIGHT).
- [ ] This "vision" constitue the only information available to the agent.
- [ ] Board and environment is displayed in a dedicated window.
- [ ] Vision and actions are displayed in the terminal.

## Rewards

- [ ] The goal of the snake is to reach at least a length of 10 cells, and stay alive as long as possible.
- [ ] The agent must learn from its actions and environment.

## Q-learning

- [ ] The model uses a Q-function to evaluate the quality of an action in a specific state.
- [ ] The Q-function is implemented with Q-values in a Q-table or a Neural Network.
- [ ] The training algorithm updates the Q-function to improve performance based on the reward system.
- [ ] You can train multiple models using different update approaches for the Q function.
- [ ] To discover new paths, the agent must sometimes take random actions.
- [ ] The training repeats iteratively and iterations are configurable.
- [ ] At any time it is possible to export a file describing the current learning state if the agent. (Save)
- [ ] A file can be imported by the agent to restore its learning. (Import)
- [ ] Train multiple models for the git repository.
- [ ] A configuration switch must be available to stop the agent from learning. In this state, it must ignore rewards.
- [ ] It is possible to remove graphical display and terminal states in order to speed up the training.

## Technical structure

The program must be modular and have three distinct parts:

- [ ] Environment (Board).
- [ ] Interpreter (Vision / Rewards).
- [ ] Agent (Decision / Learning).

## Turn-in and Peer-Evaluation

- [ ] Have a "models" folder with different trained models inside.
- [ ] Training must be done before evaluation. At least three models with 1, 10 and 100 training sessions.
- [ ] Snake with length 10 or more at the end of a session and big lifetime.

## Bonus

- [ ] Higher length up to 35.
- [ ] Visualy stunning display with lobby, configuration panel, results and statistics.
- [ ] Possibility to change the board size with the same trained models.