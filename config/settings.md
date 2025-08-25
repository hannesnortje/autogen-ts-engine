
project_name: "gemini_test_project"
project_goal: "Build a Python web application with FastAPI and modern best practices using Gemini for development."
project_type: "python"
num_sprints: 2
iterations_per_sprint: 3

llm_binding:
  provider: "gemini"
  model_name: "gemini-1.5-flash"
  api_type: "google"
  api_key: "AIzaSyDMxMeiGJTAN0iM1gYoURO4PA0JfhFjdGU"
  cache_seed: 42

work_dir: "./gemini_test_project"
vector_db_path: "./gemini_project_db"
git_branch_prefix: "gemini-"
human_input_mode: "AUTO"

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
