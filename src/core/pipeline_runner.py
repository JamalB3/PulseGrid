import time

from analytics.gold_processor import build_gold_layer
from core.logger import logger
from processing.silver_processor import build_silver_layer


def run_pipeline() -> None:
    """Run the Bronze-to-Silver-to-Gold processing pipeline."""

    start_time = time.perf_counter()

    logger.info("=" * 60)
    logger.info("PulseGrid data pipeline started.")
    logger.info("=" * 60)

    try:
        build_silver_layer()
        build_gold_layer()

    except FileNotFoundError as error:
        logger.error(
            "Pipeline failed because a required file was not found: %s",
            error,
        )
        raise

    except ValueError as error:
        logger.error(
            "Pipeline failed because invalid data or configuration was found: %s",
            error,
        )
        raise

    except Exception:
        logger.exception(
            "PulseGrid pipeline failed because of an unexpected error."
        )
        raise

    elapsed_seconds = time.perf_counter() - start_time

    logger.info(
        "PulseGrid pipeline completed successfully in %.2f seconds.",
        elapsed_seconds,
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()