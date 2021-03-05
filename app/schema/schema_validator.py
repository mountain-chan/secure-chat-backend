user_validator = {
    "type": "object",
    "properties": {
        "password": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "display_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "gender": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        }
    },
    "required": []
}

password_validator = {
    "type": "object",
    "properties": {
        "current_password": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "new_password": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        }
    },
    "required": ["new_password"]
}
