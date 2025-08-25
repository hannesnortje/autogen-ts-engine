# TypeScript Settings

```yaml
project_name: "typescript_project"
project_goal: "Build a modern TypeScript application with React and Node.js."
project_type: "typescript"
num_sprints: 2
iterations_per_sprint: 2

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "phi-3-mini-4k-instruct"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./typescript_project"
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
  project_type: "typescript"
  language: "typescript"
  typescript:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"
    lint_command: "npm run lint"
    framework: "react"
    node_version: "18"
    typescript_version: "5.0"
    react_version: "18.0"
    testing_framework: "jest"
    bundler: "vite"

debug_mode: false
auto_commit: true
create_pr: false
