import shap
from sklearn.inspection import permutation_importance

class AugmentoModelInterpretor:
    def __init__(self, pipeline, X_train):
        self.pipeline = pipeline
        self.X_train = X_train
        # Extract raw model
        self.model = pipeline.steps[-1][1]

    def shap_summary(self):
        expl = shap.Explainer(self.model, self.X_train)
        shap_values = expl(self.X_train)
        shap.summary_plot(shap_values, self.X_train)

    def permutation_importance(self, X_test, y_test):
        r = permutation_importance(self.pipeline, X_test, y_test, n_repeats=10)
        return r.importances_mean, r.importances_std
