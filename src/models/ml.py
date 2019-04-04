import pickle
from src.db import db_api

model_path = ''

model = pickle.loads(model_path)

def load():
    pass


    

def predict_price(features):
    predicted = model.predict(features)
    return predicted
