import uuid

def generate_session_id():
    return str(uuid.uuid4())

def generate_key():
    return f"autogen-oaiapi-key-{str(uuid.uuid4())}"