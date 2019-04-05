import numpy as np
import pandas as pd
import pickle, random, re, os
from src.db.credentials import db

from src.models.evaluate import train_ensemble

model_path = ''

model = pickle.loads(model_path)


def connect():
    query = {'year': {"$exists": True}, 'hours': {"$exists": True}, 'power': {"$exists": True},
             'details.engine/fuel type': {"$exists": True}}
    cursor = db.boats.find(query)
    return cursor


def load(cursor):
    df = pd.DataFrame(list(cursor))
    return df


def ready(df):
    df = df[pd.notnull(df['year'])]
    df = df[pd.notnull(df['length'])]

    df = df[df['hours'] != 'missing']

    df = df[pd.to_numeric(df['price'], errors='coerce').notnull()]
    df = df[pd.to_numeric(df['power'], errors='coerce').notnull()]

    def make_int(field):
        try:
            df[field] = df[field].astype(int)
        except TypeError:
            pass

    make_int('hours')
    make_int('price')
    make_int('year')
    make_int('length')
    make_int('power')

    def get_fuel():
        for index, row in df.iterrows():
            try:
                details = row['details']
                if 'engine/fuel type' in details:
                    fuel = details['engine/fuel type']
                    if fuel:
                        df.at[index, 'fuel'] = fuel
            except KeyError as e:
                continue

    get_fuel()

    return df


def get_model_counts(df):
    return df.model.value_counts().rename_axis('model').reset_index(name='count')


def get_X_y(df):
    df = df[['price', 'length', 'year', 'power', 'hours', 'country', 'fuel']]
    df = df.dropna()
    y = df['price']
    X = df.drop(columns=['price'])
    X = pd.get_dummies(X, columns=['country', 'fuel'])

    return X, y


def train_test(df, model_count):
    total_errors = list()
    best_regs = dict()
    bads = list()
    model_counts = get_model_counts(df)

    model_sorted_by_counts = model_counts['model']

    for boat_model in model_sorted_by_counts[:model_count]:

        df_single_model = df[df['model'] == boat_model]

        X, y = get_X_y(df_single_model)

        min_error, best_reg_name, best_reg = train_ensemble(boat_model, X, y)

        best_regs[boat_model] = dict()
        best_regs[boat_model][best_reg_name] = best_reg

        total_errors.append(min_error)

        print(boat_model, (min_error * 100).round(2), '\n')

        if min_error > 0.2:
            bads.append(boat_model)

    return total_errors, bads, best_regs


def predict_price(features):
    predicted = model.predict(features)
    return predicted


def get_df():
    cursor = connect()
    df = load(cursor)
    df = ready(df)
    return df


df = get_df()


def test():
    total_errors, bads, best_regs = train_test(df, 100)
    print('\n median deviation from true median price %', (np.median(total_errors) * 100).round(2))
    print('\n avg deviation from true median price %', (np.mean(total_errors) * 100).round(2))
