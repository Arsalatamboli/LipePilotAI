import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataProcessor:
    @staticmethod
    def records_to_dataframe(records):
        """Converts raw list of dictionary daily records into a Pandas DataFrame."""
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        # Ensure numeric columns are properly cast
        numeric_cols = ['sleep_hours', 'work_hours', 'screen_time', 'exercise_mins', 'stress_level', 'productivity_score']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                
        return df

    @staticmethod
    def extract_features(df):
        """Extracts feature matrix X and target vectors y_reg, y_clf."""
        if df.empty or len(df) < 5:
            return None, None, None, None

        # Base features
        feature_cols = ['sleep_hours', 'work_hours', 'screen_time', 'exercise_mins', 'stress_level']
        
        X = df[feature_cols].copy()
        
        # Feature engineering
        X['work_sleep_ratio'] = np.where(X['sleep_hours'] > 0, X['work_hours'] / X['sleep_hours'], 0.0)
        X['active_hours'] = X['work_hours'] + (X['exercise_mins'] / 60.0)
        X['screen_work_diff'] = X['screen_time'] - X['work_hours']
        
        # Target for Regression: productivity_score
        y_reg = df['productivity_score'].values if 'productivity_score' in df.columns else None
        
        # Target for Classification: Low (<50), Medium (50-75), High (>75)
        y_clf = None
        if y_reg is not None:
            y_clf = np.select(
                [y_reg < 50.0, (y_reg >= 50.0) & (y_reg <= 75.0), y_reg > 75.0],
                ['Low', 'Medium', 'High'],
                default='Medium'
            )
            
        return X, y_reg, y_clf, feature_cols + ['work_sleep_ratio', 'active_hours', 'screen_work_diff']

    @staticmethod
    def categorize_productivity_level(score):
        """Maps continuous score to discrete tier."""
        if score < 50.0:
            return 'Low'
        elif score <= 75.0:
            return 'Medium'
        else:
            return 'High'
