import pandas as pd
import numpy as np
from data import *

def predict():
    """
    Call deep learning model to predict the time with given features
    (robtargetA, robtargetB, and random of robtargetC)
    """
    ws = Data()
    df = pd.read_csv(ws.train_file)
    predict_df = list()

    for i in range(len(df)):
        row = df.iloc[i]
        predict_row = list()

        # How many randomC values you want?
        for j in range(ws.random_round):
            random_row = [row['A_X'], row['A_Y'], row['A_Z'], row['B_X'], row['B_Y'], row['B_Z']]
            valueC = randomC_data(random_row[0:3], random_row[3:])
            
            for k in range(3):
                random_row.append(valueC[k])

            predict_row.append(random_row)

        X_test = pd.DataFrame(predict_row, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z"])
        y_preds = ws.model.predict(X_test)
        prediction = add_ypreds(X_test, y_preds)
        prediction.sort_values('Predict Time', inplace=True)

        # How many randomC values (time sorted) you want to save?
        for j in range(ws.save_random):
            sr = prediction.iloc[j]
            sort_row = [sr['A_X'], sr['A_Y'], sr['A_Z'], sr['B_X'], sr['B_Y'], sr['B_Z'], sr['C_X'], sr['C_Y'], sr['C_Z'], sr['Predict Time']] 
            predict_df.append(sort_row)

    predict_df = pd.DataFrame(predict_df, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Predict Time"])
    predict_df.to_csv(ws.predict_file, header=True, index=False)

def randomC_data(a, b):
    """
    This function is the same as in robtarget.py
    Random self.changeC value using normal distribution where
    mean is the point at the center of point A and point B,
    standard deviation is the difference between pointA and pointB
    divided by 8 in each respective coordinate (X, Y, Z)
    """
    validPoint = False
    randomPoint = list()
    mean = [(a[i]+b[i])/2 for i in range(3)]
    std = [abs(a[i]-b[i])/8 for i in range(3)]
    
    # Change Z-Axis Standard Deviation
    std[2] = abs(a[2]-b[2])/6

    # While True Loop that will exit when values in X, Y, Z axis are valid
    while not validPoint:
        randomPoint = [np.random.normal(loc=mean[i], scale=std[i]) for i in range(3)]
        x1, x2 = a[0], b[0]
        y1, y2 = a[1], b[1]
        z1, z2 = a[2], b[2]
        x_valid = (x1 < randomPoint[0] < x2) or (x2 < randomPoint[0] < x1)
        y_valid = (y1 < randomPoint[1] < y2) or (y2 < randomPoint[1] < y1)
        z_valid = (z1 < randomPoint[2] < z2) or (z2 < randomPoint[2] < z1) 
        validPoint = x_valid and y_valid and z_valid
        return_randomC = [np.round(randomPoint[i], 2) for i in range(3)]

    return return_randomC

def add_ypreds(X_test, y_preds):
    """This function uses to aggregate features and predict label into one DataFrame"""
    df = list()

    for i in range(len(X_test)):
        row = list(X_test.iloc[i])
        row.append(np.mean(y_preds[i]))
        df.append(row)

    return pd.DataFrame(df, columns=["A_X", "A_Y", "A_Z", "B_X", "B_Y", "B_Z", "C_X", "C_Y", "C_Z", "Predict Time"])
