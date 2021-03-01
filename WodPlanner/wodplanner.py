import os
import pandas as pd
import numpy as np
import warnings


class WodPlanner:
    def __init__(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.db = os.path.join(current_path, 'db/movements.h5')

        self.movement_dict = {}
        self.df_g, self.df_w, self.df_m = self._load_movements()

    def _load_movements(self):
        df_g = pd.read_hdf(self.db, 'g')
        df_w = pd.read_hdf(self.db, 'w')
        df_m = pd.read_hdf(self.db, 'm')

        self.movement_dict['g'] = df_g['Type'].unique()[0]
        self.movement_dict['w'] = df_w['Type'].unique()[0]
        self.movement_dict['m'] = df_m['Type'].unique()[0]

        return df_g, df_w, df_m

    def _add_movement(self, movement_name: str, key: str):
        if key == 'g':
            df = self.df_g
        elif key == 'm':
            df = self.df_m
        elif key == 'w':
            df = self.df_w
        else:
            raise ValueError('Incorrect key %s' % key)

        if movement_name in df['Movement'].values:
            warnings.warn("%s is already included in the database" % movement_name)
        else:
            columns = df.columns
            data = np.array([movement_name, self.movement_dict[key]])
            data = data.reshape(1, -1)

            df_new = pd.DataFrame(data=data, columns=columns)
            df = pd.concat([df, df_new])
            df.reset_index(drop=True).to_hdf(self.db, key=key)

            self.df_g, self.df_w, self.df_m = self._load_movements()

    def _drop_movement(self, movement_name: str, key: str):
        if key == 'g':
            df = self.df_g
        elif key == 'm':
            df = self.df_m
        elif key == 'w':
            df = self.df_w
        else:
            raise ValueError('Incorrect key %s' % key)

        if movement_name in df['Movement'].values:
            idx = df['Movement'] == movement_name
            df = df.loc[~idx].reset_index(drop=True)
            df.to_hdf(self.db, key=key)

            self.df_g, self.df_w, self.df_m = self._load_movements()
        else:
            warnings.warn("%s is not included in the database and cannot be removed" % movement_name)