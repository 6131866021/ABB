from requests.auth import HTTPDigestAuth
from robtarget import *
from robtargetlist import *
from timedata import *
from model import *

class Data:
    def __init__(self):
        self.host = "http://localhost:80/"
        self.username = 'Default User'
        self.password = 'robotics'

        self.signals = [['/rw/iosystem/signals/doState;state', '/rw/iosystem/signals/doTime;state'], ['2', '2']]
        self.robtargets = ['pPickTemp', 'pPlaceTemp', 'pGetMid']
        self.robtargetslist = ['pPickTemp', 'pPlaceTemp', 'pMidP']
        self.clk = 'time'
        self.model_file = 'Path_Optimizer_Savedmodel.h5'

        # Main Object
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.robtarget = Robtarget(self.host, self.username, self.password, self.robtargets)
        self.robtargetlist = RobtargetList(self.host, self.username, self.password, self.robtargetslist)
        self.time = Time(self.host, self.username, self.password, self.clk)
        self.model = Model(self.model_file)

        # train.py
        self.train_file = 'rws_train.csv'
        self.train_round = list()
        self.train_data = list()

        # predict.py
        # self.predict_file = 'model_predict.csv'   # Inspect the program
        self.predict_file = 'rws_copy.csv'
        self.random_round = 1000
        self.save_random = 10           # How many randomC values (time sorted) you want to save?

        # test.py


        # execute.py
        self.execute_file = 'rws_execute.csv'
        self.execute_round = list()
        self.execute_data = list()

        # copy
        self.copy_file = 'rws_copy.csv'
        self.copy_data = list()

        # model_train.py
        self.model_train_file = 'model_train.csv'
        self.model_train_round = list()
        self.model_train_data = list()

