import numpy as np
from typing import Dict
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio import (
    UnitData,
    MetaData,
    DisplayData,
    DISPLAY_TYPE,
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
            box_size = _unpack_position_vector(metadata["box_size"])

        if "camera_defaults" in metadata:
            camera_defaults = metadata["camera_defaults"]
            position = None
            up_vector = None
            look_at_position = None
            fov_degrees = None
            if "position" in camera_defaults:
                position = _unpack_position_vector(camera_defaults["position"])

            if "up_vector" in camera_defaults:
                up_vector = _unpack_position_vector(camera_defaults["up_vector"])

            if "look_at_position" in camera_defaults:
                look_at_position = _unpack_position_vector(camera_defaults["look_at_position"])

            if "fov_degrees" in camera_defaults:
                fov_degrees = float(camera_defaults["fov_degrees"])

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


def _unpack_position_vector(vector_dict: Dict[str, str]) -> np.ndarray:
    if len(vector_dict) != 3:
        # we expect x, y, z coordinates
        return None
    return np.array(list(map(float, list(vector_dict.values()))))
