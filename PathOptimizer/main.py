from robtarget import *
from robtargetlist import RobtargetList
from timedata import *
from model import Model
from data import *

from train import *
from predict import *
from execute import *
from model_train import *

import pandas as pd
import numpy as np

# from sklearn.compose import make_column_transformer
# from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

host = "http://localhost:80/"
username = 'Default User'
password = 'robotics'
    
robtargets = [['pPickTemp', 'pPlaceTemp', 'pGetMid'], ['pPickTemp', 'pPlaceTemp', 'pMidP']]
signals = [['/rw/iosystem/signals/doCheck;state', '/rw/iosystem/signals/doDrop;state'], ['2', '2']]
state_signal = [['/rw/iosystem/signals/doState;state', '/rw/iosystem/signals/doTime;state'], ['2', '2']]
time_pers = [['/rw/rapid/symbol/data/RAPID/T_ROB1/Module1/time;value', '/rw/iosystem/signals/doFeed4;state'], ['2', '2']]

# timeSubscriber = TimeSubscriber(host, username, password, time_pers[0], time_pers[1])
time = Time(host, username, password, 'time')
# Initiate Class Object
# subscriber = Subscriber(host, username, password, signals[0], signals[1])

ws = Data()


def main():
    # train_subscriber = TrainSubscriber(ws.host, ws.username, ws.password, ws.signals[0], ws.signals[1])
    # try:
    #     if train_subscriber.subscribe():
    #         train_subscriber.start_recv_events()
    # except KeyboardInterrupt:
    #     train_subscriber.close()

    # try:
    #     predict()
    # except KeyboardInterrupt:
    #     pass

    # execute_subscriber = ExecuteSubscriber(ws.host, ws.username, ws.password, ws.signals[0], ws.signals[1])
    # try:
    #     if execute_subscriber.subscribe():
    #         execute_subscriber.start_recv_events()
    # except KeyboardInterrupt:
    #     execute_subscriber.close()

    model_train_subscriber = ModelTrainSubscriber(ws.host, ws.username, ws.password, ws.signals[0], ws.signals[1])
    try:
        if model_train_subscriber.subscribe():
            model_train_subscriber.start_recv_events()
    except KeyboardInterrupt:
        model_train_subscriber.close()

def optimize():
    train_df = pd.read_csv(ws.train_file)
    execute_df = pd.read_csv(ws.execute_file)
    opt = list()

    for i in range(len(train_df)):
        train_time = train_df.iloc[i]['Time']
        execute_time = execute_df.iloc[i]['Time']
        if train_time > execute_time:
            opt.append(execute_time)
    
    print(f"Optimizer: {len(opt)}")
        
def copy():
    train_df = pd.read_csv(ws.train_file)
    for i in range(len(train_df)):
        row = train_df.iloc[i]
        copy = [row['A_X'], row['A_Y'], row['A_Z'], 
                row['B_X'], row['B_Y'], row['B_Z'], 
                row['C_X'], row['C_Y'], row['C_Z'], 
                row['Time']]
        for j in range(ws.save_random):
            ws.copy_data.append(copy)
    
    if len(ws.copy_data) != 0:
        save_df = pd.DataFrame(ws.copy_data, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Time"])
        save_df.to_csv(ws.copy_file, header=True, index=False)


if __name__ == "__main__":
    main()






# def test():
#     """Test deep learning model with robtarget A and B values"""
#     model = Model()
#     X_test = list()

#     if robtargets_1.getSymbol_data():
#         # Real data
#         d = list()
#         for a in range(3):
#             d.append(robtargets_1.valueA[0][a])
#         for b in range(3):
#             d.append(robtargets_1.valueB[0][b])
#         for c in range(3):
#             d.append((robtargets_1.valueA[0][c] + robtargets_1.valueB[0][c])/2)
#         X_test.append(d)
#         for i in range(100):
#             data = list()
#             robtargets_1.randomC_data()
#             for a in range(3):
#                 data.append(robtargets_1.valueA[0][a])
#             for b in range(3):
#                 data.append(robtargets_1.valueB[0][b])
#             for c in range(3):
#                 data.append(robtargets_1.changeC[0][c])
#             X_test.append(data)
    
#     X_test = pd.DataFrame(X_test, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z"])
#     y_preds = add_ypreds(X_test, model.predict(X_test))
#     y_preds.sort_values('Predict Time', inplace=True)
#     print(y_preds)

# def subscribe():
#     # try:
#     #     if subscriber.subscribe():
#     #         subscriber.start_recv_events()
#     # except KeyboardInterrupt:
#     #     subscriber.close()

#     # try:
#     #     if doState.subscribe():
#     #         doState.start_recv_events()
#     # except KeyboardInterrupt:
#     #     doState.close()

#     try:
#         if train_subscriber.subscribe():
#             train_subscriber.start_recv_events()
#     except KeyboardInterrupt:
#         train_subscriber.close()

# def test_model():
#     """Function to test to evaluate and predict the model"""
    
#     model = Model()
#     df = pd.read_csv('rws_train.csv')
#     X = df.drop('time', axis=1)
#     y = df['time']

#     train_size = 0.8
#     train_index = int(len(df)*train_size)

#     # Split data into train and test set
#     X_train = X[0:train_index]
#     X_test = X[train_index:]
#     y_train = y[0:train_index]
#     y_test = y[train_index:]

#     model.evaluate(X_test, y_test)
#     model.predict(X_test)

# def predict_rws():
#     model = Model()
#     df = pd.read_csv('rws_train_palletizing.csv')
#     new_df = list()

#     for i in range(len(df)):
#         predict_df = list()
#         row = df.iloc[i]

#         for j in range(500):
#             r = [row['A_X'], row['A_Y'], row['A_Z'], row['B_X'], row['B_Y'], row['B_Z']]
#             c = randomC_data_rws(r[0:3], r[3:])
#             for k in range(3):
#                 r.append(c[k])
#             predict_df.append(r)
#         predict_df = pd.DataFrame(predict_df, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z"])
#         y_preds = add_ypreds(predict_df, model.predict(predict_df))
#         y_preds.sort_values('Predict Time', inplace=True)

#         for j in range(10):
#             sr = y_preds.iloc[j]
#             sort_row = [sr['A_X'], sr['A_Y'], sr['A_Z'], sr['B_X'], sr['B_Y'], sr['B_Z'], sr['C_X'], sr['C_Y'], sr['C_Z'], sr['Predict Time']] 
#             new_df.append(sort_row)

#     n_df = pd.DataFrame(new_df, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Predict Time"])
#     n_df.to_csv(r'C:\Users\_\Desktop\ABB\PathOptimizer\rws_palletizing.csv', header=True)

# def ex_value():
#     df = pd.read_csv('rws_predict.csv')
#     print(df[:10])
#     prediction = list()
#     for i in range(10):
#         row = df.iloc[i]
#         prediction.append([row['C_X'], row['C_Y'], row['C_Z']])
#     if robtargets_2.getSymbol_data():
#         robtargets_2.changeC_listdata(prediction)
#         if robtargets_2.updateC_listdata():
#             print("Change")
