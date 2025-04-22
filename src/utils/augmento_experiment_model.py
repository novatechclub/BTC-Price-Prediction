# augmento_experiment_modeller.py

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.ensemble import RandomForestClassifier

class AugmentoExperimentModeller:
    def __init__(self, df, target_col, feature_cols):
        self.df = df.copy()
        self.y = self.df[target_col]
        self.X = self.df[feature_cols]
        self.models = {}

    def build_pipeline(self, model_name, model, scale=True):
        steps = []
        if scale:
            steps.append(('scaler', StandardScaler()))
        steps.append((model_name, model))
        self.models[model_name] = Pipeline(steps)

    def evaluate(self, model_name, cv_splits=5, scoring='accuracy'):
        tscv = TimeSeriesSplit(n_splits=cv_splits)
        scores = cross_val_score(self.models[model_name], self.X, self.y,
                                 cv=tscv, scoring=scoring)
        return scores

    def grid_search(self, model_name, param_grid, cv_splits=5, scoring='accuracy'):
        from sklearn.model_selection import GridSearchCV
        tscv = TimeSeriesSplit(n_splits=cv_splits)
        gs = GridSearchCV(self.models[model_name], param_grid,
                          cv=tscv, scoring=scoring, n_jobs=-1)
        gs.fit(self.X, self.y)
        return gs.best_params_, gs.best_score_
