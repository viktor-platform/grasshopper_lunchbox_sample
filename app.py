from io import BytesIO
import json

from viktor import ViktorController,File
from viktor.parametrization import ViktorParametrization
from viktor.parametrization import NumberField,MultiFileField,BooleanField
from viktor.parametrization import Text
from viktor.parametrization import Image
from viktor.external.generic import GenericAnalysis
from viktor.views import GeometryView,DataGroup,DataItem,GeometryAndDataResult,GeometryAndDataView
from viktor.views import GeometryResult


class Parametrization(ViktorParametrization):
    img = Image(path="blubgtruss.png")
    intro = Text(
        "# SpaceTruess app 🏗️ \n This app parametrically generates and visualizes a 3D model of a 3d space truss structure system using Rhinoceros 🦏, Grasshopper 🦗 & Lunchbox Plugin📦.  \n\n Please fill in the following parameters:")
    text2 = Text("## Step 1 :  Upload Geometry")
    files = MultiFileField('Upload Geometry', file_types=['.png', '.jpg', '.jpeg',".obj",".3dm"], max_size=5_000_000)
    # Input fields
    # {"truss_depth": 3, "u_division": 18, "v_division": 16, "truss_lines": .7, "diagonals": .1}
    text3 =Text("## Step 2 :  Configure SpaceTruss")
    truss_depth = NumberField("truss_depth", default=3)
    u_division = NumberField("u_division", default=18)
    v_division = NumberField("v_division", default=16)
    truss_lines = NumberField("truss_lines", default=0.2)
    diagonals = NumberField("diagonals", default=0.1)
    is_true = BooleanField('Shaded / Skeleton')


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @GeometryAndDataView("Geometry", duration_guess=10, update_label='Run Grasshopper')
    def run_grasshopper(self, params, **kwargs):
        # Create a JSON file from the input parameters
        input_json = json.dumps(params)
        print(params)
        # Generate the input files
        files = [('input.json', BytesIO(bytes(input_json, 'utf8')))]

        # Run the Grasshopper analysis and obtain the output files
        generic_analysis = GenericAnalysis(files=files, executable_key="run_grasshopper",
                                           output_filenames=["geometry.3dm"])
        generic_analysis.execute(timeout=60)
        threedm_file = generic_analysis.get_output_file("geometry.3dm", as_file=True)

        data_group = DataGroup(
            DataItem("Area",1733),
            DataItem("Cost", (params.u_division + params.v_division )*34)
        )

        # return GeometryResult(geometry=threedm_file, geometry_type="3dm")
        return GeometryAndDataResult(geometry=threedm_file, geometry_type="3dm", data=data_group)


