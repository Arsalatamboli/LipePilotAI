import os
import matplotlib
matplotlib.use('Agg') # Non-interactive backend for server generation
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from config import Config
from app.ml.data_processor import DataProcessor

class ModelEvaluator:
    @staticmethod
    def evaluate_models(records):
        """Evaluates Regression & Classification models and outputs evaluation metrics + plots."""
        df = DataProcessor.records_to_dataframe(records)
        X, y_reg, y_clf, _ = DataProcessor.extract_features(df)
        
        if X is None or len(X) < 10:
            return {
                "status": "warning",
                "message": "At least 10 historical records are required to compute train/test evaluation metrics."
            }

        # Train/Test Split
        X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
            X, y_reg, y_clf, test_size=0.25, random_state=42
        )
        
        # 1. Regression Evaluation (RandomForestRegressor)
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        regressor = RandomForestRegressor(n_estimators=100, random_state=42)
        regressor.fit(X_train_scaled, y_reg_train)
        y_reg_pred = regressor.predict(X_test_scaled)
        
        mse = mean_squared_error(y_reg_test, y_reg_pred)
        r2 = r2_score(y_reg_test, y_reg_pred)
        
        # 2. Classification Evaluation (RandomForestClassifier)
        classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        classifier.fit(X_train_scaled, y_clf_train)
        y_clf_pred = classifier.predict(X_test_scaled)
        
        acc = accuracy_score(y_clf_test, y_clf_pred)
        prec = precision_score(y_clf_test, y_clf_pred, average='weighted', zero_division=0)
        rec = recall_score(y_clf_test, y_clf_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_clf_test, y_clf_pred, average='weighted', zero_division=0)
        
        labels = ['Low', 'Medium', 'High']
        cm = confusion_matrix(y_clf_test, y_clf_pred, labels=labels)
        
        # 3. Generate Confusion Matrix Plot in Light Mode Style
        os.makedirs(Config.PLOT_OUTPUT_DIR, exist_ok=True)
        cm_plot_path = os.path.join(Config.PLOT_OUTPUT_DIR, 'confusion_matrix.png')
        
        plt.figure(figsize=(6, 5), facecolor='#F8FAFC')
        ax = plt.subplot()
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels,
                    cbar=False, ax=ax, linewidths=1, linecolor='#E2E8F0')
        
        ax.set_title('Productivity Level Confusion Matrix', fontsize=12, fontweight='bold', color='#0F172A', pad=12)
        ax.set_xlabel('Predicted Label', fontsize=10, fontweight='bold', color='#475569')
        ax.set_ylabel('True Label', fontsize=10, fontweight='bold', color='#475569')
        ax.tick_params(colors='#0F172A')
        plt.tight_layout()
        plt.savefig(cm_plot_path, dpi=150, facecolor='#F8FAFC')
        plt.close()

        return {
            "status": "success",
            "regression_metrics": {
                "mse": round(float(mse), 4),
                "r2_score": round(float(r2), 4)
            },
            "classification_metrics": {
                "accuracy": round(float(acc), 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1_score": round(float(f1), 4)
            },
            "confusion_matrix": cm.tolist(),
            "confusion_matrix_plot": "/static/images/plots/confusion_matrix.png"
        }
