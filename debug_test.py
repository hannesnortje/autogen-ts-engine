#!/usr/bin/env python3

import sys
from pathlib import Path

print("1. Starting debug test...")

# Test 1: Basic imports
print("2. Testing imports...")
try:
    from autogen_ts_engine.config_parser import ConfigParser
    print("   ✓ ConfigParser imported")
except Exception as e:
    print(f"   ✗ ConfigParser import failed: {e}")
    sys.exit(1)

try:
    from autogen_ts_engine.sprint_runner import SprintRunner
    print("   ✓ SprintRunner imported")
except Exception as e:
    print(f"   ✗ SprintRunner import failed: {e}")
    sys.exit(1)

try:
    from autogen_ts_engine.logging_utils import EngineLogger
    print("   ✓ EngineLogger imported")
except Exception as e:
    print(f"   ✗ EngineLogger import failed: {e}")
    sys.exit(1)

# Test 2: Config parsing
print("3. Testing config parsing...")
try:
    cp = ConfigParser()
    settings = cp.parse_settings(Path('config'))
    print(f"   ✓ Settings parsed: {settings.project_name}")
except Exception as e:
    print(f"   ✗ Settings parsing failed: {e}")
    sys.exit(1)

# Test 3: Agent definitions
print("4. Testing agent parsing...")
try:
    agent_defs = cp.parse_agents(Path('config'))
    print(f"   ✓ Agents parsed: {len(agent_defs)} agents")
except Exception as e:
    print(f"   ✗ Agent parsing failed: {e}")
    sys.exit(1)

# Test 4: Logger creation
print("5. Testing logger creation...")
try:
    logger = EngineLogger()
    print("   ✓ Logger created")
except Exception as e:
    print(f"   ✗ Logger creation failed: {e}")
    sys.exit(1)

# Test 5: SprintRunner creation
print("6. Testing SprintRunner creation...")
try:
    runner = SprintRunner(settings, logger)
    print("   ✓ SprintRunner created")
except Exception as e:
    print(f"   ✗ SprintRunner creation failed: {e}")
    sys.exit(1)

# Test 6: LM Studio connection
print("7. Testing LM Studio connection...")
try:
    import requests
    response = requests.get('http://localhost:1234/v1/models', timeout=5)
    print(f"   ✓ LM Studio connection: {response.status_code}")
except Exception as e:
    print(f"   ✗ LM Studio connection failed: {e}")
    sys.exit(1)

# Test 7: Agent creation
print("8. Testing agent creation...")
try:
    from autogen_ts_engine.agent_factory import AgentFactory
    from autogen_ts_engine.rag_store import RAGStore
    
    rag_store = RAGStore(settings.vector_db_path, settings.rag)
    factory = AgentFactory(settings, rag_store)
    agents = factory.create_agents(agent_defs)
    print(f"   ✓ Agents created: {len(agents)} agents")
except Exception as e:
    print(f"   ✗ Agent creation failed: {e}")
    sys.exit(1)

# Test 8: Run sprints (this is likely where it hangs)
print("9. Testing sprint execution...")
try:
    print("   Starting sprint execution...")
    results = runner.run_sprints(agent_defs)
    print(f"   ✓ Sprint execution completed: {len(results)} results")
except Exception as e:
    print(f"   ✗ Sprint execution failed: {e}")
    sys.exit(1)

print("10. All tests completed successfully!")
