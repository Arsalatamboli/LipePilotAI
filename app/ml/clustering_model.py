import os
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from config import Config
from app.ml.data_processor import DataProcessor

CLUSTER_LABELS = {
    0: {"name": "Optimal Balance", "badge": "badge-success", "color": "#10B981", "desc": "Great balance between work, sleep, and exercise with low stress."},
    1: {"name": "High Work / Burnout Risk", "badge": "badge-danger", "color": "#EF4444", "desc": "High workload and stress paired with insufficient sleep."},
    2: {"name": "Sedentary / High Screen Time", "badge": "badge-warning", "color": "#F59E0B", "desc": "Elevated screen time and lower physical activity levels."},
    3: {"name": "Low Activity / Recovery Mode", "badge": "badge-info", "color": "#0EA5E9", "desc": "Lower overall activity and work output, focus on rest."}
}

class BehaviorClusterer:
    def __init__(self, n_clusters=4):
        self.n_clusters = n_clusters
        self.model_path = os.path.join(Config.ML_MODEL_DIR, 'kmeans_clusterer.joblib')
        self.pca_path = os.path.join(Config.ML_MODEL_DIR, 'pca_reducer.joblib')
        self.scaler_path = os.path.join(Config.ML_MODEL_DIR, 'cluster_scaler.joblib')
        self.kmeans = None
        self.pca = None
        self.scaler = None
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(Config.ML_MODEL_DIR, exist_ok=True)

    def fit_predict(self, records):
        """Performs K-Means clustering and PCA 2D reduction on daily records."""
        df = DataProcessor.records_to_dataframe(records)
        if df.empty or len(df) < 4:
            return None

        features = ['sleep_hours', 'work_hours', 'screen_time', 'exercise_mins', 'stress_level']
        X = df[features].copy()
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit K-Means
        actual_k = min(self.n_clusters, len(df))
        self.kmeans = KMeans(n_clusters=actual_k, random_state=42, n_init=10)
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        # Fit PCA (2D)
        self.pca = PCA(n_components=2, random_state=42)
        pca_coords = self.pca.fit_transform(X_scaled)
        
        # Save fitted transformers
        joblib.dump(self.kmeans, self.model_path)
        joblib.dump(self.pca, self.pca_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Prepare output list of dictionaries for frontend visualization
        result_df = df.copy()
        result_df['cluster'] = cluster_labels
        result_df['pca_x'] = pca_coords[:, 0]
        result_df['pca_y'] = pca_coords[:, 1]
        
        # Add cluster metadata
        cluster_points = []
        for idx, row in result_df.iterrows():
            c_id = int(row['cluster'])
            meta = CLUSTER_LABELS.get(c_id, {"name": f"Cluster {c_id}", "badge": "badge-secondary", "color": "#64748B", "desc": ""})
            cluster_points.append({
                "record_date": str(row['record_date']),
                "cluster_id": c_id,
                "cluster_name": meta['name'],
                "color": meta['color'],
                "pca_x": float(row['pca_x']),
                "pca_y": float(row['pca_y']),
                "sleep_hours": float(row['sleep_hours']),
                "work_hours": float(row['work_hours']),
                "screen_time": float(row['screen_time']),
                "exercise_mins": int(row['exercise_mins']),
                "stress_level": int(row['stress_level'])
            })
            
        explained_variance = [float(ev) for ev in self.pca.explained_variance_ratio_]
        
        return {
            "cluster_points": cluster_points,
            "explained_variance": explained_variance,
            "total_variance_explained": float(sum(explained_variance) * 100)
        }

    def predict_single(self, sleep_hours, work_hours, screen_time, exercise_mins, stress_level):
        """Assigns a single day's metrics to a cluster persona."""
        if self.kmeans is None or self.scaler is None:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.kmeans = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                if os.path.exists(self.pca_path):
                    self.pca = joblib.load(self.pca_path)
            else:
                return CLUSTER_LABELS[0]

        feature_names = ['sleep_hours', 'work_hours', 'screen_time', 'exercise_mins', 'stress_level']
        input_data = pd.DataFrame([[sleep_hours, work_hours, screen_time, exercise_mins, stress_level]], columns=feature_names)
        input_scaled = self.scaler.transform(input_data)
        cluster_id = int(self.kmeans.predict(input_scaled)[0])
        
        meta = CLUSTER_LABELS.get(cluster_id, {"name": f"Cluster {cluster_id}", "badge": "badge-secondary", "color": "#64748B", "desc": ""})
        meta['cluster_id'] = cluster_id
        return meta
