# Settings

```yaml
project_name: "react-dashboard"
project_goal: "Build a data visualization dashboard with React, D3.js, and Material-UI for real-time analytics"
project_type: "react"
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./react-dashboard"
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
  project_type: "react"
  language: "javascript"
  framework: "react"
  node:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"

debug_mode: false
auto_commit: true
create_pr: false
