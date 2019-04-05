from sklearn.metrics import (r2_score,
                             mean_squared_error,
                             explained_variance_score,
                             mean_absolute_error,
                             mean_squared_log_error,
                             median_absolute_error)

from sklearn.linear_model import SGDRegressor, LinearRegression, Lasso, ElasticNet
from sklearn.ensemble import GradientBoostingRegressor, BaggingRegressor, RandomForestRegressor, AdaBoostRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

from sklearn.model_selection import cross_val_score
import numpy as np
import pickle

from sklearn.model_selection import cross_val_score

from sklearn.model_selection import train_test_split



def train_ensemble(boat_model, X, y):
    def cv(model, n):
        return cross_val_score(model, X, y, cv=n)

    def evaluate(model, name):
        y_pred = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        percentage_error = rmse / np.median(y_test)

        return percentage_error

    def predict(model, name):
        model.fit(X_train, y_train)
        # save_model(model_name)
        error = evaluate(model, name)
        # cv_scores = cv(model,5)
        errors[name] = error.round(3)
        regs[name] = pickle.dumps(model)

    def train():
        sgd = SGDRegressor()
        # predict(sgd, 'SGDRegressor')

        lasso = Lasso()
        predict(lasso, 'Lasso')

        linreg = LinearRegression()
        predict(linreg, 'LinearRegression')

        adb = AdaBoostRegressor()
        predict(adb, 'AdaBoostRegressor')

        knn = KNeighborsRegressor()
        predict(knn, 'KNeighborsRegressor')

        tr = DecisionTreeRegressor()
        predict(tr, 'DecisionTreeRegressor')

        baggins = BaggingRegressor()
        predict(baggins, 'BaggingRegressor')

        gbr = GradientBoostingRegressor(loss='lad', max_depth=6)
        predict(gbr, 'GradientBoostingRegressor')

        rf = RandomForestRegressor()
        predict(rf, 'RandomForestRegressor')

        #xgbr = XGBRegressor()
        #predict(xgbr, 'XGBRegressor')

    errors = dict()
    regs = dict()

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
    train()

    best_reg_name = min(errors, key=errors.get)
    best_reg = regs.get(best_reg_name)

    errs = list(errors.values())

    median_error = np.median(errs)

    min_error = min(errs)

    return min_error, best_reg_name, best_reg
