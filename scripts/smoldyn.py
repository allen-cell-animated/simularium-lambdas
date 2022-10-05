import numpy as np
from typing import Dict
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio.constants import DISPLAY_TYPE, DEFAULT_CAMERA_SETTINGS, DEFAULT_BOX_SIZE
from simulariumio import (
    UnitData,
    MetaData,
    DisplayData,
    ModelMetaData,
    InputFileData,
    JsonWriter,
    CameraData,
)


def lambda_handler(event, context):
    display_data = None
    camera_data = None
    box_size = None
    model_meta_data = None
    if "display_data" in event:
        display_data = dict()
        for index in event["display_data"]:
            agent_info = event["display_data"][index]
            for agent_name in agent_info:
                agent_data = agent_info[agent_name]
                display_data[agent_name] = DisplayData(
                    name=agent_data.get("name"),
                    radius=float(agent_data.get("radius", 1.0)),
                    display_type=agent_data.get("display_type", DISPLAY_TYPE.SPHERE),
                    url=agent_data.get("url"),
                    color=agent_data.get("color"),
                )
    if "meta_data" in event:
        metadata = event["meta_data"]
        if "box_size" in metadata:
            box_size = _unpack_position_vector(metadata["box_size"], DEFAULT_BOX_SIZE)

        if "camera_defaults" in metadata:
            camera_defaults = metadata["camera_defaults"]

            position = _unpack_position_vector(
                camera_defaults.get("position"),
                DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION
            )
            up_vector = _unpack_position_vector(
                camera_defaults.get("up_vector"),
                DEFAULT_CAMERA_SETTINGS.UP_VECTOR
            )
            look_at_position = _unpack_position_vector(
                camera_defaults.get("look_at_position"),
                DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION
            )
            fov_degrees = float(camera_defaults.get(
                "fov_degrees",
                DEFAULT_CAMERA_SETTINGS.FOV_DEGREES
            ))

            camera_data = CameraData(
                fov_degrees=fov_degrees,
                position=position,
                up_vector=up_vector,
                look_at_position=look_at_position,
            )

        if "model_meta_data" in metadata:
            model_data = metadata["model_meta_data"]
            model_meta_data = (
                ModelMetaData(
                    title=model_data.get("title"),
                    version=model_data.get("version", ""),
                    authors=model_data.get("author", ""),
                    description=model_data.get("description", ""),
                    doi=model_data.get("doi", ""),
                    source_code_url=model_data.get("source_code_url", ""),
                    source_code_license_url=model_data.get(
                        "source_code_license_url", ""
                    ),
                    input_data_url=model_data.get("input_data_url", ""),
                    raw_output_data_url=model_data.get("raw_output_data_url", ""),
                ),
            )

    spatial_units = None
    if "spatial_units" in event:
        # spatial units defaults to meters on UI
        name = event["spatial_units"]["name"] if "name" in event["spatial_units"] else "meter"

        if "magnitude" in event["spatial_units"]:
            spatial_units = UnitData(name, float(event["spatial_units"]["magnitude"]))
        else:
            spatial_units = UnitData(name)

    time_units = None
    if "time_units" in event:
         # time units default to seconds on UI
        name = event["time_units"]["name"] if "name" in event["time_units"] else "second"

        if "magnitude" in event["time_units"]:
            time_units = UnitData(name, float(event["time_units"]["magnitude"]))
        else:
            time_units = UnitData(name)

    data = SmoldynData(
        meta_data=MetaData(
            box_size=box_size,
            trajectory_title=event.get("trajectory_title", "No Title"),
            scale_factor=float(event.get("scale_factor", 1.0)),
            camera_defaults=camera_data,
            model_meta_data=model_meta_data,
        ),
        smoldyn_file=InputFileData(
            file_contents=event["file_contents"]["file_contents"],
        ),
        display_data=display_data,
        time_units=time_units,
        spatial_units=spatial_units,
    )

    return JsonWriter.format_trajectory_data(SmoldynConverter(data)._data)


def _unpack_position_vector(vector_dict: Dict[str, str], defaults: np.ndarray) -> np.ndarray:
    # if no vector information was given, go with the defaults
    if vector_dict == None:
        return defaults

    # use all positions given, but use defaults if any are missing
    return np.array(
        [
            float(vector_dict.get("0", defaults[0])),
            float(vector_dict.get("1", defaults[1])),
            float(vector_dict.get("2", defaults[2])),
        ]
    )
