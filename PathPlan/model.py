"""
This model has implemented from 
'https://github.com/kimmyungsup/Reinforcement-Learning-with-Tensorflow-2.0/blob/master/DDPG_tf20/ddpg_tf20.py'
"""

import requests
from requests import auth
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import urllib.parse
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers, losses, Model
from .env import *
from .hyperparam import *

# create environment and actions
env = RobotEnv()

class ActorModel(Model):
    def __init__(self):
        super(ActorModel, self).__init__()
        self.layer_a1 = Dense(128, activation='relu')
        self.layer_a2 = Dense(128, activation='relu')
        
    def call(self, state):
        layer_a1 = self.layer_a1(state)
        layer_a2 = self.layer_a2(layer_a1)
        logits = self.logits(layer_a2)
        return logits

class CriticModel(Model):
    def __init__(self):
        super(CriticModel, self).__init__()
        self.layer_c1 = Dense(128, activation='relu')
        self.layer_c2 = Dense(128, activation='relu')
        self.value = Dense(1)

    def call(self, state_action):
        layer_c1 = self.layer_c1(state_action)
        layer_c2 = self.layer_c2(layer_c1)
        value = self.value(layer_c2)
        return value