import os
import yaml


def generate(name, spec):
    return f"""package {name}


/////////////////////////////////////////////////////////////////////
// Request
/////////////////////////////////////////////////////////////////////

{generateStruct(spec["req"])}

{generateDecode(spec["req"])}

{generateEncode(spec["req"])}


/////////////////////////////////////////////////////////////////////
// Response
/////////////////////////////////////////////////////////////////////

{generateStruct(spec["res"])}

{generateDecode(spec["res"])}

{generateEncode(spec["res"])}
"""

def generateStruct(spec):
    return "// Todo: generate struct"

def generateDecode(spec):
    return "// Todo: generate decode function"

def generateEncode(spec):
    return "// Todo: generate encode function"


for filename in os.listdir("def"):
    name, _ = os.path.splitext(os.path.basename(filename))
    os.makedirs(os.path.dirname(f"pkg/{name}/"), exist_ok=True)

    with open(f"def/{filename}", "r") as f:
        api = yaml.load(f.read(), Loader=yaml.FullLoader)
        api = {k.lower(): v for k, v in api.items()}

    with open(f"pkg/{name}/{name}.go", "w") as f:
        f.write(generate(name, api[name]))
