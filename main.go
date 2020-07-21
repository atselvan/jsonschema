package main

import (
	"fmt"
	"github.com/atselvan/goutils"
	"github.com/xeipuuv/gojsonschema"
)

const (
	schemaPath = "./resources/acnh_schema.json"
	documentPath = "./resources/acnh.json"
)

func main() {

	err := ValidateJsonSchema(schemaPath, documentPath)
	
	if err != nil {
		log := utils.LogFormatter{ErrMsg: err}
		log.Error().Println(log.Out)
	} else {
		log := utils.LogFormatter{Msg: "The document is valid"}
		log.Info().Println(log.Out)
	}
}

func ValidateJsonSchema(schemaPath, documentPath string) error {
	var (
		schema        map[string]interface{}
		missingParams []string
	)

	if err := utils.ReadJsonFile(schemaPath, &schema); err != nil {
		panic(err)
	}

	schemaProperties := schema["properties"].(map[string]interface{})

	schemaLoader := gojsonschema.NewReferenceLoader("file://" + schemaPath)
	documentLoader := gojsonschema.NewReferenceLoader("file://" + documentPath)

	result, err := gojsonschema.Validate(schemaLoader, documentLoader)
	if err != nil {
		panic(err.Error())
	}

	for _, err := range result.Errors() {
		if err.Type() == "required" {
			if err.Details()["field"].(string) == "(root)" {
				missingParams = append(missingParams, err.Details()["property"].(string))
			} else {
				missingParams = append(missingParams, err.Details()["field"].(string)+"."+err.Details()["property"].(string))
			}
		}
	}
	if len(missingParams) > 0 {
		return utils.MissingMandatoryParamError(missingParams)
	}

	for _, err := range result.Errors() {
		if err.Type() == "pattern" {
			fieldDefinition := schemaProperties[err.Field()].(map[string]interface{})
			return fmt.Errorf(fieldDefinition["error_msg"].(string))
		} else {
			return fmt.Errorf("%v", err)
		}
	}
	return nil
}
