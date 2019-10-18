#!/usr/bin/env python3

"""
Program: create_template_from_schema.py

Purpose: Use a JSON validation schema to generate a csv template file. If
         a definitions file is also desired, it will be created with an
         '_definitions' added to the end of the file name before the
         extension.

Input parameters: Full pathname to the JSON validation schema
                  Full pathname to the output template file
                  Optional flag to generate a definitions file

Outputs: csv template file

Execution: create_template_from_schema.py <JSON schema> <output file>
               --definitions

"""

import argparse
import csv
from schema_tools import convert_bool_to_string
from schema_tools import load_and_deref
from schema_tools import values_list_keywords

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("json_schema_file", type=argparse.FileType("r"),
                        help="Full pathname for the JSON schema file")
    parser.add_argument("output_file", type=argparse.FileType("w"),
                        help="Full pathname for the output file")
    parser.add_argument("--definitions", action="store_true",
                        help="Indicates that a definitions file should be generated also")

    args = parser.parse_args()

    values_list_keys = values_list_keywords()

    # Define headers for the definitions file in case one is requested.
    definition_column_headers = ["key", "type", "definition", "required", "rules", "possible values", "possible values definitions"]

    # Load the JSON schema.
    _, json_schema = load_and_deref(args.json_schema_file)

    # Get the schema keys into a list and then write them to the output file.
    column_header_list = []
    for column_header in json_schema["properties"].keys():
        column_header_list.append(column_header)

    template_writer = csv.writer(args.output_file, delimiter=",")
    template_writer.writerow(column_header_list)
    args.output_file.close()

    # Write the definitions file if one has been requested.
    if args.definitions:

        # Create the new output file name.
        output_file_name = args.output_file.name
        if output_file_name.find(".") != -1:
            dot_location = output_file_name.find(".")
            def_output_filename = output_file_name[: dot_location] + "_definitions" + output_file_name[dot_location :]
        else:
            def_output_filename = output_file_name + "_definitions"

        def_output_file = open(def_output_filename, "w")
        definitions_writer = csv.DictWriter(def_output_file, fieldnames=definition_column_headers)
        definitions_writer.writeheader()

        for json_key in json_schema["properties"]:
            output_row = {}

            # Assemble the output row.
            output_row["key"] = json_key

            if len(json_schema["properties"][json_key].keys()) > 0:
                if "type" in json_schema["properties"][json_key]:
                    output_row["type"] = json_schema["properties"][json_key]["type"]

                if "description" in json_schema["properties"][json_key]:
                    output_row["definition"] = json_schema["properties"][json_key]["description"]

                if json_key in json_schema["required"]:
                    output_row["required"] = "Yes"

                if "pattern" in json_schema["properties"][json_key]:
                    output_row["rules"] = json_schema["properties"][json_key]["pattern"]

                if any([value_key in json_schema["properties"][json_key] for value_key in values_list_keys]):
                    vkey = list(set(values_list_keys).intersection(json_schema["properties"][json_key]))[0]
                    for value_row in json_schema["properties"][json_key][vkey]:
                        if "const" in value_row:
                            output_row["possible values"] = convert_bool_to_string(value_row["const"])
                            if "description" in value_row:
                                output_row["possible values definitions"] = value_row["description"]
                            definitions_writer.writerow(output_row)
                else:
                    definitions_writer.writerow(output_row)

        def_output_file.close()


if __name__ == "__main__":
    main()
