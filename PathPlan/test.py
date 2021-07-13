import numpy as np
from gym import spaces

def main():
    high = np.array([1., 1., 8], dtype=np.float32)
    action_space = spaces.Box(
            low=-2.,
            high=2., shape=(1,),
            dtype=np.float32
        )
    observation_space = spaces.Box(
            low=-high,
            high=high,
            dtype=np.float32
    )
    print(action_space, observation_space)

if __name__ == "__main__":
     main()