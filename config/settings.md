# Settings

```yaml
project_name: "python_project"
project_goal: "Build a Python application with modern best practices."
project_type: "python"
num_sprints: 2
iterations_per_sprint: 2

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "phi-3-mini-4k-instruct"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./python_project"
vector_db_path: "./project_db"
git_branch_prefix: "sprint-"
human_input_mode: "NEVER"

rl:
  epsilon: 0.1
  alpha: 0.1
  gamma: 0.9
  state_buckets: 10

rag:
  top_k: 5
  max_doc_tokens: 4000

project_config:
  project_type: "python"
  language: "python"
  python:
    package_manager: "pip"
    test_command: "pytest"
    build_command: "python setup.py build"
    virtual_env: true
    requirements_file: "requirements.txt"

debug_mode: false
auto_commit: true
create_pr: false
```
