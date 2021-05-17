from jsonschema import Draft7Validator, RefResolver
import argparse
from ruamel.yaml import YAML
import json


main_schema_file = 'schema.json'
strict_schema_file = 'schema-strict.json'


def print_validation_result(validator, data):
    if validator.is_valid(data):
            print('Data is valid!')
    else:
        print('Data is invalid! Errors:')
        for i, error in enumerate(sorted(validator.iter_errors(data), key=str)):
            print('    ' + str(i + 1) + ': ' + error.message)


def validate(data_path, strict_bool):
    # Read main schema file, we need this in any case
    with open(main_schema_file, 'r') as sf:
        main_schema = json.loads(sf.read())

    # Read YAML data, we need this in any case
    with open(data_path, 'r') as fi:
        yaml = YAML(typ='safe')
        data = yaml.load(fi)

    # Do we need strict validation?
    if strict_bool:
        print('Strict validation')
        # Read strict schema
        with open(strict_schema_file, 'r') as sf:
            strict_schema = json.loads(sf.read())
        schemastore = {}

        # Store both schemas in local schemastore
        schemastore[main_schema["$id"]] = main_schema
        schemastore[strict_schema["$id"]] = strict_schema
        assert len(schemastore) == 2

        # Construct ref resolver
        # https://python-jsonschema.readthedocs.io/en/stable/references/#jsonschema.RefResolver
        resolver = RefResolver(
            "file://schema-strict.json", referrer=strict_schema, store=schemastore)
        print_validation_result(Draft7Validator(strict_schema, resolver=resolver), data)
    else:
        print('Lax validation')
        print_validation_result(Draft7Validator(main_schema), data)
        


if __name__ == "__main__":
    """Run like this from the command line:
    `python3 -m schema_poc.py -d data.yml [-s]`
    """
    parser = argparse.ArgumentParser(
        description='Validates a YAML file against a JSON Schema')
    parser.add_argument(
        '-d', '--data', type=str,
        help='A YAML data file', required=True)
    parser.add_argument(
        '-s', '--strict', help='Turns on strict validation', action="store_true")
    args = parser.parse_args()
    validate(args.data, args.strict)
