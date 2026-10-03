import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from config import Config
from app.ml.data_processor import DataProcessor

class ProductivityRegressor:
    def __init__(self):
        self.model_path = os.path.join(Config.ML_MODEL_DIR, 'productivity_regressor.joblib')
        self.scaler_path = os.path.join(Config.ML_MODEL_DIR, 'regressor_scaler.joblib')
        self.model = None
        self.scaler = None
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(Config.ML_MODEL_DIR, exist_ok=True)

    def train(self, records):
        """Trains the regression model using daily records."""
        df = DataProcessor.records_to_dataframe(records)
        X, y_reg, _, feature_names = DataProcessor.extract_features(df)
        
        if X is None or len(X) < 5:
            return False, "Insufficient data for regression model training (at least 5 records needed)."
            
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Use Random Forest Regressor for non-linear daily habit patterns
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y_reg)
        
        # Save model & scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        return True, "Regression model trained and saved successfully."

    def load(self):
        """Loads saved regression model and scaler."""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            return True
        return False

    def predict(self, sleep_hours, work_hours, screen_time, exercise_mins, stress_level):
        """Predicts productivity score for given input metrics."""
        if self.model is None or self.scaler is None:
            if not self.load():
                # Rule-based fallback if model not yet trained
                base_score = (sleep_hours / 8.0) * 30 + (work_hours / 8.0) * 40 + (exercise_mins / 30.0) * 15 - (stress_level / 10.0) * 15
                return round(max(10.0, min(100.0, base_score)), 2)

        # Feature engineering matching DataProcessor
        work_sleep_ratio = work_hours / sleep_hours if sleep_hours > 0 else 0.0
        active_hours = work_hours + (exercise_mins / 60.0)
        screen_work_diff = screen_time - work_hours
        
        feature_names = ['sleep_hours', 'work_hours', 'screen_time', 'exercise_mins', 'stress_level', 'work_sleep_ratio', 'active_hours', 'screen_work_diff']
        input_data = pd.DataFrame([[sleep_hours, work_hours, screen_time, exercise_mins, stress_level,
                                work_sleep_ratio, active_hours, screen_work_diff]], columns=feature_names)
        
        input_scaled = self.scaler.transform(input_data)
        predicted_score = self.model.predict(input_scaled)[0]
        return round(float(max(0.0, min(100.0, predicted_score))), 2)
