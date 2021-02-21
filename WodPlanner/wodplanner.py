import os
import pandas as pd
import numpy as np


class WodPlanner:
    def __init__(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.db = os.path.join(current_path, 'db/movements.h5')

        self.df_g, self.df_w, self.df_m = self._load_movements()

    def _load_movements(self):
        df_g = pd.read_hdf(self.db, 'g')
        df_w = pd.read_hdf(self.db, 'w')
        df_m = pd.read_hdf(self.db, 'm')

        return df_g, df_w, df_m

    def _add_movement(self, movement_name: str, key: str):
        columns = self.df_g.columns
        data = np.array([movement_name, key])
        data = data.reshape(1, -1)
        print(data.shape)

        df = pd.DataFrame(data=data, columns=columns)
        print(df)
