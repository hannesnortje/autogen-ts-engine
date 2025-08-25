# Gemini Configuration Example

```yaml
project_name: "gemini_test_project"
project_goal: "Build a Python application with modern best practices using Gemini for fast testing."
project_type: "python"
num_sprints: 2
iterations_per_sprint: 3

llm_binding:
  provider: "gemini"  # Use Gemini instead of LM Studio
  model_name: "gemini-1.5-flash"  # Fastest model for testing
  api_type: "google"
  api_key: "your_google_api_key_here"  # Or set GOOGLE_API_KEY environment variable
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
```

## Setup Instructions

1. **Get Google API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

2. **Set API Key:**
   ```bash
   # Option 1: Set environment variable
   export GOOGLE_API_KEY="your_api_key_here"
   
   # Option 2: Update the config file
   # Replace "your_google_api_key_here" with your actual API key
   ```

3. **Install Gemini Dependencies:**
   ```bash
   pip install google-generativeai
   ```

4. **Run with Gemini:**
   ```bash
   # Copy this config to settings.md
   cp config/gemini_settings.md config/settings.md
   
   # Run the engine
   python autogen_ts_engine/main.py
   ```

## Benefits of Gemini for Testing

- ✅ **Fast responses** - Much faster than LM Studio
- ✅ **Free tier** - Generous free usage
- ✅ **No local setup** - No need to download models
- ✅ **Reliable** - Google's infrastructure
- ✅ **Good code generation** - Excellent for development tasks

## Model Options

- `gemini-1.5-flash` - Fastest, best for testing
- `gemini-1.5-pro` - Most capable, good for complex tasks
- `gemini-pro` - Legacy name, maps to 1.5-pro
