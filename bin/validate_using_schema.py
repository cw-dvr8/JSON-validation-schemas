#!/usr/bin/env python3

"""
Program: validate_using_schema.py

Purpose: Validate an object using a JSON Draft 7 schema. If the object to
         be validated is a manifest file, it is assumed to be a csv file.

         For local reference definition files, the reference passed in
         must be preceded by the string "file://".  For remote references,
         the full URL must be provided.

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the object to be validated
                  Optional full pathname to the location of any definition
                      references.
                  Optional flag to indicate that the object is a
                      manifest file.

Outputs: Terminal output

Execution: validate_using_schema.py <JSON schema> <object to be validated>
               --reference_path <definition reference path> --manifest_file

"""

import argparse
import json
import jsonref
import jsonschema
import pandas as pd

def convert_to_boolean(data_row, val_schema):

    bool_conversion = {"TRUE": True, "FALSE": False}
    converted_row = dict()

    # We only want to convert strings into Booleans if the field has a controlled
    # values list and has more than one possible type, e.g. True, False, "Unknown".
    # In that instance, we want to convert a string true/false to a Boolean true/false
    # while ignoring case (true, TRUE, False, FaLsE, etc.).
    for rec_key in data_row:
            
        # Pass the row through if:
        # a) the key is not in the schema, i.e. the site put extra columns in the file;
        # b) the value is not a string;
        # c) the value is a string but there are no other alternative types/values for it in the schema
        if ((rec_key not in val_schema["properties"]) or
            (not(isinstance(data_row[rec_key], str))) or
            ((isinstance(data_row[rec_key], str)) and ("anyOf" not in val_schema["properties"][rec_key]))):
            converted_row[rec_key] = data_row[rec_key]

        else:
            # If it is possible for the key to contain a number and the string value is some sort of number,
            # convert the string into a number.
            number_is_possible = False
            for schema_anyof in val_schema["properties"][rec_key]["anyOf"]:
                if ("type" in schema_anyof) and (schema_anyof["type"] in ["integer", "number"]):
                    number_is_possible = True
                    break

            if number_is_possible:
                if data_row[rec_key].isnumeric():
                    converted_row[rec_key] = int(data_row[rec_key])
                elif data_row[rec_key].replace(".", "", 1).isnumeric():
                    converted_row[rec_key] = float(data_row[rec_key])
                else:
                    converted_row[rec_key] = bool_conversion.get(data_row[rec_key].upper(), data_row[rec_key])

            else:
                converted_row[rec_key] = bool_conversion.get(data_row[rec_key].upper(), data_row[rec_key])

    return converted_row


def validate_object(json_val_schema, object_to_validate):
    
    schema_validator = jsonschema.Draft7Validator(json_val_schema)

    schema_errors = schema_validator.iter_errors(object_to_validate)
    for error in schema_errors:
        # If the first value in the relative_schema_path deque is "properties", the
        # second value is going to be the name of the column that is in error.
        if error.relative_schema_path[0] == "properties":
            print(f"{error.relative_schema_path[1]}: {error.message}")
        else:
            print(f"{error.message}")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("validation_obj_file", type=argparse.FileType("r"),
                        help="Full pathname for the object to be validated")
    parser.add_argument("--reference_path", type=str,
                        help="Full pathname location for references")
    parser.add_argument("--manifest_file", action="store_true",
                        help="Is the object to be validated a manifest file?")

    args = parser.parse_args()

    # Check to see if a reference path has been passed in. If it has, use jsonref to load
    # the validation schema.  If not, use the json module.
    if args.reference_path is not None:
        json_schema = jsonref.load(args.json_schema_file, base_uri=args.reference_path, jsonschema=True)

    else:
        json_schema = json.load(args.json_schema_file)

    # If the object to be validated is a manifest file, read it into a pandas
    # dataframe.  Otherwise, read it into JSON.
    if args.manifest_file:
        data_file_df = pd.read_csv(args.validation_obj_file)

        # Pandas reads in empty fields as nan. Replace nan with None.
        data_file_df = data_file_df.replace({pd.np.nan: None})

        # Convert the dataframe to a list of dictionaries and loop through it.
        data_file_dict = data_file_df.to_dict(orient="records")
        for data_record in data_file_dict:

            # Remove any None values from the dictionary - it simplifies the coding of the
            # JSON validation schema.
            clean_record = {k: data_record[k] for k in data_record if data_record[k] is not None}

            # Convert string true/false values to Boolean true/false values only if the JSON key
            # is not strictly defined as a string column.
            converted_clean_record = convert_to_boolean(clean_record, json_schema)

            validate_object(json_schema, converted_clean_record)
    
    else:
        val_json_obj = json.load(args.validation_obj_file)

        # Convert string true/false values to Boolean true/false values.
        converted_val_json_obj = convert_to_boolean(val_json_obj, json_schema)

        validate_object(json_schema, converted_val_json_obj)

if __name__ == "__main__":
    main()
