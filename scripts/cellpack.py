import json
import numpy as np

from scipy.spatial.transform import Rotation as R
from simulariumio import TrajectoryConverter, TrajectoryData, AgentData, UnitData, MetaData, CameraData

print('Loading function')


class ConvertToSimularium():

    def __init__(self, total_steps=1):

        self.recipe_name = ""
        self.debug = True
        # simularium parameters
        self.total_steps = total_steps
        self.timestep = 1
        self.box_size = [10, 10, 10]
        self.n_agents = [0 for x in range(total_steps)]
        self.points_per_fiber = 0
        self.type_names = [[] for x in range(total_steps)]
        self.positions = [[] for x in range(total_steps)]
        self.rotations = [[] for x in range(total_steps)]
        self.viz_types = [[] for x in range(total_steps)]
        self.unique_ids = [[] for x in range(total_steps)]
        self.radii = [[] for x in range(total_steps)]
        self.n_subpoints = [[] for x in range(total_steps)]
        self.subpoints = [[] for x in range(total_steps)]

        # stored data for processesing
        self.fiber_points = [[] for x in range(total_steps)]
        self.max_fiber_length = 0
        # defaults for missing data
        self.default_radius = 5

    def get_bounding_box(self, recipe_data):
        options = recipe_data["options"]
        bb = options["boundingBox"]
        x_size = bb[1][0] - bb[0][0]
        y_size = bb[1][1] - bb[0][1]
        z_size = bb[1][2] - bb[0][2]
        self.box_size = [x_size, y_size, z_size]

    def get_ingredient_data(self, main_container, ingredient, version):
        data = None
        if version == 0:
            if self.debug:
                print("version 0")
            ingredient_name = ingredient
            ingredients = main_container["ingredients"]
            data = ingredients[ingredient]
        elif version == 1:
            if self.debug:
                print("version 1")
            ingredient_name = ingredient["name"]
            compartment = main_container[ingredient["compartment"]]
            position = ingredient["position"]
            try:
                compartment[position]
                data = compartment[ingredient["position"]
                                   ]["ingredients"][ingredient_name]
            except Exception as e:
                # Ingredient in recipe wasn't packed
                print(e, position, ingredient_name)
        return (ingredient_name, data)

    def get_euler_from_matrix(self, data_in):
        rotation_matrix = [data_in[0][0:3], data_in[1][0:3], data_in[2][0:3]]
        return R.from_matrix(rotation_matrix).as_euler('xyz', degrees=True)

    def get_euler_from_quat(self, data_in):
        return R.from_quat(data_in).as_euler('xyz', degrees=True)

    def is_matrix(self, data_in):
        if isinstance(data_in[0], list):
            return True
        else:
            return False

    def get_euler(self, data_in):
        if self.is_matrix(data_in):
            return self.get_euler_from_matrix(data_in)
        else:
            return self.get_euler_from_quat(data_in)

    def loop_through_ingredients(self, results_data_in, time_step_index):
        if "cytoplasme" in results_data_in:
            main_container = results_data_in["cytoplasme"]
            version = 0
        elif "compartments" in results_data_in:
            main_container = results_data_in["compartments"]
            version = 1
        id = 0
        for i in range(len(self.unique_ingredient_names)):
            ingredient = self.unique_ingredient_names[i]
            (ingredient_name, data) = self.get_ingredient_data(
                main_container, ingredient, version)
            if data is None:
                continue
            elif len(data["results"]) > 0:
                for j in range(len(data["results"])):
                    self.positions[time_step_index].append(
                        data["results"][j][0])
                    rotation = self.get_euler(data["results"][j][1])
                    self.rotations[time_step_index].append(rotation)
                    self.viz_types[time_step_index].append(1000)
                    self.n_agents[time_step_index] = self.n_agents[time_step_index] + 1
                    self.type_names[time_step_index].append(ingredient_name)
                    self.unique_ids[time_step_index].append(id)
                    if "radii" in data:
                        self.radii[time_step_index].append(
                            data["radii"][0]["radii"][0])
                    elif "encapsulatingRadius" in data:
                        self.radii[time_step_index].append(
                            data["encapsulatingRadius"])
                    else:
                        self.radii[time_step_index].append(self.default_radius)

                    self.n_subpoints[time_step_index].append(0)
                    id = id + 1

            elif data["nbCurve"] > 0:
                for i in range(data["nbCurve"]):
                    curve = "curve" + str(i)
                    self.positions[time_step_index].append([0, 0, 0])
                    self.rotations[time_step_index].append([0, 0, 0])
                    self.viz_types[time_step_index].append(1001)
                    self.n_agents[time_step_index] = self.n_agents[time_step_index] + 1
                    self.type_names[time_step_index].append(ingredient_name)
                    self.unique_ids[time_step_index].append(id)
                    if "encapsulatingRadius" in data:
                        self.radii[time_step_index].append(
                            data["encapsulatingRadius"])
                    else:
                        self.radii[time_step_index].append(5)
                    self.n_subpoints[time_step_index].append(len(data[curve]))
                    self.fiber_points[time_step_index].append(data[curve])
                    if len(data[curve]) > self.max_fiber_length:
                        if self.debug:
                            print("found longer fiber, new max",
                                  len(data[curve]))
                        self.max_fiber_length = len(data[curve])
                    id = id + 1

    def get_positions_per_ingredient(self, results_data_in, time_step_index):
        if results_data_in["recipe"]["name"] != self.recipe_name:
            raise Exception("Recipe name in results file doesn't match recipe file",
                            "result:", results_data_in["recipe"]["name"], "recipe", self.recipe_name)
        self.loop_through_ingredients(results_data_in, time_step_index)

    def fill_in_empty_fiber_data(self, time_step_index):
        blank_value = [[0, 0, 0] for x in range(self.max_fiber_length)]
        for viz_type in self.viz_types[time_step_index]:
            if viz_type == 1000:
                self.subpoints[time_step_index].append(blank_value)
            elif viz_type == 1001:
                if self.debug:
                    print("adding control points")
                control_points = self.fiber_points[time_step_index].pop(0)
                while len(control_points) < self.max_fiber_length:
                    control_points.append([0, 0, 0])
                self.subpoints[time_step_index].append(control_points)

    def get_all_ingredient_names(self, recipe_in):
        self.recipe_name = recipe_in["recipe"]["name"]
        if "cytoplasme" in recipe_in:
            container = recipe_in["cytoplasme"]
            ingredients = container["ingredients"]
            self.unique_ingredient_names = list(ingredients)
        elif "compartments" in recipe_in:
            ingredients = []
            for compartment in recipe_in["compartments"]:
                current_compartment = recipe_in["compartments"][compartment]
                if "surface" in current_compartment:
                    ingredients = ingredients + [{
                        "name": ingredient,
                        "compartment": compartment,
                        "position": "surface"
                    } for ingredient in current_compartment["surface"]["ingredients"]]
                if "interior" in current_compartment:

                    ingredients = ingredients + ingredients + [{
                        "name": ingredient,
                        "compartment": compartment,
                        "position": "interior"
                    } for ingredient in current_compartment["interior"]["ingredients"]]
            self.unique_ingredient_names = ingredients


