import os
import pandas as pd
import numpy as np
import warnings


class WodPlanner:
    def __init__(self, new_wod=False):
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(current_path, 'db/movements.h5')
        self.wod_name = os.path.join(current_path, 'db/wods.h5')

        if new_wod:
            self.wod = self._initialize_wod_db()
        else:
            self.wod = self._load_wod_db()

        self.movement_dict = {}
        self.df_g, self.df_w, self.df_m = self._load_movements()

    def _initialize_wod_db(self):
        columns = ['Date', 'Strength/Skill', 'Sets_reps', 'Movement', 'Scheme',
                   'Time_rounds', 'Wod_Movements', 'Reps', 'Weight', 'Comments']

        df = pd.DataFrame(columns=columns)
        df.to_hdf(self.wod_name, key='wod')

        return df

    def _load_wod_db(self):
        return pd.read_hdf(self.wod_name)

    def _add_wod(self, date, strength_skill, sets_reps, movement, scheme, time_rounds, wod_movements, reps,
                 weights, comments=None):

        wod = {'Date': date,
               'Strength/Skill': strength_skill,
               'Sets_reps': sets_reps,
               'Movement': movement,
               'Scheme': scheme,
               'Time_rounds': time_rounds,
               'Wod_Movements': wod_movements,
               'Reps': reps,
               'Weight': weights,
               'Comments': comments}

        self.wod = pd.concat([self.wod, pd.json_normalize(wod)])
        # self.wod['Date'] = pd.to_datetime(self.wod['Date'], format='%d/%m/%Y')

        self.wod.to_hdf(self.wod_name, key='wod')

    def _load_movements(self):
        df_g = pd.read_hdf(self.db_name, 'g')
        df_w = pd.read_hdf(self.db_name, 'w')
        df_m = pd.read_hdf(self.db_name, 'm')

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
            df.reset_index(drop=True).to_hdf(self.db_name, key=key)

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
            df.to_hdf(self.db_name, key=key)

            self.df_g, self.df_w, self.df_m = self._load_movements()
        else:
            warnings.warn("%s is not included in the database and cannot be removed" % movement_name)
