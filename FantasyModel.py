from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
import xgboost as xgb

class FantasyModel:
    def __init__(self,position):
        if position == 1:   # goalkeeper
            self.model = xgb.XGBRegressor(
                n_estimators=1000,       # The number of boosting rounds or trees to build. More trees can be better but may lead to overfitting.
                learning_rate=0.1,      # Step size shrinkage to prevent overfitting. A lower value makes the boosting process more conservative.
                max_depth=8,             # The maximum depth of each tree. Deeper trees capture more complex patterns but are more likely to overfit.
                subsample=0.8,           # The fraction of the training data to be randomly sampled for each tree. Prevents overfitting.
                colsample_bytree=0.4,    # The fraction of features (columns) to be randomly sampled when building each tree.
                gamma=0,               # Minimum loss reduction required to make a split. A higher gamma makes the algorithm more conservative.
                reg_alpha=1,         # L1 regularization on weights. Encourages sparsity, which can be useful in high-dimensional data.
                reg_lambda=1,            # L2 regularization on weights. A standard regularization technique to prevent overfitting by smoothing weights.
                objective='reg:squarederror', # Defines the loss function to be minimized. 'reg:squarederror' is for regression tasks.

                random_state=27,
                n_jobs=-1
            )
        elif position == 2: # defenders
            self.model = xgb.XGBRegressor(
                n_estimators=1000,       # The number of boosting rounds or trees to build. More trees can be better but may lead to overfitting.
                learning_rate=0.005,      # Step size shrinkage to prevent overfitting. A lower value makes the boosting process more conservative.
                max_depth=4,             # The maximum depth of each tree. Deeper trees capture more complex patterns but are more likely to overfit.
                subsample=0.8,           # The fraction of the training data to be randomly sampled for each tree. Prevents overfitting.
                colsample_bytree=0.2,    # The fraction of features (columns) to be randomly sampled when building each tree.
                gamma=0,                  # Minimum loss reduction required to make a split. A higher gamma makes the algorithm more conservative.
                reg_alpha=0,              # L1 regularization on weights. Encourages sparsity, which can be useful in high-dimensional data.
                reg_lambda=1,             # L2 regularization on weights. A standard regularization technique to prevent overfitting by smoothing weights.
                objective='reg:squarederror', # Defines the loss function to be minimized. 'reg:squarederror' is for regression tasks.

                random_state=27,
                n_jobs=-1
            )
        else: # attackers and midfielders
            self.model = xgb.XGBRegressor(
                n_estimators=1000,       # The number of boosting rounds or trees to build. More trees can be better but may lead to overfitting.
                learning_rate=0.06,      # Step size shrinkage to prevent overfitting. A lower value makes the boosting process more conservative.
                max_depth=8,             # The maximum depth of each tree. Deeper trees capture more complex patterns but are more likely to overfit.
                subsample=0.5,           # The fraction of the training data to be randomly sampled for each tree. Prevents overfitting.
                colsample_bytree=0.2,    # The fraction of features (columns) to be randomly sampled when building each tree.
                gamma=0,                  # Minimum loss reduction required to make a split. A higher gamma makes the algorithm more conservative.
                reg_alpha=0,              # L1 regularization on weights. Encourages sparsity, which can be useful in high-dimensional data.
                reg_lambda=0,             # L2 regularization on weights. A standard regularization technique to prevent overfitting by smoothing weights.
                objective='reg:squarederror', # Defines the loss function to be minimized. 'reg:squarederror' is for regression tasks.

                random_state=27,
                n_jobs=-1
            )

    def train(self, X, y):
        # Convert object columns to numeric
        for col in X.columns:
            if X[col].dtype == "object":
                X[col] = pd.to_numeric(X[col], errors="coerce")

        y = np.clip(y, None, np.percentile(y, 98))
        self.model.fit(X, y)

    def predict(self, X):
        for col in X.columns:
            if X[col].dtype == "object":
                X[col] = pd.to_numeric(X[col], errors="coerce")
        return np.round(self.model.predict(X), 2)
