import json
import jsonschema

SCHEMA_PATH="resources/acnh_schema.json"
DOCUMENT_PATH="resources/acnh.json"

with open(SCHEMA_PATH) as f:
    schema = json.loads(f.read())

with open(DOCUMENT_PATH) as f:
    document = json.loads(f.read())

validator = jsonschema.Draft7Validator(schema)

errors = list(validator.iter_errors(document))  # get all validation errors

missingParams = []
patternErrors = []

for error in errors:
    if error.validator == "required":
        missingParams.append(error.message.split()[0].replace("'", ""))
    elif error.validator == "pattern" and len(error.path) == 1:
        patternErrors.append(
            {
                "field": error.path[0],
                "message": error.schema['error_msg']
            }
        )

if len(missingParams) > 0:
    print(f"Missing mandatory param(s): {missingParams}")
elif len(patternErrors) > 0:
    for err in patternErrors:
        print(f"- {err}")
else:
    print("The document is valid.")
