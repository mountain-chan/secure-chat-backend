user_validator = {
    "type": "object",
    "properties": {
        "password": {
            "type": "string",
            "minLength": 3,
            "maxLength": 50
        },
        "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "gender": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
        "phone": {
            "type": "string",
            "minLength": 1,
            "maxLength": 20
        },
        "email": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "is_admin": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        }
    },
    "required": ["name", "gender", "phone", "email"]
}

password_validator = {
    "type": "object",
    "properties": {
        "current_password": {
            "type": "string",
            "minLength": 3,
            "maxLength": 50
        },
        "new_password": {
            "type": "string",
            "minLength": 3,
            "maxLength": 50
        }
    },
    "required": ["new_password"]
}
