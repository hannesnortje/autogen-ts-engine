# Settings

```yaml
project_name: "typescript-api"
project_goal: "Build a REST API server with Express.js, TypeScript, and PostgreSQL for a task management system"
project_type: "typescript"
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./typescript-api"
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
  framework: "express"
  node:
    package_manager: "npm"
    test_command: "npm test"
    build_command: "npm run build"

debug_mode: false
auto_commit: true
create_pr: false
```
