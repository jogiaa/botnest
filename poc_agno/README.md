# carburetor [agents](../../PythonProject/agents)
Extract the provided code in a folder.The directory structure should be
```
.
├── agents
│         ├── __init__.py
│         ├── calories_agent_team.py
│         ├── simplest_match_agent.py
│         └── web_search_ddg_agent.py
├── api
│         ├── __init__.py
│         └── main.py
├── data
│         └── __init__.py
├── llm_model_config.py
├── main.py
├── memory
│         ├── __init__.py
│         └── main_chroma_test.py
├── README.md
├── reuirements.txt
└── tools
    └── __init__.py
```
        
Run the following command within the folder to set up the python ‘virtual environment’.
```bash
python3 -m venv .venv
```

From the same folder run the following command to activate the virtual environment.
```bash
source .venv/bin/activate
```

After activating the virtual environment use the python package manager (pip) to install all dependencies.
```bash
pip install -r requirements.txt
```
