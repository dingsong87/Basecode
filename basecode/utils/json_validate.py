from jsonschema import Draft4Validator, validators


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS['properties']

    def set_defaults(validator, properties, instance, schema):
        for property, sub_schema in properties.iteritems():
            if "default" in sub_schema:
                instance.setdefault(property, sub_schema['default'])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return validators.extend(validator_class, {"properties": set_defaults})

DefaultValidatingDraft4Validator  = extend_with_default(Draft4Validator)
