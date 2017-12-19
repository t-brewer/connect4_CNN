#!/usr/bin/env python3

# import libraries
import numpy as np
from pprint import pprint

class Board(object):

    # Constructor
    def __init__(self, grid_size=(6,7), verbose=False):
        
        # Define Grid/Board height width and number of positions
        # this part was implemented in case we want to play games with different sizes.
        # Complete implementation for this functionality is pending.
        self.height      = grid_size[0]
        self.width       = grid_size[1]
        self.N_positions = self.height*self.width
        self.winner      = 0 # winner of game (p1 = 1, p2 =-1, tie=0

        # Initialize game grids and vectors
        # Details in their respective functions
        self.init_grids(grid_size)
        self.init_vectors()

        # Define number of moves left (same as N_positions for now)
        # Used to flag and break out of game loop if no players win.
        self.N_moves_left = int(self.N_positions)

        # Array to keep track of how many positions are left in each column
        self.col_moves = np.zeros(self.width, dtype=np.int64) + self.height

    def init_grids(self, grid_size):
        '''
        The Board object uses three different numpy arrays with shape = grid_shape for various purposes.
        
        self.grid : numpy array representing the actual game grid.
        0 indicates empty positions, 1 for Player 1, and -1 for Player 2
        
        self.bool_grid : boolean numpy array with True values where players may place a piece, and 
        False values for filled or inaccessible positions.
        
        self.col_grid : Holds the column number of each position on the grid.  This was made to make it easier
        to look up columns when dealing with diagonals.
        '''
        
        # Initialize grids to help manage the game
        self.grid          = np.zeros(grid_size) # Main game grid
        self.bool_grid     = np.zeros_like(self.grid, dtype=bool) # Grid for available moves
        self.bool_grid[-1] = True # Mark initial available positions

        # Grid to hold column numbers
        self.column_grid = [[i for i in range(self.width)] for j in range(self.height)] 
        self.column_grid = np.array(self.column_grid)

        return 0

    def init_vectors(self):
        '''
            Vectors (as we call them) are an important part of the functionality of this code.
            They provide views of sections of the main grids.  Each view is a 4 element section representing
            a row, column, or diagonal.  The vectors for the game grid are used to see if a player has won, 
            while the boolean grid vectors are used in the decision process of the SetAI.  The vectors from 
            the column grid are simply used loop up which column each element of the the other vectors are in.
        '''
        # Initialize lists to store vectors
        self.vectors        = []
        self.bool_vectors   = []
        self.column_vectors = []

        # We split the work into three sections : row, column, and diagonal vectors
        
        # Initialize Row Vectors
        for i, r in enumerate(self.grid):
            # Loop over vector starting points
            for j in range(self.width - 3):
                # Make view of next 4 elements
                grid_view = r[j:j+4].view()
                bool_view = self.bool_grid[i][j:j+4].view()
                col_view  = self.column_grid[i][j:j+4]
                
                # Append views to respective lists
                self.vectors.append(grid_view)
                self.bool_vectors.append(bool_view)
                self.column_vectors.append(col_view)

                
        # For column vectors, we do pretty much the same thing as for the row vectors
        # except we use the Transpose of the grid. 
        grid_T = self.grid.transpose()
        bool_T = self.bool_grid.transpose()
        col_T  = self.column_grid.transpose()

        # Loop over columns (rows in transpose of grid)
        for i in range(len(grid_T)):
            # Loop over vector starting points
            for j in range(self.height - 3):
                # Make views of the next 4 elements in each grid
                grid_view = grid_T[i][j:j+4].view()
                bool_view = bool_T[i][j:j+4].view()
                col_view  = col_T[i][j:j+4]
                
                # Append views to respective lists
                self.vectors.append(grid_view)
                self.bool_vectors.append(bool_view)
                self.column_vectors.append(col_view)

        # Diagonal vectors got a little confusing but we split them up into 2 parts :
        # Looking at the grid we start by diagonals going from the top left corner
        # down towards the right.  We loop over these for each row and column.
        # We then get diagonal vectors starting from the bottom left of the grid 
        # going up towards the right.  To do this we flip the grid on it's y axis
        # and do the same thing as before.  
        
        # To actually grab each diagonal we divide the grid into smaller 4x4 slices
        # and use the numpy_arr.diagonal method

        # Left-Right Down up Diagonals
        max_offset = self.width - 4
        for i in range(self.height - 3):
            # Define grid-subset :
            sub_grid = self.grid[i:i+4]
            sub_bool = self.bool_grid[i:i+4]
            sub_col  = self.column_grid[i:i+4]
 
            for j in range(max_offset + 1):
                d_grid = sub_grid.diagonal(offset=j).view()
                d_bool = sub_bool.diagonal(offset=j).view()
                d_col  = sub_col.diagonal(offset=j).view()

                self.vectors.append(d_grid)
                self.bool_vectors.append(d_bool)
                self.column_vectors.append(d_col)

        # # Left-Right down up Diagonals
        # Flip on y axis
        flip_grid = np.flip(self.grid, axis=0)
        flip_bool = np.flip(self.bool_grid, axis=0)
        flip_col  = np.flip(self.column_grid, axis=0)
        max_offset = self.width - 4
        for i in range(self.height - 3):
            # Define grid-subset :
            sub_grid = flip_grid[i:i+4]
            sub_bool = flip_bool[i:i+4]
            sub_col  = flip_col[i:i+4]

            for j in range(max_offset + 1):
                d_grid = sub_grid.diagonal(offset=j).view()
                d_bool = sub_bool.diagonal(offset=j).view()
                d_col = sub_col.diagonal(offset=j).view()
                self.vectors.append(d_grid)
                self.bool_vectors.append(d_bool)
                self.column_vectors.append(d_col)

        return 0

    def update(self, Player):
        '''
        Method that updates the board based on a players choice.  
        The Player objects only choose which column to place the piece in
        (Player.choice), and the Board.update method figures out which position
        that corresponds to, and updates the value in the grids
        '''

        # Extract column choice :
        choice = Player.choice

        # Double check to make sure it is a valid move:
        available = [i for i,v in enumerate(self.col_moves) if v != 0]

        # Error Message and pause if nothing (ran into some problems while implementing)
        if choice not in available:
                print('Choice Error in Board.update')
                print('available:', available)
                print('player choice:', Player.choice)
                print('playertype:', Player.player_type)
                print('playername:', Player.name)
                self.display_grid()
                input()
                return -1

        # Get row corresponding to the column choice
        row = self.col_moves[choice] - 1

        # Update values in main grid and boolean grid
        self.grid[row,choice] = Player.marker
        self.bool_grid[row, choice] = False
        if (row != 0):
            self.bool_grid[row-1, choice] = True

        # Update number of moves left in that column :
        if(self.col_moves[choice] > 0):
            self.col_moves[choice] -= 1

        # Another Error Message
        elif self.col_moves[choice]  == 0:
            print('Error : number of moves in that column {} is already 0'.format(choice))
            return -1

        # Update number of moves left (also an error message):
        if (self.N_moves_left <= 0):
            print('Error : there are no more moves')
            return -1
        else :
            self.N_moves_left -= 1

        return 0

    def check_vectors(self, Player):
        '''
        Loop through all grid vectors to find if a player has won.
        Returns True if so.
        
        Because Players are marked as 1 or -1, it gets the sum of the elements in a vector, 
        and compares it to the target value of the player (4 or -4).
        '''
        flag = False
        for v in self.vectors:
            if sum(v) == Player.target:
                self.winner = Player.marker
                flag = True
                break
        return flag


    def display_grid(self):
        '''
        Display Game Grid in a more readable fashion:
        X = Player 1 (1)
        O = Player 2 (-1)
        _ = Empty element
        '''
         
        display = np.zeros_like(self.grid).astype(int).astype(str)
        for i, r in enumerate(display):
            for j, c in enumerate(r):
                if(self.grid[i][j] == -1):
                    display[i][j] = 'O'
                elif(self.grid[i][j] == 1):
                     display[i][j] = 'X'
                elif(self.grid[i][j] == 0):
                     display[i][j] = '_'

        display = np.vstack((display, np.arange(7)))
        for r in display:
            txt = ''
            for c in r :
                txt += c
                txt += '  '
            print(txt)
        print('')
        pass

    def display_vectors(self):
        '''
        Function used while debugging.  
        Simply lists all the grid vectors and corresponding bool vectors side by side.
        Separates them into rows, columns and diagonals.
        '''
        for i in range(len(self.vectors)):
            if (i ==0):
                print('ROWS')
            if (i==24):
                print('COLUMNS')
            if (i == 45):
                print('DIAGONALS')

            print(self.vectors[i], self.bool_vectors[i])
        pass

    def display_bool_grid(self):
        '''
        Function used for debugging.
        Display the bool grid.
        '''
        for r in self.bool_grid:
            print(r)

        pass
