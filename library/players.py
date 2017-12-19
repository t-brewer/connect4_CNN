#!/usr/bin/env python3

import numpy as np

class Player(object):
    '''
    Parent Class for all player types (different AIs).
    Simply defines some consistent things for each player.
    Each Player type inherits from this object.
    '''
    def __init__(self, p=1, name='Player'):
        self.player  = p      # Player Number 
        self.name    = name   # Player Name (for display purposes only)
        self.marker  = 1 if self.player == 1 else -1 # Marker / token to be displayed on the Grid
        self.target  = 4*self.marker # Target value to flag when player won the game


class SetAI(Player):
    '''
    Player type with simple hard coded strategy to play the game.
    Strategy simply places winning piece if there are three of its own in a row.  
    If that fails, it checks if the opponent is about to win and blocks it.
    '''
    
    # Constructor
    def __init__(self, p=1, name="Albert"):
        Player.__init__(self, p, name) # Same definitions as Parent Class
        self.player_type = 'SetAI'     # Name of class (used as need arises)


    def move(self, Board):
        '''
        Move method : chooses which column to place token in.  Result is assigned to .choice attribute
        and gathered when updating the board. 
        '''

        # Get columns that still have available moves.
        available = [i for i,v in enumerate(Board.col_moves) if v != 0]

        # Fail safe : assigns random choice (ran into some bugs where 
        # script ran without errors but nothing was ever assigned to choice)
        self.choice = np.random.choice(available)


        # Get Vectors with available moves (True values in Board.bool_vectors)
        playable_vector_indices = self.get_playable_vectors(Board)
        
        
        # Select a vector to play on.
        # Details in function, but this returns the index in the list of vectors
        vector_index_choice = self.choose_vector(playable_vector_indices, Board)

        # Pull out vector associated to the index :
        vector        = Board.vectors[vector_index_choice]
        bool_vector   = Board.bool_vectors[vector_index_choice]
        column_vector = Board.column_vectors[vector_index_choice]

        # Get index of True values in the Bool Vector
        true_positions = np.where(bool_vector == True)[0]

        # Assign the column number to the choice attribute based 
        # on the number of True values in the bool vector
        position_choice = None
        
        if (len(true_positions) == 0): # Error message
            print('True Positions Error')
        elif(len(true_positions == 1)): # If there is only one
            position_choice = true_positions[0]
        elif(len(true_positions > 1)): # Random choice if more than one
            position_choice = np.random.choice(true_positions)

        if position_choice != None: 
            # Condition due to previously mentioned fail-safe
            self.choice = column_vector[position_choice]

        return 0

    def get_playable_vectors(self, Board):
        # Get indices of vectors with playable positions
        # that is, a True value in the Bool Vector list.
        indices = []
        for i, v in enumerate(Board.bool_vectors):
            if True in v:
                indices.append(i)
        return indices


    def choose_vector(self, playable, Board):
        # Algorithm to pick a vector to play in
        # By order of preference :
        # - Vector that lets player win on this turn
        # - Vector that keeps opponent from winning on next turn
        # - Random vector with available position (True in Bool vectors)

        # Make list of of playable vectors
        play_vectors = []
        for i in playable:
            play_vectors.append(Board.vectors[i])

        # See if there are any winning vectors :
        winning_vector_indices = []
        for i in range(len(play_vectors)):
            score = sum(play_vectors[i])

            # Vectors for Player 1 (marker = 1)
            if self.target > 0:
                if(score == self.target - 1):
                    # This is a winning vector for player 1
                    winning_vector_indices.append(playable[i])

            # Vectors for Player 2 (marker = -1)
            if self.target < 0 :
                if(score == self.target +1):
                    # This is a winning vector for player 2
                    winning_vector_indices.append(playable[i])


        # Return array of winning vectors (if there are any)
        if (len(winning_vector_indices) > 0):
            return np.random.choice(winning_vector_indices)

        # See if there any losing vectors
        losing_vector_indices = []
        for i in range(len(play_vectors)):
            score = sum(play_vectors[i])

            # Vectors for Player 1 (marker = 1)
            if self.target > 0:
                if(score == -1*self.target + 1):
                    # This is a losing vector for player 1
                    losing_vector_indices.append(playable[i])

            # Vectors for Player 2 (marker = -1)
            if self.target < 0:
                if(score == -1*self.target - 1):
                    # This is a losing vector for player 2
                    losing_vector_indices.append(playable[i])

        # Return array of losing vector indices (if there are any)
        if (len(losing_vector_indices) > 0):
            return np.random.choice(losing_vector_indices)

        # If there are no winning or losing vectors, return a random one with available positions
        if (len(losing_vector_indices) == 0) and (len(winning_vector_indices) == 0):
            return np.random.choice(playable)
        else:
            # Error message
            print('Winning/Losing Vector Error')


        return None


class LearningAI(Player):
    
    '''
    Player type that uses a Keras CNN model to make decisions.
    
    Model input :
    6x7 numpy array representing the game grid, or list of such grids, but the model has to 
    be reshaped to (N_grids, 6, 7, 1), adding an extra dimension to mimic an image.
    
    Model Output Layer :
    1 Single node with Sigmoid Activation function (mean't to represent the likelihood of winning given a
    certain grid).  
    
    Important note : for now the implementation assumes that the LearningAI is Player 1.  Because of this
    it makes decisions based on the assumption that it wants the 1 marker to win on the game grid.
    '''
        
    # Constructor
    def __init__(self,
                    keras_model, # Path to keras Conv2D model. 
                    p=1,
                    name="Paul"):

        import keras.models as km # Do it here so that we don't have to if this AI isn't playing
        
        Player.__init__(self, p, name)        # Parent class declarations
        self.model = keras_model # Load Keras Model
        self.player_type = 'LearningAI'       # Object name (used when need arises)


    def move(self, Board):
        '''
        Assigns column choice to .choice attribute.
        '''
        
        # Get Available column and corresponding row indices
        self.col_indices = [i for i,v in enumerate(Board.col_moves) if v != 0]
        row_indices      = [i - 1 for i in Board.col_moves if i != 0]

        # Make array of potential board states, each with the players next possible moves
        potential_states = np.array([Board.grid.copy() for i in self.col_indices])
        
        for i, v in enumerate(self.col_indices):
            potential_states[i][row_indices[i]][v] = self.marker

        # Reshape potential states so that it fits into the Conv2D model
        potential_states = np.array([s.reshape(6,7,1) for s in potential_states])

        # Make predictions with Model object
        self.predictions = self.model.predict(potential_states).flatten()


        # Select prediction closest to 1 (likelihood of winning?)
        # and assign it to the choice attribute
        best_move = np.where(self.predictions == self.predictions.max())[0][0]
        self.choice = self.col_indices[best_move]

        return 0

    def print_move_weights(self):
        '''
        Print the predictions of the different model predictions and the max value. 
        Mostly used to check that things were working.
        '''
        tuples = [(self.col_indices[i],v) for i,v in enumerate(self.predictions)]
        print("Move Weights :", tuples)


        pass


class RandomAI(Player):
    '''
    A Player that only places pieces at Random.
    '''
    
    def __init__(self, p=1, name  = 'Randy'):
        Player.__init__(self, p, name)
        self.player_type = 'RandomAI'


    def move(self, Board, SaveObj):

        available = [i for i,v in enumerate(Board.col_moves) if v != 0]
        self.choice = np.random.choice(available)

        pass
