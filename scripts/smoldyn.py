import numpy as np
from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio import UnitData, MetaData, DisplayData, DISPLAY_TYPE, ModelMetaData, InputFileData, TrajectoryConverter
from simulariumio.filters import TranslateFilter

def lambda_handler(event, context):
    box_size = 100.

    example_data = SmoldynData(
        meta_data=MetaData(
            box_size=np.array([box_size, box_size, box_size]),
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
        smoldyn_file=InputFileData(
            file_contents=event["file_contents"],
        ),
        display_data={
            "red(solution)": DisplayData(
                name="B",
                radius=1.0,
                display_type=DISPLAY_TYPE.OBJ,
                url="b.obj",
                color="#dfdacd",
            ),
            "green(solution)": DisplayData(
                name="A",
                radius=2.0,
                color="#0080ff",
            ),
        },
        time_units=UnitData("ns"),  # nanoseconds
        spatial_units=UnitData("nm"),  # nanometers
    )
    
    c = SmoldynConverter(example_data)
    translation_magnitude = -box_size / 2
    filtered_data = c.filter_data([
        TranslateFilter(
            translation_per_type={},
            default_translation=translation_magnitude * np.ones(3)
        ),
    ])
    
    return TrajectoryConverter._read_trajectory_data(filtered_data)
