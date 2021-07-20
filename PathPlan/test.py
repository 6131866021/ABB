import numpy as np
import pandas as pd

def main():
    # for i in range(5):
    #     valueA = np.array([1300.0, -300.0, 1000.0])
    #     valueB = np.array([1550.0, 1000.0, 700.0])
    #     valueC = np.array([1500.0, 300.0, 850.0])
    #     invalid, randomPoint = True, []

    #     mean = [(valueA[i] + valueB[i])/2 for i in range(3)]
    #     std = [abs(valueA[i] - valueB[i])/4 for i in range(3)]
    #     sm = abs(valueA[i] - valueB[i])/4
    #     mean[2] = valueA[2] + sm if valueA[2] > valueB[2] else valueB[2] + sm
    #     print(mean, std)
        
    #     while invalid:
    #         randomPoint = [np.random.normal(loc=mean[i], scale=std[i]) for i in range(3)]
    #         print(randomPoint)
    #         x1, x2 = valueA[0], valueB[0]
    #         y1, y2 = valueA[1], valueB[1]
    #         z1, z2 = valueA[2], valueB[2]
    #         x_valid = (x1 < randomPoint[0] < x2) or (x2 < randomPoint[0] <x1)
    #         y_valid = (y1 < randomPoint[1] < y2) or (y2 < randomPoint[1] <y1)
    #         # z_valid = (z1 < randomPoint[2] < z2) or (z2 < randomPoint[2] <z2)
    #         invalid = not(x_valid and y_valid)

    #     print(randomPoint)

    df = pd.read_csv('rws_train_palletizing.csv')
    row = df.iloc[1]
    print(row['A_X'], row['A_Y'])



if __name__ == "__main__":
    main()