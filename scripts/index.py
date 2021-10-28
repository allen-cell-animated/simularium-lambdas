from simulariumio.springsalad import SpringsaladConverter, SpringsaladData
from simulariumio import DisplayData, DISPLAY_TYPE, MetaData, ModelMetaData, InputFileData

def lambda_handler(event, context):
    example_data = SpringsaladData(
        sim_view_txt_file=InputFileData(
            file_contents=event["file_contents"],
        ),
        meta_data=MetaData(
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
        display_data={
            "GREEN": DisplayData(
                name="Ligand",
                radius=1.0,
                display_type=DISPLAY_TYPE.OBJ,
                url="b.obj",
                color="#dfdacd",
            ),
            "RED": DisplayData(
                name="Receptor Kinase#B site",
                radius=2.0,
                color="#0080ff",
            ),
            "GRAY": DisplayData(
                name="Receptor Kinase",
                radius=1.0,
                display_type=DISPLAY_TYPE.OBJ,
                url="b.obj",
                color="#dfdacd",
            ),
            "CYAN": DisplayData(
                name="Receptor Kinase#K site",
                radius=2.0,
                color="#0080ff",
            ),
            "BLUE": DisplayData(
                name="Substrate",
                radius=1.0,
                display_type=DISPLAY_TYPE.OBJ,
                url="b.obj",
                color="#dfdacd",
            ),
        },
        draw_bonds=True,
    )
    
    return SpringsaladConverter(example_data).to_JSON()
