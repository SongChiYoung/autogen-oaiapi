import uuid

def generate_session_id() -> str:
    return str(uuid.uuid4())

def generate_key() -> str:
    return f"autogen-oaiapi-key-{str(uuid.uuid4())}"