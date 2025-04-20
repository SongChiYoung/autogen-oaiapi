# 🧠 autogen-oaiapi

OpenAI-style Chat API server for [AutoGen](https://github.com/microsoft/autogen) teams.  
Deploy your own `/v1/chat/completions` endpoint using any AutoGen-compatible team configuration.

---

## ✨ Features

- ✅ **OpenAI-compatible** API interface
- ✅ Plug in any AutoGen `GroupChat` or `SocietyOfMindAgent`
- ✅ Session-aware execution (per session_id)
- ✅ FastAPI-based server with `/v1/chat/completions` endpoint
- ✅ `stream=True` response support (coming soon)

---

## 📦 Installation
```shell
pip install autogen-oaiapi
```

---

## How to use?
Using just `SIMPLE` api!

example
```python
client = OpenAIChatCompletionClient(
    model="claude-3-5-haiku-20241022"
)
agent1 = AssistantAgent(name="writer", model_client=client)
agent2 = AssistantAgent(name="editor", model_client=client)
team = RoundRobinGroupChat(
    participants=[agent1, agent2],
    termination_condition=TextMentionTermination("TERMINATE")
)

server = Server(team=team, source_select="writer")
server.run(host="0.0.0.0", port=8000)  # you could do not filled that args. default is that host="0.0.0.0", port=8000
```

Just write AutoGen team, and... Run it!

CURL call test!
example
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
 -H "Content-Type: application/json" \
 -d '{
 "session_id": "test-session",
 "messages": [ { "role": "user", "content": "Please write 5 funny stories." } ]
}'
```

---

## Demo
![Demo](https://github.com/SongChiYoung/autogen-oaiapi/blob/main/demo.gif?raw=true)
