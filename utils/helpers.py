from bson import ObjectId
from datetime import datetime

def serialize_doc(doc):
    """Helper function to convert ObjectId to string and handle datetime objects"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        
        # Handle MongoDB's special formats first
        if "$oid" in doc:
            return doc["$oid"]
        if "$date" in doc:
            date_str = doc["$date"]
            if isinstance(date_str, str):
                
                # Extract just the date part (YYYY-MM-DD)
                return date_str.split('T')[0]
            return str(date_str).split('T')[0]
        
        # Process regular dictionary
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.strftime('%Y-%m-%d')
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.strftime('%Y-%m-%d')
    return doc