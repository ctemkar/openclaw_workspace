
def safe_read_json_file(filename):
    """Safely read JSON file, handling both list and dict formats"""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Handle different data structures
        if isinstance(data, list):
            return {"type": "list", "data": data, "count": len(data)}
        elif isinstance(data, dict):
            return {"type": "dict", "data": data, "keys": list(data.keys())}
        else:
            return {"type": "unknown", "data": data, "error": "Unexpected format"}
            
    except FileNotFoundError:
        return {"type": "error", "error": f"File not found: {filename}"}
    except json.JSONDecodeError as e:
        return {"type": "error", "error": f"JSON decode error: {e}"}
    except Exception as e:
        return {"type": "error", "error": f"Error reading file: {e}"}
