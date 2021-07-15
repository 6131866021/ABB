import numpy as np
import pandas as pd
import tensorflow as tf

def main():
    df = pd.read_csv(r'C:\Users\_\Desktop\ABB\PathPlan\test.csv')
    df.head()
    tf.random.set_seed(42)
    
    X = df.drop("time", axis=1)
    y = df["time"]
    Xtrain, X_test, y_train, y_test = X[:0.8*len(X)], X[0.8*len(X):], y[:0.8*len(X)], y[0.8*len(y):]
    df_model = tf.keras.Sequential([tf.keras.layers.Dense(100),
                                    tf.keras.layers.Dense(10)])
    df_model.compile(loss=tf.keras.losses.mae,
                        optimizer=tf.keras.optimizers.Adam(),
                        metrics=["mae"])
    df_model.fit(X_train, y_train, epochs=2000, verbose=0)  
if __name__ == "__main__":
    main()