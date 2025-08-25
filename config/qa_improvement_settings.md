# Q&A and Improvement Session Settings

```yaml
project_name: "qa_improvement_session"
project_goal: "Analyze and improve existing codebase through Q&A sessions and automated improvements."
project_type: "python"
num_sprints: 3
iterations_per_sprint: 5

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "phi-3-mini-4k-instruct"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./qa_improvement_project"
vector_db_path: "./qa_project_db"
git_branch_prefix: "improvement-"
human_input_mode: "AUTO"  # Allow human input for Q&A

rl:
  epsilon: 0.05  # Lower exploration for focused improvements
  alpha: 0.15    # Higher learning rate for quick adaptation
  gamma: 0.95    # Higher future reward consideration
  state_buckets: 15

rag:
  top_k: 8       # More context for comprehensive analysis
  max_doc_tokens: 6000  # Larger context window

project_config:
  project_type: "python"
  language: "python"
  python:
    package_manager: "pip"
    test_command: "pytest"
    build_command: "python setup.py build"
    virtual_env: true
    requirements_file: "requirements.txt"

# Q&A and Improvement specific settings
qa_mode: true
improvement_focus:
  - "code_quality"
  - "performance"
  - "security"
  - "testing"
  - "documentation"
  - "architecture"

# Analysis depth settings
analysis_depth: "comprehensive"  # deep, comprehensive, quick
improvement_priority: "balanced"  # high_impact, balanced, incremental

debug_mode: false
auto_commit: true
create_pr: false
