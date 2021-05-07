import os
import pandas as pd
import numpy as np
import warnings
import sqlite3
import json


class WodPlanner:
    def __init__(self, new_wod=False):
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(current_path, 'db/wodplanner.db')
        self.wod_name = os.path.join(current_path, 'db/wods.h5')

        if new_wod:
            self.db, self.c = self._initialize_wod_db()
        else:
            self.db, self.c = self._load_wod_db()

        self.movement_dict = {'g': 'Gymnastics', 'w': 'Weightlifting', 'm': 'Monostructural'}

    def _initialize_wod_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("select name from sqlite_master where type = 'table';")
        tables = c.fetchall()

        if ('wods',) in tables:
            c.execute("DROP TABLE wods")

        c.execute("CREATE TABLE wods (wod_id int, data json)")

        return conn, c

    def _load_wod_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        c.execute("select name from sqlite_master where type = 'table';")
        tables = c.fetchall()

        if ('wods',) not in tables:
            c.execute("CREATE TABLE wods (wod_id int, data json)")

        return conn, c

    def _add_wod(self, date, strength_skill, sets_reps, movement, scheme, time_rounds, wod_movements, reps,
                 weights, comments=''):

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

        mydates = self.c.execute("select json_extract(data, '$.Date') from wods").fetchall()
        mydates = [x[0] for x in mydates]

        if date in mydates:
            warnings.warn('Date already exists. Workout is not added.')
        else:
            self.c.execute("insert into wods values (?, ?)", [1, json.dumps(wod)])  # TODO: change wod ID
            self.db.commit()

    def _add_movement(self, movement_name: str, key: str):
        if key not in self.movement_dict.keys():
            raise ValueError('Incorrect key %s' % key)

        self.c.execute('SELECT MAX(id) from movements;')
        idx_max = self.c.fetchall()[0][0]

        self.c.execute("SELECT COUNT(1) FROM movements WHERE Movement = '%s';" % movement_name)
        movement_count = self.c.fetchall()[0][0]

        if movement_count == 0:
            self.c.execute("insert into movements values (?, ?, ?)", [idx_max + 1, movement_name,
                                                                      self.movement_dict[key]])
            self.db.commit()
        else:
            warnings.warn("%s is already included in the database and cannot be added" % movement_name)

    def _drop_movement(self, movement_name: str):
        self.c.execute("DELETE FROM movements WHERE Movement='%s';" % movement_name)
        self.db.commit()
