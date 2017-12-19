#!/usr/bin/env python3

# LIBRARIES
import numpy as np
import os

from board import Board
from players import *

class C4(object):
    '''
    Connect 4 Engine designed to be connected to other scripts.
    There are still some kinks to work out, but its a work in progress.
    Generally speaking the only required parameter is gametype, which determines
    the types of AIs playing.  types are passed as strings, options are :
    setset        : SetAI, SetAI
    setrand       : SetAI, RandomAI
    anything else : LearnAI, SetAI
    '''

    # Constructor
    def __init__(self, gametype=None, keras_model=None, verbose=False, pause=False,p1_name=None, p2_name=None):

        # Parameters
        self.verbose     = verbose     # To display grid as the game is being played and other outputs
        self.pause       = pause       # To pause the game between each move
   
        # Flag for breaking out of game loop (if winner or no more moves)
        self.flag = False

        # Instantiate Game Objects

        # Board/Grid
        self.Board = Board()

        # Players
        if (gametype == "setset"):
            p1 = SetAI(p= 1)
            p2 = SetAI(p=-1)

        elif (gametype == 'setrand') :
            p1 = RandomAI(p=1)
            p2 = SetAI(p=-1)

        else:
            # LearningAI will not work if no model is provided
            p1 = LearningAI(p=1, keras_model=keras_model)
            p2 = SetAI(p=-1)
            
        # If names were provided, update them
        if(p1_name != None): p1.name = p1_name
        if(p2_name != None): p2.name = p2_name

            
        # Put players in a list and shuffle to randomize who starts
        self.player_list = [p1, p2]
        np.random.shuffle(self.player_list)

        # Print stuff if verbose
        if(self.verbose):
            print('Game Type       :', gametype)
            print('Players         : {} ({}), {} ({})'.format(self.player_list[0].name, self.player_list[0].marker, self.player_list[1].name, self.player_list[1].marker))
            print('Starting Player :', (self.player_list[0].name, self.player_list[0].player_type))


    def play_game(self):
        '''
        Runs through a game!
        '''
        
        # Move counter (various purposes)
        move = 0

        for i in range(21):                 # Main Game loop
            for player in self.player_list: # Loop over player turns
                move += 1               # Update move number

                if (self.verbose):
                    # Display Turn info (player, moves left, etc...) and board (before players choice)
                    txt = 'Player: {}, Moves Left: {}'.format(player.name, self.Board.N_moves_left)
                    print(txt)
                    self.Board.display_grid()
                    if (self.pause) : input()

                # Player chooses which column to play in
                player.move(self.Board) 

                if(player.player_type == 'LearningAI' and self.verbose==True):
                    player.print_move_weights()
                
                # Board updates based on player's choice
                self.Board.update(player) 

                
                # Check if player has won 
                self.flag = self.Board.check_vectors(player)

                # Break out of loop if player has won (don't go to next players turn)
                if (self.flag):
                    if(self.verbose) :
                        print(player.name, 'wins!', '({})'.format(player.player_type))
                    
                    self.Board.winner = player.player # save winner
                    break

                # END PLAYER LOOP
                  
            # Check if there are any mores moves
            if(self.Board.N_moves_left == 0):
                self.flag = True # Flag so we can break out of main game loop
                
            if(self.flag == True):    
                break 

            # END MAIN GAME LOOP

        # print end game board
        if (self.verbose):
            self.Board.display_grid()

    def save_game(self, output_file, verbose=True):
        '''
        Saves game to output_file.
        If output_file doesn't exist, it will create it and make a header.
        '''
        
        # Check to see if the output_file already exists
        # if not, create it with a header
        # if so, just add row to the file

        if (os.path.isfile(output_file) == False):
            # make header 
            header = self.create_header()
            
            # Create file and add header
            f = open(output_file, "w")
            f.write(header)
            f.close()

        # Create Game array (see function)
        game_array = self.make_game_array(Board)

        # Convert Game Array to csv line
        txt = ''
        for i in game_array:
            txt += '{},'.format(str(i))
            
        # Take of excess comma from loop and add an end line character
        txt = txt.strip(',')
        txt += '\n'

        # Save to ouput file
        if(verbose==True): print('saving game to', output_file)
        f = open(output_file, "a")
        f.write(txt)
        f.close()

        pass
                  
    def create_header(self):
        '''
        Creates header for csv file (string)
        This is its own function in case we implement variable grid sizes.
        '''
        N_positions = 42
        header      = ''
        
        for p in range(1, N_positions + 1):
            if(p < 10):
                header += 'pos_0{},'.format(str(p))
            else :
                header += 'pos_{},'.format(str(p))

        header += 'winner\n'

        return header
        
        

    def make_game_array(self, Board):
        '''
        Flatten board grid and append the winner marker (1, 0, -1)
        '''
        flat = self.Board.grid.flatten()
        game_array = [int(f) for f in flat]
        game_array.append(self.Board.winner)

        return game_array
                  
