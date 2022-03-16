import logging
import time

from just_bin_it.histograms.histogram1d import (
    TOF_1D_TYPE,
    Histogram1d,
    validate_hist_1d,
)
from just_bin_it.histograms.histogram2d import (
    TOF_2D_TYPE,
    Histogram2d,
    validate_hist_2d,
)
from just_bin_it.histograms.histogram2d_map import (
    MAP_TYPE,
    DetHistogram,
    validate_hist_2d_map,
)
from just_bin_it.histograms.histogram2d_roi import (
    ROI_TYPE,
    RoiHistogram,
    validate_hist_2d_roi,
)

SCHEMAS = {'hs00', 'hs01'}
DEFAULT_SCHEMA = "hs00"


def parse_config(configuration, current_time_ms=None):
    """
    Parses the configuration that defines the histograms.

    :param configuration: The dictionary containing the configuration.
    :param current_time_ms: The time to use for defining the start time (milliseconds).
    :return: tuple of start time, stop time and the list of histograms
    """
    start = configuration.get("start")
    stop = configuration.get("stop")

    schema = configuration.get("output_schema", DEFAULT_SCHEMA)
    if schema not in SCHEMAS:
        raise Exception(f"Unknown schema, be one of {SCHEMAS}")

    # Interval is configured in seconds but needs to be converted to milliseconds
    interval = (
        configuration["interval"] * 10 ** 3 if "interval" in configuration else None
    )

    if interval and (start or stop):
        raise Exception(
            "Cannot define 'interval' in combination with start and/or stop"
        )

    if interval and interval < 0:
        raise Exception("Interval cannot be negative")

    if interval:
        start = int(current_time_ms) if current_time_ms else int(time.time() * 1000)
        stop = start + interval

    hist_configs = []

    if "histograms" in configuration:
        for hist in configuration["histograms"]:
            if hist["type"] == TOF_1D_TYPE:
                if not validate_hist_1d(hist):
                    raise Exception("Could not parse 1d histogram config")
            elif hist["type"] == TOF_2D_TYPE:
                if not validate_hist_2d(hist):
                    raise Exception("Could not parse 2d histogram config")
            elif hist["type"] == MAP_TYPE:
                if not validate_hist_2d_map(hist):
                    raise Exception("Could not parse 2d map config")
            elif hist["type"] == ROI_TYPE:
                if not validate_hist_2d_roi(hist):
                    raise Exception("Could not parse 2d ROI config")
            else:
                raise Exception("Unexpected histogram type")
            hist_configs.append(hist)

    return start, stop, hist_configs, schema


class HistogramFactory:
    @staticmethod
    def generate(configuration):
        """
        Generate the histograms based on the supplied configuration.

        :param configuration: The configuration.
        :return: A list of created histograms.
        """
        histograms = []

        for config in configuration:
            histogram = None

            hist_type = config["type"]
            topic = config["topic"]
            num_bins = config["num_bins"] if "num_bins" in config else None
            tof_range = tuple(config["tof_range"]) if "tof_range" in config else None
            det_range = tuple(config["det_range"]) if "det_range" in config else None
            source = config["source"] if "source" in config else ""
            identifier = config["id"] if "id" in config else ""

            try:
                if hist_type == TOF_1D_TYPE:
                    histogram = Histogram1d(
                        topic, num_bins, tof_range, det_range, source, identifier
                    )
                elif hist_type == TOF_2D_TYPE:
                    histogram = Histogram2d(
                        topic, num_bins, tof_range, det_range, source, identifier
                    )
                elif hist_type == MAP_TYPE:
                    width = config["width"]
                    height = config["height"]
                    histogram = DetHistogram(
                        topic, det_range, width, height, source, identifier
                    )
                elif hist_type == ROI_TYPE:
                    width = config["width"]
                    left_edges = config["left_edges"]
                    histogram = RoiHistogram(
                        topic, left_edges, width, source, identifier
                    )
                else:
                    # Log but do nothing
                    logging.warning(
                        "Unrecognised histogram type: %s", hist_type
                    )  # pragma: no mutate
            except Exception as error:
                logging.warning(
                    "Could not create histogram. %s", error
                )  # pragma: no mutate

            if histogram is not None:
                histogram.identifier = identifier
                histograms.append(histogram)

        return histograms
