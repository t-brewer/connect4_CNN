#!/usr/bin/env python3

# Basic Libraries
import numpy as np

# Keras Libraries (ANNs)
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Flatten, AveragePooling2D, MaxPooling2D
from keras import losses
from keras import optimizers

from sklearn.model_selection import train_test_split


def generate_CNN(conv_layers=[], dense_layers=[], lr=0.01):
    '''
    Generate a 2D Convolutional Neural Network.
    Input parameters are : 
    conv_layers  : a list of Conv2D layers (before flattening the values for the dense layers)
    dense_layers : a list of Dense layers (after flattening)
    lr           : learning rate for the optimizer
    '''

    # Basic Input Layers : Conv2D layer with 4x4 filter, followed by 2x2 filter
    # This seems to work pretty well, so it will be kept for all model variations
    model = Sequential()
    model.add(Conv2D(42, (4,4), input_shape=(6,7,1), activation='tanh', padding='same'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2,2)))

    # Add pre-flattening layers
    if len(conv_layers) != 0:
        for l in conv_layers:
            model.add(l)
    
    model.add(Flatten())

    # Add Post flattening layers
    if len(dense_layers) > 0:
        for l in new_layers:
            model.add(l)

    model.add(Dense(1,   activation='sigmoid'))

    # Define optimizer with provided learning rate
    adam_optimizer = optimizers.Adam(lr=lr)
    
    # compile and return model :
    model.compile(optimizer=adam_optimizer, loss=losses.mean_squared_error, metrics=['accuracy'])
    return model


def load_shape_ttsplit(filename, test_size=0.3):
    ''' 
    Custom function to load reshape and train_test_split data from game data base.
    Somewhat specific function, not great for general use.
    '''

    data = np.genfromtxt(filename, delimiter=',')
    
    X0 = data[:, :-1].copy()
    y0 = data[:, -1].copy()

    for i, v in enumerate(y0):
        if(v != 1):
            y0[i] = 0

    X0 = X0.reshape(X0.shape[0], 6, 7, 1)
    
    return train_test_split(X0, y0, test_size=test_size)

    
    
    
