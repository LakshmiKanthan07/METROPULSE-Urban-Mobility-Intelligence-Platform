"""
METROPULSE Dashboard — Page 5: Machine Learning
"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.components.data_loader import (
    load, load_csv, format_number, PLOTLY_TEMPLATE
)

st.set_page_config(page_title="Machine Learning | METROPULSE", page_icon="🤖", layout="wide")
st.markdown("""<style>.stApp{background:#0a0f1e;color:#f1f5f9;}[data-testid="stSidebar"]{background:#111827!important;}
[data-testid="metric-container"]{background:#1a2235;border:1px solid #1e3a5f;border-radius:12px;padding:1rem!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#8b5cf6!important;font-size:1.8rem!important;font-weight:700;}
h1,h2,h3{color:#f1f5f9!important;}</style>""", unsafe_allow_html=True)

st.markdown("# 🤖 Machine Learning & Predictive Analytics")
st.markdown("**Demand profile estimation, congestion classification, and unsupervised station topology clustering**")

# ─── Load ML data ─────────────────────────────────────────────────────────────
demand_results = load_csv("ml_demand_model_results")
feat_imp       = load_csv("ml_feature_importance")
clusters       = load_csv("ml_station_clusters")
cluster_prof   = load_csv("ml_cluster_profiles")
cong_pred      = load_csv("ml_congestion_predictions")
cong_fi        = load_csv("ml_congestion_feature_importance")

tabs = st.tabs([
    "📈 Demand Profile Estimation",
    "🚦 Congestion Classification",
    "🧩 Station Clustering",
    "🔍 Feature Explainability"
])

# ── TAB 1: Demand Profile Estimation ──────────────────────────────────────────
with tabs[0]:
    st.markdown("### Model Benchmark Comparison (Leave-One-Year-Out Validation)")
    st.caption("Validation strategy strictly blocks test years to evaluate generalized demand estimation on typical-day profiles.")

    if not demand_results.empty:
        summary_models = (
            demand_results.groupby("model")[["mae", "rmse", "r2"]]
            .mean().reset_index()
            .sort_values("mae", ascending=True)
        )
        
        c1, c2, c3 = st.columns(3)
        best_model = summary_models.iloc[0]
        c1.metric("Top Model", f"{best_model['model']}")
        c2.metric("Mean MAE", f"{best_model['mae']:,.0f} pax")
        c3.metric("Validation R²", f"{best_model['r2']:.3f}")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            fig_mae = px.bar(
                summary_models, x="model", y="mae",
                color="model",
                labels={"mae": "Mean Absolute Error (Pax)", "model": "Model Architecture"},
                title="Cross-Validation MAE Across Candidate Models"
            )
            fig_mae.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=350)
            st.plotly_chart(fig_mae, use_container_width=True)

        with col_m2:
            fig_r2 = px.bar(
                summary_models, x="model", y="r2",
                color="model",
                labels={"r2": "R² Variance Explained", "model": "Model Architecture"},
                title="Generalization R² (Leave-One-Year-Out)"
            )
            fig_r2.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=350)
            st.plotly_chart(fig_r2, use_container_width=True)

        st.markdown("#### Detailed Fold Performance Table")
        st.dataframe(demand_results, use_container_width=True)
    else:
        st.info("Demand model results not yet generated. Run `python run.py --stage ml`.")

# ── TAB 2: Congestion Classification ──────────────────────────────────────────
with tabs[1]:
    st.markdown("### Supervised Congestion Risk Classification")
    if not cong_pred.empty and "congestion_class" in cong_pred.columns and "predicted_class" in cong_pred.columns:
        from sklearn.metrics import confusion_matrix
        labels = ["Low", "Moderate", "High", "Critical"]
        y_true = [c for c in cong_pred["congestion_class"] if c in labels]
        y_pred = [c for c in cong_pred["predicted_class"] if c in labels]
        
        if y_true and y_pred:
            cm = confusion_matrix(y_true, y_pred, labels=labels)
            cm_df = pd.DataFrame(cm, index=labels, columns=labels)
            
            c_cm1, c_cm2 = st.columns(2)
            with c_cm1:
                fig_cm = px.imshow(
                    cm_df, text_auto=True,
                    color_continuous_scale="Blues",
                    labels=dict(x="Predicted Class", y="Actual Class", color="Count"),
                    title="Confusion Matrix: Gradient Boosting Classifier"
                )
                fig_cm.update_layout(**PLOTLY_TEMPLATE["layout"], height=400)
                st.plotly_chart(fig_cm, use_container_width=True)

            with c_cm2:
                st.markdown("#### Sample Model Predictions on Underground Links")
                disp_cols = ["link", "line", "am_peak", "freq_am_peak", "congestion_class", "predicted_class"]
                disp_cols = [c for c in disp_cols if c in cong_pred.columns]
                st.dataframe(cong_pred[disp_cols].head(15), use_container_width=True, height=350)
    else:
        st.info("Congestion predictions not available yet.")

# ── TAB 3: Station Clustering ─────────────────────────────────────────────────
with tabs[2]:
    st.markdown("### Unsupervised Topological & Demand Clustering")
    if not clusters.empty:
        c_k1, c_k2 = st.columns([1, 2])
        with c_k1:
            st.markdown("#### Cluster Population")
            c_counts = clusters["cluster_label"].value_counts().reset_index()
            c_counts.columns = ["Cluster", "Station Count"]
            fig_cl_pie = px.pie(
                c_counts, values="Station Count", names="Cluster",
                hole=0.4, color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_cl_pie.update_layout(**PLOTLY_TEMPLATE["layout"], height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_cl_pie, use_container_width=True)

        with c_k2:
            st.markdown("#### Cluster Profile Characteristics")
            if not cluster_prof.empty:
                st.dataframe(cluster_prof.round(2), use_container_width=True, height=320)

        st.markdown("#### Search Station Clusters")
        search_q = st.text_input("Filter by Station Name or ASC", "")
        if search_q:
            sub = clusters[clusters["station"].astype(str).str.contains(search_q, case=False, na=False) |
                           clusters["asc"].astype(str).str.contains(search_q, case=False, na=False)]
        else:
            sub = clusters.head(30)
        st.dataframe(sub, use_container_width=True, height=300)
    else:
        st.info("Cluster data not available yet.")

# ── TAB 4: Explainability ─────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### Feature Importance & Attribution")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("#### Demand Model: Feature Importance")
        if not feat_imp.empty:
            fig_fi = px.bar(
                feat_imp.sort_values("importance", ascending=True),
                x="importance", y="feature",
                orientation="h",
                color="importance",
                color_continuous_scale="Purples",
                labels={"importance": "Gini Importance", "feature": "Engineered Feature"}
            )
            fig_fi.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=450)
            st.plotly_chart(fig_fi, use_container_width=True)
        else:
            st.info("Feature importance data not found.")

    with col_f2:
        st.markdown("#### Congestion Model: Feature Importance")
        if not cong_fi.empty:
            fig_cfi = px.bar(
                cong_fi.sort_values("importance", ascending=True),
                x="importance", y="feature",
                orientation="h",
                color="importance",
                color_continuous_scale="Reds",
                labels={"importance": "Importance", "feature": "Feature"}
            )
            fig_cfi.update_layout(**PLOTLY_TEMPLATE["layout"], showlegend=False, height=450)
            st.plotly_chart(fig_cfi, use_container_width=True)
        else:
            st.info("Congestion feature importance not found.")

