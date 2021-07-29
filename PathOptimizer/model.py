from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import plot_model
from tensorboard.plugins.hparams import api as hp
from tensorflow.keras.models import model_from_json

# from sklearn.compose import make_column_transformer
# from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

class Model:
    def __init__(self, modelfile):
        """Path Optimizer Deep Learning Model for IRB660."""
        self.model = keras.models.load_model(modelfile)

    def summary(self):
        """Operations for writing summary data, for use in analysis and visualization."""
        print(self.model.summary())
    
    def plot_model(self):
        """
        Converts a Keras model to dot format and save to a file.
        `Returns`
        A Jupyter notebook Image object if Jupyter is installed. This enables in-line display of the model plots in notebooks.
        """
        plot_model(self.model, to_file='model.png', show_shapes=True, show_dtype=True)

    def evaluate(self, X_test, y_test):
        return self.model.evaluate(X_test, y_test)

    def predict(self, X_test):
        return self.model.predict(X_test)


# Evaluate Success with loss: 0.0216 - mse: 0.0216