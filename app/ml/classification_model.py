import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from config import Config
from app.ml.data_processor import DataProcessor

class ProductivityClassifier:
    def __init__(self):
        self.model_path = os.path.join(Config.ML_MODEL_DIR, 'productivity_classifier.joblib')
        self.scaler_path = os.path.join(Config.ML_MODEL_DIR, 'classifier_scaler.joblib')
        self.model = None
        self.scaler = None
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(Config.ML_MODEL_DIR, exist_ok=True)

    def train(self, records):
        """Trains the classification model using daily records."""
        df = DataProcessor.records_to_dataframe(records)
        X, _, y_clf, _ = DataProcessor.extract_features(df)
        
        if X is None or len(X) < 5:
            return False, "Insufficient data for classification model training."
            
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y_clf)
        
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        return True, "Classification model trained and saved successfully."

    def load(self):
        """Loads saved classification model and scaler."""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            return True
        return False

    def predict(self, sleep_hours, work_hours, screen_time, exercise_mins, stress_level):
        """Predicts productivity category (Low / Medium / High)."""
        if self.model is None or self.scaler is None:
            if not self.load():
                # Rule fallback
                if stress_level >= 7 or sleep_hours < 5.5:
                    return 'Low'
                elif work_hours >= 6 and sleep_hours >= 7 and stress_level <= 4:
                    return 'High'
                return 'Medium'

        work_sleep_ratio = work_hours / sleep_hours if sleep_hours > 0 else 0.0
        active_hours = work_hours + (exercise_mins / 60.0)
        screen_work_diff = screen_time - work_hours
        
        feature_names = ['sleep_hours', 'work_hours', 'screen_time', 'exercise_mins', 'stress_level', 'work_sleep_ratio', 'active_hours', 'screen_work_diff']
        input_data = pd.DataFrame([[sleep_hours, work_hours, screen_time, exercise_mins, stress_level,
                                work_sleep_ratio, active_hours, screen_work_diff]], columns=feature_names)
        
        input_scaled = self.scaler.transform(input_data)
        predicted_level = self.model.predict(input_scaled)[0]
        return str(predicted_level)
