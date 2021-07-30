from requests.auth import HTTPDigestAuth
from timedata import Timedata
from model import Model
from robtargetdata import *

class Data:
    def __init__(self):
        """All important params use in this program are storing here"""
        self.host = "http://localhost:80/"
        self.username = 'Default User'
        self.password = 'robotics'

        # Attributes relate to ABB Robot Studio
        self.signals = [['/rw/iosystem/signals/doState;state', '/rw/iosystem/signals/doTime;state'], ['2', '2']]
        self.robtargets = ['pPickTemp', 'pPlaceTemp', 'pGetMid']
        self.robtargetslist = ['pPickTemp', 'pPlaceTemp', 'pMidP']
        self.clk = 'time'

        # Folder
        self.model_file = './modelfile/model_IRB660_path_optimizer.h5'
        self.csvfolder = './csvfile/'

        # Main Object
        self.digest_auth = HTTPDigestAuth(self.username, self.password)
        self.robtarget = Robtarget(self.host, self.username, self.password, self.robtargets)
        self.robtargetlist = RobtargetList(self.host, self.username, self.password, self.robtargetslist)
        self.time = Timedata(self.host, self.username, self.password, self.clk)
        self.model = Model(self.model_file)

        # train.py
        self.train_file = self.csvfolder + 'rws_train.csv'
        self.train_round = list()
        self.train_data = list()

        # predict.py
        self.predict_file = self.csvfolder + 'model_predict.csv'    # Inspect the program
        self.random_round = 30
        self.save_random = 10                      # How many randomC values (time sorted) you want to save?

        # test.py
        self.test_file = self.csvfolder + 'rws_test.csv'
        self.test_round = list()
        self.test_data = list()

        # optimize.py
        self.optimize_file = self.csvfolder + 'rws_optimize.csv'
        self.optimize_round = list()

        # execute.py
        self.execute_file = self.csvfolder + 'rws_execute.csv'
        self.execute_round = list()
        self.execute_data = list()



        # <-- For building new model -->

        # copy
        self.copy_file = self.csvfolder + 'rws_copy.csv'
        self.copy_data = list()

        # model_train.py
        self.model_train_file = self.csvfolder + 'model_train.csv'
        self.model_train_round = list()
        self.model_train_data = list()

