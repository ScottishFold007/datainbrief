print('error/median', percentage_error, '\n')

print('median price', int(np.median(y_test)))

print("\n scores for", name)

print('r2 score', model.score(X_test, y_test))

print('rmse:', int(rmse))

print('explained_variance_score', explained_variance_score(y_test, y_pred))

print('mean_absolute_error', mean_absolute_error(y_test, y_pred))

print('mean_squared_log_error', mean_squared_log_error(y_test, y_pred))

print('median_absolute_error', median_absolute_error(y_test, y_pred))
