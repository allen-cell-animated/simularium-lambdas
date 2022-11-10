from simulariumio.smoldyn import SmoldynConverter, SmoldynData
from simulariumio import JsonWriter


def lambda_handler(event, context):
    smoldyn_data = SmoldynData.from_dict(event)
    return JsonWriter.format_trajectory_data(SmoldynConverter(smoldyn_data)._data)
