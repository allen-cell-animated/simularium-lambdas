import numpy as np
from simulariumio.cytosim import CytosimConverter, CytosimData, CytosimObjectInfo
from simulariumio import MetaData, DisplayData, DISPLAY_TYPE, ModelMetaData, InputFileData

def lambda_handler(event, context):
    box_size = 2.

    example_data = CytosimData(
        meta_data=MetaData(
            box_size=np.array([box_size, box_size, box_size]),
            scale_factor=100.0,
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
        object_info={
            "fibers" : CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_contents=event["fibers"],
                ),
                display_data={
                    1 : DisplayData(
                        name="microtubule"
                    ),
                    2 : DisplayData(
                        name="actin"
                    )
                }
            ),
            "solids" : CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_contents=event["solids"],
                ),
                display_data={
                    1 : DisplayData(
                        name="aster",
                        radius=0.1
                    ),
                    2 : DisplayData(
                        name="vesicle",
                        radius=0.1
                    )
                }
            ),
            "singles" : CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_contents=event["singles"],
                ),
                display_data={
                    1 : DisplayData(
                        name="dynein",
                        radius=0.01,
                        display_type=DISPLAY_TYPE.PDB,
                        url="https://files.rcsb.org/download/3VKH.pdb",
                        color="#f4ac1a",
                    ),
                    2 : DisplayData(
                        name="kinesin",
                        radius=0.01,
                        display_type=DISPLAY_TYPE.PDB,
                        url="https://files.rcsb.org/download/3KIN.pdb",
                        color="#0080ff",
                    )
                }
            ),
            "couples" : CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_contents=event["couples"],
                ),
                display_data={
                    1 : DisplayData(
                        name="motor complex",
                        radius=0.02,
                        color="#bf95d4",
                    )
                },
                position_indices=[3, 4, 5]
            )
        },
    )
    
    return CytosimConverter(example_data).to_JSON()
