import os
import yaml


#####################################################################
## Generators
#####################################################################

def generate(name, spec):
    return f"""package {name.lower()}

import (
    "io"
)


/////////////////////////////////////////////////////////////////////
// {name}Request (key: {spec[name]["key"]}, version: {spec[name]["version"]})
/////////////////////////////////////////////////////////////////////

{generateStruct(spec[name]["req"])}
{generateDecode(name + "Request", spec[name]["req"])}
{generateEncode(name + "Request", spec[name]["req"])}


/////////////////////////////////////////////////////////////////////
// {name}Response (key: {spec[name]["key"]}, version: {spec[name]["version"]})
/////////////////////////////////////////////////////////////////////

{generateStruct(spec[name]["res"])}
{generateDecode(name + "Response", spec[name]["res"])}
{generateEncode(name + "Response", spec[name]["res"])}
"""

def expand(fn):
    def _expand(*args, **kwargs):
        return "\n".join(fn(*args, **kwargs))
    return _expand

def spaces(indent):
    return " " * indent * 4

@expand
def generateStruct(structs):
    for struct in structs:
        yield f"type {struct['struct']} struct {{"
        for field in struct['fields']:
            yield f"    {field['name']} {types.get(field['type'], field['type'])}"
        yield "}\n"

@expand
def generateDecode(name, structs):
    hasList = any([f["type"].startswith("[]") for s in structs for f in s["fields"]])
    indexes = ["i", "j", "k", "l", "m", "n"]

    structs = {struct["struct"]: struct["fields"] for struct in structs}

    yield f"func (msg *{name}) Decode(r io.Reader, apiVer int16, size int32) error {{"
    if hasList:
        yield "    var len int32"
    yield "    var err error"
    yield ""
    yield _generateDecode(name, structs, indexes, "msg")
    yield ""
    yield "    return nil"
    yield "}\n"

@expand
def _generateDecode(name, structs, indexes, prefix, version=0, indent=1):
    isOpen = False

    for field in structs[name]:
        if field["version"] > version and isOpen:
            indent = indent - 1
            isOpen = False
            yield spaces(indent) + "}"
        if field["version"] > version:
            yield spaces(indent) + f"if apiVer > {field['version']-1} {{"
            version = field["version"]
            indent = indent + 1
            isOpen = True
        if field["version"] < version:
            version = field["version"]
            indent = indent - 1
            isOpen = False
            yield spaces(indent) + "}"

        if field["type"] in primitives:
            yield spaces(indent) + f"if {prefix}.{field['name']}, err = {functions.get(field['type'])}(r); err != nil {{"
            yield spaces(indent) + "    return err"
            yield spaces(indent) + "}"
        elif field["type"].startswith("[]"):
            index = indexes.pop(0)
            yield spaces(indent) + "if len, err = wire.ReadInt32(r); err != nil {"
            yield spaces(indent) + "    return err"
            yield spaces(indent) + "}"
            yield spaces(indent) + f"{prefix}.{field['name']} = make({field['type']}, len)"
            yield spaces(indent) + f"for {index} := range {prefix}.{field['name']} {{"
            yield _generateDecode(field["type"][2:], structs, indexes, f"{prefix}.{field['name']}[{index}]", version=version, indent=indent+1)
            yield spaces(indent) + "}"
        else:
            yield spaces(indent) + f"{prefix}.{field['name']} = {field['type']}{{}}"
            yield _generateDecode(field["type"], structs, indexes, f"{prefix}.{field['name']}", version=version, indent=indent)

    if isOpen:
        yield spaces(indent-1) + "}"

@expand
def generateEncode(name, structs):
    yield "// Todo: generate encode function"


#####################################################################
## Helpers
#####################################################################

primitives = (
    "bool",
    "int8",
    "int16",
    "int32",
    "int64",
    "uint32",
    "varint",
    "varlong",
    "uuid",
    "float64",
    "string",
    "compact_string",
    "nullable_string",
    "compact_nullable_string",
    "bytes",
    "compact_bytes",
    "nullable_bytes",
    "compact_nullable_bytes",
    "records",
    "tag_buffer"
)

types = {
    "bool": "bool",
    "int8": "int8",
    "int16": "int16",
    "int32": "int32",
    "int64": "int64",
    "uint32": "uint32",
    "varint": "int",
    "varlong": "int",
    "uuid": "uuid.UUID",
    "float64": "float64",
    "string": "string",
    "compact_string": "string",
    "nullable_string": "string",
    "compact_nullable_string": "string",
    "bytes": "[]byte",
    "compact_bytes": "[]byte",
    "nullable_bytes": "[]byte",
    "compact_nullable_bytes": "[]byte",
    "records": "[]byte",
    "tag_buffer": "TagBuffer"
}

functions = {
    "bool": "wire.ReadBool",
    "int8": "wire.ReadInt8",
    "int16": "wire.ReadInt16",
    "int32": "wire.ReadInt32",
    "int64": "wire.ReadInt64",
    "uint32": "wire.ReadUInt32",
    "varint": "wire.ReadVarInt",
    "varlong": "wire.ReadVarLong",
    "uuid": "wire.ReadUUID",
    "float64": "wire.ReadFloat64",
    "string": "wire.ReadString",
    "compact_string": "wire.ReadString",
    "nullable_string": "wire.ReadString",
    "compact_nullable_string": "wire.ReadString",
    "bytes": "wire.ReadBytes",
    "compact_bytes": "wire.ReadBytes",
    "nullable_bytes": "wire.ReadBytes",
    "compact_nullable_bytes": "wire.ReadBytes",
    "records": "wire.ReadBytes",
    "tag_buffer": "wire.ReadTagBuffer"
}


#####################################################################
## Execute
#####################################################################

for filename in os.listdir("def"):
    name, _ = os.path.splitext(os.path.basename(filename))
    os.makedirs(os.path.dirname(f"pkg/{name.lower()}/"), exist_ok=True)

    with open(f"def/{filename}", "r") as f:
        spec = yaml.load(f.read(), Loader=yaml.FullLoader)

    with open(f"pkg/{name.lower()}/{name.lower()}.go", "w") as f:
        f.write(generate(name, spec))

    print("Processed:", name)
