"""
METROPULSE Sidebar Component
Renders the brand sidebar with platform telemetry, zero-fabrication badge, and dataset status.
"""
import streamlit as st


def render_sidebar():
    """Render unified enterprise sidebar."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #172338; margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 8px; background: linear-gradient(135deg, #3B82F6, #22D3EE); display: flex; align-items: center; justify-content: center; font-weight: 900; color: #080D17; font-size: 18px;">
                        M
                    </div>
                    <div>
                        <div style="font-size: 16px; font-weight: 800; color: #F8FAFC; letter-spacing: -0.02em;">METROPULSE</div>
                        <div style="font-size: 10px; font-weight: 600; color: #3B82F6; letter-spacing: 0.08em; text-transform: uppercase;">Mobility Intelligence</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Integrity & System Status Card
        st.markdown(
            """
            <div style="background: #0D1422; border: 1px solid #172338; border-radius: 8px; padding: 12px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 700; color: #94A3B8; text-transform: uppercase;">Integrity Guard</span>
                    <span class="badge badge-observed">ACTIVE</span>
                </div>
                <div style="font-size: 11px; color: #64748B; line-height: 1.4;">
                    Zero fabrication rule enforced. Real TfL NUMBAT data only. Missing values explicitly marked.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                Network Telemetry
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 6px;">
                <strong>Corpus:</strong> TfL NUMBAT 2023–2025
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 6px;">
                <strong>Scope:</strong> London Underground (LU)
            </div>
            <div style="font-size: 12px; color: #94A3B8; margin-bottom: 16px;">
                <strong>Engines:</strong> Parquet Cache &bull; PyArrow
            </div>
            <div style="padding-top: 12px; border-top: 1px solid #172338; font-size: 10px; color: #475569;">
                DataNova 2026 &bull; Problem DN-DS-01<br>
                London Underground Mobility Analytics
            </div>
            """,
            unsafe_allow_html=True,
        )

