from pathlib import Path
from core.logger import logger
import pandas as pd
from core.config import (

    DEVICE_HEALTH_FILE,

    DEVICE_OFFLINE_MINUTES,

    GOLD_DIRECTORY,

    HOURLY_METRICS_FILE,

    LOCATION_METRICS_FILE,

    SILVER_FILE,

    TEMPERATURE_ALERT_THRESHOLD,

)


PROJECT_ROOT = Path(__file__).resolve().parents[2]



def load_silver_data() -> pd.DataFrame:
    """Load validated telemetry from the Silver layer."""

    if not SILVER_FILE.exists():
        raise FileNotFoundError(
            f"Silver file not found: {SILVER_FILE}"
        )

    dataframe = pd.read_parquet(SILVER_FILE)

    dataframe["timestamp"] = pd.to_datetime(
        dataframe["timestamp"],
        utc=True,
    )

    return dataframe


def build_location_metrics(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate telemetry metrics for each building room."""

    location_metrics = (
        dataframe.groupby(
            [
                "building_id",
                "building",
                "floor",
                "room_id",
                "room",
                "room_type",
            ],
            as_index=False,
        )
        .agg(
            total_events=("event_id", "count"),
            unique_devices=("device_id", "nunique"),
            average_temperature=("temperature", "mean"),
            maximum_temperature=("temperature", "max"),
            average_humidity=("humidity", "mean"),
            total_energy_usage=("energy_usage", "sum"),
            average_energy_usage=("energy_usage", "mean"),
            average_air_quality=("air_quality", "mean"),
            average_occupancy=("occupancy", "mean"),
            maximum_occupancy=("occupancy", "max"),
        )
    )

    decimal_columns = [
        "average_temperature",
        "maximum_temperature",
        "average_humidity",
        "total_energy_usage",
        "average_energy_usage",
        "average_air_quality",
        "average_occupancy",
    ]

    location_metrics[decimal_columns] = (
        location_metrics[decimal_columns].round(2)
    )

    return location_metrics

def build_hourly_metrics(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate telemetry by location and hour."""

    hourly_dataframe = dataframe.copy()

    hourly_dataframe["event_hour"] = (
        hourly_dataframe["timestamp"].dt.floor("h")
    )

    hourly_metrics = (
        hourly_dataframe.groupby(
            [
                "event_hour",
                "building_id",
                "building",
                "floor",
                "room_id",
                "room",
                "room_type",
            ],
            as_index=False,
        )
        .agg(
            event_count=("event_id", "count"),
            average_temperature=("temperature", "mean"),
            average_humidity=("humidity", "mean"),
            total_energy_usage=("energy_usage", "sum"),
            average_air_quality=("air_quality", "mean"),
            average_occupancy=("occupancy", "mean"),
        )
    )

    numeric_columns = [
        "average_temperature",
        "average_humidity",
        "total_energy_usage",
        "average_air_quality",
        "average_occupancy",
    ]

    hourly_metrics[numeric_columns] = (
        hourly_metrics[numeric_columns].round(2)
    )

    return hourly_metrics


def build_device_health(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """Create device-level operational health metrics."""

    latest_timestamp = dataframe["timestamp"].max()

    device_health = (
        dataframe.groupby(
            [
                "device_id",
                "building_id",
                "building",
                "floor",
                "room_id",
                "room",
                "room_type",
                ],
            as_index=False,
        )
        .agg(
            total_events=("event_id", "count"),
            last_event_timestamp=("timestamp", "max"),
            average_temperature=("temperature", "mean"),
            maximum_temperature=("temperature", "max"),
            average_energy_usage=("energy_usage", "mean"),
        )
    )

    device_health["minutes_since_last_event"] = (
        (
            latest_timestamp
            - device_health["last_event_timestamp"]
        )
        .dt.total_seconds()
        .div(60)
        .round(2)
    )

    device_health["temperature_alert"] = (
        device_health["maximum_temperature"]
        > TEMPERATURE_ALERT_THRESHOLD
    )

    device_health["device_status"] = (
        device_health["minutes_since_last_event"]
        .apply(
            lambda minutes: (
                "offline"
                if minutes > DEVICE_OFFLINE_MINUTES
                else "online"
            )
        )
    )

    decimal_columns = [
        "average_temperature",
        "maximum_temperature",
        "average_energy_usage",
    ]

    device_health[decimal_columns] = (
        device_health[decimal_columns].round(2)
    )

    return device_health


def build_gold_layer() -> None:
    """Create analytics-ready Gold tables."""

    logger.info("Starting Gold-layer processing.")
    dataframe = load_silver_data()

    GOLD_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    location_metrics = build_location_metrics(dataframe)
    hourly_metrics = build_hourly_metrics(dataframe)
    device_health = build_device_health(dataframe)

    location_metrics.to_parquet(
        LOCATION_METRICS_FILE,
        index=False,
    )

    hourly_metrics.to_parquet(
        HOURLY_METRICS_FILE,
        index=False,
    )

    device_health.to_parquet(
        DEVICE_HEALTH_FILE,
        index=False,
    )

    logger.info("Gold processing completed successfully.")
    logger.info("Room metrics written: %d rows", len(location_metrics))
    logger.info("Hourly metrics written: %d rows", len(hourly_metrics))
    logger.info("Device-health metrics written: %d rows", len(device_health))
    logger.info("Gold output directory: %s", GOLD_DIRECTORY)


if __name__ == "__main__":
    build_gold_layer()