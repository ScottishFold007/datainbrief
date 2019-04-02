import pickle

model_path = ''

model = pickle.loads(model_path)


def predict_price(features):
    predicted = model.predict(features)
    return predicted
