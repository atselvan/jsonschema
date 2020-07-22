import json
import jsonschema

SCHEMA_PATH = "resources/acnh_schema.json"
DOCUMENT_PATH = "resources/acnh.json"


class ValidationError(Exception):
    """
    Base Class for validation errors
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MissingMandatoryParamError(ValidationError):
    """
    Class for missing mandatory param errors
    """

    def __init__(self, message):
        super(MissingMandatoryParamError, self).__init__(message)


class JsonSchemaValidationError(ValidationError):
    """
    Class for json schema validation errors
    """

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super(JsonSchemaValidationError, self).__init__(f"field: {self.field}, message: {self.message}")


def validate_json_doc(schema_path: str, document_path: str):
    with open(schema_path) as f:
        schema = json.loads(f.read())

    with open(document_path) as f:
        document = json.loads(f.read())

    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(document))  # get all validation errors

    missing_params = []

    for error in errors:
        if error.validator == "required":
            field = error.message.split()[0].replace("'", "")
            field_path = '.'.join([str(x) for x in list(error.path)])

            if field_path:
                missing_params.append(field_path + "." + field)
            else:
                missing_params.append(field)

    if len(missing_params) > 0:
        raise MissingMandatoryParamError(f"Missing mandatory param(s): {missing_params}")

    for error in errors:

        field = '.'.join([str(x) for x in list(error.path)])

        if error.validator == "pattern" and len(error.path) == 1:
            raise JsonSchemaValidationError(field=field, message=error.schema['error_msg'])
        else:
            raise JsonSchemaValidationError(field=field, message=error.message)


try:
    validate_json_doc(SCHEMA_PATH, DOCUMENT_PATH)
except ValidationError as e:
    print(e)
else:
    print("The document is valid.")
