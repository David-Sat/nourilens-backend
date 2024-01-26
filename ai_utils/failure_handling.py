import json


def clean_json_string(json_string):
    start = json_string.find('{')
    end = json_string.rfind('}')
    if start != -1 and end != -1:
        return json_string[start:end+1]
    return json_string

def is_valid_json(data):
    try:
        json.loads(data)
        return True
    except json.JSONDecodeError:
        print(data)
        return False

def retry_function(func, arg, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            result = func(arg)
            cleaned_result = clean_json_string(result)  # Clean the result
            if is_valid_json(cleaned_result):
                return cleaned_result  # Return the cleaned result
            else:
                raise ValueError("Invalid JSON returned")
        except (ValueError, json.JSONDecodeError) as e:
            if attempt == max_attempts - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")