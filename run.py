"""
METROPULSE — run.py
Entry point for running individual pipeline stages.

Usage:
    python run.py --stage inventory
    python run.py --stage preprocess
    python run.py --stage analytics
    python run.py --stage ml
    python run.py --stage all
"""
import argparse
import logging
import sys
import time
from pathlib import Path

# ─── Setup logging ────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "metropulse.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("metropulse")

# ─── Add project root to sys.path ────────────────────────────────────────────
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def stage_inventory():
    logger.info("Running INVENTORY stage...")
    from src.ingestion.inventory import build_inventory, save_inventory, print_summary
    inv = build_inventory()
    save_inventory(inv)
    print_summary(inv)


def stage_preprocess():
    logger.info("Running PREPROCESS stage...")
    from src.pipeline.run_pipeline import run_pipeline
    datasets = run_pipeline()
    logger.info("Preprocessing complete. %d datasets generated.", len(datasets))


def stage_analytics():
    logger.info("Running ANALYTICS stage...")
    from src.analytics.demand_analysis import run_demand_analysis
    from src.analytics.congestion import run_congestion_analysis
    from src.analytics.service_adequacy import run_service_adequacy
    from src.analytics.temporal_analysis import run_temporal_analysis
    run_demand_analysis()
    run_congestion_analysis()
    run_service_adequacy()
    run_temporal_analysis()
    logger.info("Analytics complete.")


def stage_ml():
    logger.info("Running ML stage...")
    from src.ml.feature_engineering import build_ml_features
    from src.ml.demand_model import run_demand_models
    from src.ml.congestion_model import run_congestion_model
    from src.ml.clustering import run_clustering
    build_ml_features()
    run_demand_models()
    run_congestion_model()
    run_clustering()
    logger.info("ML stage complete.")


def stage_geospatial():
    logger.info("Running GEOSPATIAL stage...")
    from src.geospatial.station_mapping import fetch_station_coordinates
    fetch_station_coordinates()
    logger.info("Geospatial stage complete.")


def stage_optimization():
    logger.info("Running OPTIMIZATION stage...")
    from src.optimization.network_builder import build_network
    from src.optimization.bottleneck_detection import detect_bottlenecks
    from src.optimization.service_optimizer import run_optimization_scenarios
    G = build_network()
    detect_bottlenecks(G)
    run_optimization_scenarios(G)
    logger.info("Optimization stage complete.")


def stage_bi_exports():
    logger.info("Running BI EXPORTS stage...")
    from src.analytics.demand_analysis import generate_bi_exports
    generate_bi_exports()
    logger.info("BI exports complete.")


def stage_quality_reports():
    logger.info("Running QUALITY REPORTS stage...")
    from src.quality_reports_generator import generate_quality_reports
    generate_quality_reports()
    logger.info("Quality reports complete.")


STAGES = {
    "inventory":        stage_inventory,
    "preprocess":       stage_preprocess,
    "analytics":        stage_analytics,
    "ml":               stage_ml,
    "geospatial":       stage_geospatial,
    "optimization":     stage_optimization,
    "bi_exports":       stage_bi_exports,
    "quality_reports":  stage_quality_reports,
}


def main():
    parser = argparse.ArgumentParser(
        description="METROPULSE — Urban Mobility Intelligence Platform"
    )
    parser.add_argument(
        "--stage",
        choices=list(STAGES.keys()) + ["all"],
        default="all",
        help="Pipeline stage to run (default: all)",
    )
    args = parser.parse_args()

    t0 = time.time()
    logger.info("=" * 70)
    logger.info("  METROPULSE — Urban Mobility Intelligence Platform")
    logger.info("  Stage: %s", args.stage)
    logger.info("=" * 70)

    if args.stage == "all":
        for name, fn in STAGES.items():
            logger.info("\n--- %s ---", name.upper())
            try:
                fn()
            except Exception as exc:
                logger.error("Stage '%s' failed: %s", name, exc, exc_info=True)
    else:
        try:
            STAGES[args.stage]()
        except Exception as exc:
            logger.error("Stage '%s' failed: %s", args.stage, exc, exc_info=True)
            sys.exit(1)

    elapsed = time.time() - t0
    logger.info("\n" + "=" * 70)
    logger.info("  Completed in %.1f seconds", elapsed)
    logger.info("=" * 70)


if __name__ == "__main__":
    main()

