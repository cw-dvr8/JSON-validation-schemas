#!/usr/bin/env python3

"""
Program: schema_tools.py

Purpose: Common functions used by validation or template generation programs.

"""

VALUES_LIST_KEYWORDS = ["anyOf", "enum"]

def convert_bool_to_string(input_value):

    """
    Function: convert_bool_to_string

    Purpose: Convert a value from the Python Boolean representation (True/False)
             into a lower case string representation (true/false).

    Arguments: A variable that might contain a Python Boolean value

    Returns: Either a) a string representation of a Boolean value if
             the value passed in was a Python Boolean, or b) the original
             value if it was not.
    """
    string_conversion = {True: "true", False: "false"}

    # Make sure that the input value is a Boolean. Passing a string in
    # will probably not matter, but passing a number into the conversion
    # will convert any 0/1 values into false/true.
    if isinstance(input_value, bool):
        return_value = string_conversion.get(input_value, input_value)
    else:
        return_value = input_value

    return return_value


def convert_string_to_bool(input_value):
    """
    Function: convert_string_to_bool

    Purpose: Convert a string true/false value into a Python Boolean value (True/False)

    Arguments: A variable that might contain a true/false value

    Returns: Either a) a Boolean value if the value contained a string
             true/false value, or b) the original value if it did not.
    """
    bool_conversion = {"TRUE": True, "FALSE": False}

    if isinstance(input_value, str):
        return_value = bool_conversion.get(input_value.upper(), input_value)
    else:
        return_value = input_value

    return return_value


def convert_string_to_numeric(input_value):
    """
    Function: convert_string_to_numeric

    Purpose: Convert a string numeric value into the appropriate numeric typ (either
             integer or float).

    Arguments: A variable that might contain a string representation of a number.

    Returns: Either a) a number, or b) the original value if the string was not a number.
    """
    if input_value.isnumeric():
        return_value = int(input_value)
    elif input_value.replace(".", "", 1).isnumeric():
        return_value = float(input_value)
    else:
        return_value = input_value

    return return_value


def get_schema_properties(json_schema):
    """
    Function: get_schema_properties

    Purpose: Return dictionaries of schema properties needed to generate templates.

    Input parameters: File object pointing to the JSON schema file

    Returns: A dictionary of key types, definitions, required keys, and maximum sizes
                 definitions_dict[key]["type"] - string
                 definitions_dict[key]["description"] - string
                 definitions_dict[key]["required"] - Boolean
                 definitions_dict[key]["maximumSize"] - integer

             A dictionary of key values lists
                 values_dict[key][list index]["value"] - string
                 values_dict[key][list index]["valueDescription"] - string
                 values_dict[key][list index]["source"] - string
    """

    import collections

    values_list_keys = VALUES_LIST_KEYWORDS

    definitions_dict = collections.defaultdict(dict)
    definitions_keys = ["type", "description", "required", "maximumSize"]
    values_dict = collections.defaultdict(list)
    values_keys = ["value", "valueDescription", "source"]

    for schema_key in json_schema["properties"].keys():
        definitions_dict[schema_key] = dict.fromkeys(definitions_keys)
        schema_values = json_schema["properties"][schema_key]

        if schema_values:
            if "type" in schema_values:
                definitions_dict[schema_key]["type"] = schema_values["type"]

            if "description" in schema_values:
                definitions_dict[schema_key]["description"] = schema_values["description"]

            if "maximumSize" in schema_values:
                definitions_dict[schema_key]["maximumSize"] = schema_values["maximumSize"]

            if ("required" in json_schema) and (schema_key in json_schema["required"]):
                definitions_dict[schema_key]["required"] = True
            else:
                definitions_dict[schema_key]["required"] = False

            if "pattern" in schema_values:
                values_dict[schema_key].append({"value": schema_values["pattern"],
                                                "valueDescription": "",
                                                "source": ""})

            elif any([value_key in schema_values for value_key in values_list_keys]):
                vkey = list(set(values_list_keys).intersection(schema_values))[0]
                for value_row in schema_values[vkey]:
                    key_values_dict = dict.fromkeys(values_keys)

                    if "const" in value_row:
                        key_values_dict["value"] = value_row["const"]

                    if "description" in value_row:
                        key_values_dict["valueDescription"] = value_row["description"]

                    if "source" in value_row:
                        key_values_dict["source"] = value_row["source"]

                    values_dict[schema_key].append(key_values_dict)

    return(definitions_dict, values_dict)


def load_and_deref(schema_file_handle):
    """
    Function: load_and_deref

    Purpose: Load the JSON validation schema and resolve any $ref statements.

    Arguments: JSON schema file handle

    Returns: A dictionary containing the full path of the object reference, and a
             dereferenced JSON schema in dictionary form
    """
    import json
    import jsonschema

    ref_location_dict = {}

    # Load the JSON schema. I am not using jsonref to resolve the $refs on load
    # so that the $refs can point to different locations. I formerly had to pass in
    # a reference path when I was using jsonref, so all of the modules accessed by
    # the $ref statements had to live in the same location.
    json_schema = json.load(schema_file_handle)

    # Create a reference resolver from the schema.
    ref_resolver = jsonschema.RefResolver.from_schema(json_schema)

    # Resolve any references in the schema.
    for schema_key in json_schema["properties"]:
        if "$ref" in json_schema["properties"][schema_key]:
            deref_object = ref_resolver.resolve(json_schema["properties"][schema_key]["$ref"])
            ref_location_dict[schema_key] = deref_object[0]
            json_schema["properties"][schema_key] = deref_object[1]
        else:
            json_schema["properties"][schema_key] = json_schema["properties"][schema_key]

    return(ref_location_dict, json_schema)


def validation_errors(schema_errors, **kwargs):
    """
    Function: validation_errors

    Purpose: Create an output error message for errors found using a
             jsonschema validator

    Arguments: The deque output of the jsonschema validator
               Any text to be prepended to the error string

    Returns: A string containing any errors found during validation
    """

    prepend_string = ""
    error_string = ""

    for in_string in kwargs.values():
        prepend_string += in_string

    for error in schema_errors:
        # If the first value in the realtive_schema_path deque is "properties", the
        # second value is going to be the name of the column that is in error. If it
        # is not, the problem is something other than a column type or value error
        # and the column name will not be in the deque..
        if error.relative_schema_path[0] == "properties":
            error_string += f"{prepend_string} {error.relative_schema_path[1]}: {error.message}\n"
        else:
            error_string += f"{prepend_string} {error.message}\n"

    return error_string
