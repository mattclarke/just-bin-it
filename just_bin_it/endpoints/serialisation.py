import streaming_data_types.histogram_hs00 as hs00
import streaming_data_types.eventdata_ev42 as ev42
from streaming_data_types.eventdata_ev42 import EventData
from just_bin_it.exceptions import JustBinItException


def get_schema(buf):
    """
    Extract the schema code embedded in the buffer

    :param buf: The raw buffer of the FlatBuffers message.
    :return: The schema name
    """
    return buf[4:8].decode("utf-8")


def deserialise_hs00(buf):
    """
    Convert flatbuffer into a histogram.

    :param buf:
    :return: dict of histogram information
    """
    try:
        return hs00.deserialise_hs00(buf)
    except Exception as error:
        raise JustBinItException(f"Could not deserialise hs00 buffer: {error}")


def serialise_hs00(histogrammer, timestamp: int = 0, info_message: str = ""):
    """
    Serialise a histogram as an hs00 FlatBuffers message.

    :param histogrammer: The histogrammer containing the histogram to serialise.
    :param timestamp: The timestamp to assign to the histogram.
    :param info_message: Information to write to the 'info' field.
    :return: The raw buffer of the FlatBuffers message.
    """

    dim_metadata = [
        {"bin_boundaries": histogrammer.x_edges, "length": histogrammer.shape[0]}
    ]

    if hasattr(histogrammer, "y_edges"):
        dim_metadata.append(
            {"bin_boundaries": histogrammer.y_edges, "length": histogrammer.shape[1]}
        )

    data = {
        "source": "just-bin-it",
        "timestamp": timestamp,
        "current_shape": histogrammer.shape,
        "dim_metadata": dim_metadata,
        "data": histogrammer.data,
        "info": info_message,
    }

    return hs00.serialise_hs00(data)


def deserialise_ev42(buf) -> EventData:
    """
    Deserialise an ev42 FlatBuffers message.

    :param buf: The raw buffer of the FlatBuffers message.
    :return: A tuple of the deserialised values.
    """
    try:
        return ev42.deserialise_ev42(buf)
    except Exception as error:
        raise JustBinItException(f"Could not deserialise ev42 buffer: {error}")


def serialise_ev42(source_name, message_id, pulse_time, tofs, det_ids):
    """
    Serialise into an ev42 FlatBuffers message.

    :param source_name: The source name.
    :param message_id: The message ID.
    :param pulse_time: The pulse_time.
    :param tofs: The time-of-flights for the events.
    :param det_ids: The detector IDs for the events.
    :return: The raw buffer of the FlatBuffers message.
    """
    return ev42.serialise_ev42(source_name, message_id, pulse_time, tofs, det_ids)
