task_request_schema = {
  "name": "TaskResponse",
  "strict": True,
  "schema": {
    "type": "object",
    "properties": {
      "TASK": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "parameters": {
              "type": "array",
              "items": {
                "type": "array",
                  "items": {
                    "type": "number"
                  }
              }
            },
            "pass_returned_value_from": {
              "type": "string"
            },
          },
          "required": ["name", "parameters", "pass_returned_value_from"],
          "additionalProperties": False
        }
      }
    },
    "required": ["TASK"],
    "additionalProperties": False
  }
}