# Artificial Neural Networks with Connect-Four

## Context

In this work, we set ourselves in the context of the popular game Connect-4 (C4) to see if we can train an Artificial Neural Network (ANN) to make decisions without explicitly stating the rules of the game.  Specifically, we train a Convolutional Neural Network (CNN) to recognize the winner of a game using over 300,000 examples.  We then link the model to an artificial intelligence (AI), which we refer to as `LearningAI`, in a C4 engine.  The `LearningAI` uses the model to infer the best decision given the state of the C4 grid and a list of possible moves.  To create a database of C4 games and test the performance of our model we use an artificial intelligence (AI) with a hard coded strategy (`SetAI`).  To evaluate the CNN's capabilities we also define a baseline AI (`RandomAI`) that choses  each move at random.
<br>
<br>
For more details about about performance tests, please refer to the report (PDF file) included in this repository.


### Note to Reader

This notebook is meant to be a step by step presentation of the code used for the Connect-4 ANN project and go into the details about the flow of the work.  The code is presented in the order that objects and functions would need to be defined for the code to work the way it is meant to.  We admit that the code is a little bit messy, but we try our best to explain everything in the comments and function docstrings.<br>
<br>
We start by presenting the code and structure of the Connect-4 Engine.  We follow this by providing an explanation on the basic topography of the Keras model expected for the the engine to work, and create a demo model.  Finally, we provide a **demonstration** of how to play games, generate data, and link the keras model to the engine.  For details about our process and results please refer to the report included in the repository.<br>
<br>
The code is available in this repository as a package of `.py` files (see the *library* directory).
