import json
import numpy as np
from simulariumio.medyan import MedyanConverter, MedyanData
from simulariumio import MetaData, DisplayData, ModelMetaData, InputFileData, TrajectoryConverter
from simulariumio.filters import TranslateFilter

def lambda_handler(event, context):
    box_size = 1000.0
    scale = 0.1

    example_data = MedyanData(
        meta_data=MetaData(
            box_size=np.array([box_size, box_size, box_size]),
            scale_factor=scale,
            trajectory_title="Some parameter set",
            model_meta_data=ModelMetaData(
                title="Some agent-based model",
                version="8.1",
                authors="A Modeler",
                description=(
                    "An agent-based model run with some parameter set"
                ),
                doi="10.1016/j.bpj.2016.02.002",
                source_code_url="https://github.com/allen-cell-animated/simulariumio",
                source_code_license_url="https://github.com/allen-cell-animated/simulariumio/blob/main/LICENSE",
                input_data_url="https://allencell.org/path/to/native/engine/input/files",
                raw_output_data_url="https://allencell.org/path/to/native/engine/output/files",
            ),
        ),
        snapshot_file=InputFileData(
            # TODO: also send in meta_data and display_data through event
            file_contents=event["file_contents"]
        ),
        filament_display_data={
            0: DisplayData(
                name="Filament",
                radius=5.0,
                color="#ff1493",
            ),
        },
        linker_display_data={
            0: DisplayData(
                name="LinkerA",
                radius=8.0,
                color="#ffffff",
            ),
            1: DisplayData(
                name="LinkerB",
                radius=8.0,
            ),
            2: DisplayData(
                name="LinkerC",
                radius=8.0,
            ),
        },
        motor_display_data={
            1: DisplayData(
                name="Motor",
                radius=2.0,
                color="#0080ff",
            ),
        },
        agents_with_endpoints=["Motor"]
    )
    
    c = MedyanConverter(example_data)
    translation_magnitude = -(box_size * scale) / 2
    filtered_data = c.filter_data([
        TranslateFilter(
            translation_per_type={},
            default_translation=translation_magnitude * np.ones(3)
        ),
    ])
    
    return TrajectoryConverter._read_trajectory_data(filtered_data)
