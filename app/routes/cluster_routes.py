from flask import Blueprint, render_template, session
from app.routes.main_routes import login_required
from app.models.daily_record_model import DailyRecordModel
from app.ml.clustering_model import BehaviorClusterer, CLUSTER_LABELS

cluster_bp = Blueprint('clustering', __name__, url_prefix='/clustering')

@cluster_bp.route('/')
@login_required
def index():
    user_id = session['user_id']
    records = DailyRecordModel.get_all_records_for_user(user_id)
    
    # Run K-Means and PCA
    clusterer = BehaviorClusterer(n_clusters=4)
    clustering_result = clusterer.fit_predict(records) if records else None
    
    return render_template(
        'clustering/index.html',
        clustering_result=clustering_result,
        cluster_labels=CLUSTER_LABELS,
        total_records=len(records) if records else 0
    )