def lambda_handler(event, context):
    time_point_index = 0

    converter = ConvertToSimularium()
    recipe_data = event["input_recipe"]
    packing_data = event["packing_result"]

    converter.get_all_ingredient_names(recipe_data)
    converter.get_bounding_box(recipe_data)
    box_size = converter.box_size
    converter.get_positions_per_ingredient(packing_data, time_point_index)
    converter.fill_in_empty_fiber_data(time_point_index)
    print("stored all data needed")
    meta_data = MetaData(
        box_size=np.array(box_size),
        camera_defaults=CameraData(
            position=np.array([10.0, 0.0, -box_size[2]]),
            look_at_position=np.array([10.0, 0.0, 0.0]),
            fov_degrees=60.0,
        ),
    )
    agent_data = AgentData(
        times=converter.timestep *
        np.array(list(range(converter.total_steps))),
        n_agents=np.array(converter.n_agents),
        viz_types=np.array(converter.viz_types),
        unique_ids=np.array(converter.unique_ids),
        types=np.array(converter.type_names),
        positions=np.array(converter.positions),
        rotations=np.array(converter.rotations),
        radii=np.array(converter.radii),
        subpoints=np.array(converter.subpoints),
        n_subpoints=np.array(converter.n_subpoints),
    )
    converted_data = TrajectoryData(
        meta_data=meta_data,
        agent_data=agent_data,
        # time_units=UnitData("ns"),
        # spatial_units=UnitData("nm"),
    )
    print("converted data")
    return TrajectoryConverter(converted_data).to_JSON()
