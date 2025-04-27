# 🧠 autogen-oaiapi
[![GitHub stars](https://img.shields.io/github/stars/SongChiYoung/autogen-oaiapi?style=social)](https://github.com/SongChiYoung/autogen-oaiapi/stargazers)
[![Downloads](https://static.pepy.tech/personalized-badge/autogen-oaiapi?period=week&units=international_system&left_color=gray&right_color=orange&left_text=Downloads/week)](https://pepy.tech/project/autogen-oaiapi)

OpenAI-style Chat API server for [AutoGen](https://github.com/microsoft/autogen) teams.  
Deploy your own `/v1/chat/completions` endpoint using any AutoGen-compatible team configuration.

🚀 **Try it? → Don’t forget to ⭐ the repo if useful!**


> A **self-hosted**, **open-source alternative** to OpenAI’s ChatCompletion API, built on top of Microsoft AutoGen.
> 
> 🔍 **Looking for**:
> - **OpenAI-style API server** you can run locally?
> - An **AutoGen-based ChatCompletion** implementation?
> - A **FastAPI wrapper** for multi-agent LLM orchestration?
> 
> You found it. 🚀


---
## WARNING
### NOW(autogen-agentchat == 0.5.5) limit supported. 
> Because of it has bug on deserialization `AssistantAgent` with tools.


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


---

## Multi team support
```python
from autogen_oaiapi.server import Server
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano"
)
agent1 = AssistantAgent(name="writer", model_client=client)
agent2 = AssistantAgent(name="editor", model_client=client)
team = RoundRobinGroupChat(
    participants=[agent1, agent2],
    termination_condition=TextMentionTermination("TERMINATE"),
)

server = Server()
server.model.register(
    name="TEST_TEAM",
    actor=team,
    source_select="writer",
)
server.run(port=8001)
```

or 

```python
from autogen_oaiapi.server import Server
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

server = Server()

@server.model.register(name="TEST_TEAM_DECORATOR", source_select="writer")
def build_team():
    client = OpenAIChatCompletionClient(
        model="gpt-4.1-nano"
    )
    agent1 = AssistantAgent(name="writer", model_client=client)
    agent2 = AssistantAgent(name="editor", model_client=client)
    team = RoundRobinGroupChat(
        participants=[agent1, agent2],
        termination_condition=TextMentionTermination("TERMINATE"),
    )
    return team

server.run(port=8001)
```

**Look at the `example` folder include more examples!**
- simmple example
- function style register example
- decorator sytle register example
- JSON file style api_key register example
- Memory style api_key register example

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SongChiYoung/autogen-oaiapi&type=Date)](https://www.star-history.com/#SongChiYoung/autogen-oaiapi&Date)
