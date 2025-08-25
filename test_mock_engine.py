#!/usr/bin/env python3
"""
Test script for the AutoGen TS Engine with Mock LLM.
This allows development and testing without requiring a heavy LLM model.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from autogen_ts_engine.config_parser import ConfigParser
from autogen_ts_engine.sprint_runner import SprintRunner
from autogen_ts_engine.logging_utils import EngineLogger

def test_mock_engine():
    """Test the engine with mock LLM."""
    print("🚀 Testing AutoGen TS Engine with Mock LLM...")
    
    try:
        # Initialize components
        print("📋 Initializing config parser...")
        config_parser = ConfigParser()
        
        print("📖 Loading settings...")
        config_dir = Path("config")
        settings = config_parser.parse_settings(config_dir)
        print(f"   Project: {settings.project_name}")
        print(f"   Type: {settings.project_type}")
        print(f"   Goal: {settings.project_goal}")
        
        print("🤖 Loading agent definitions...")
        agent_definitions = config_parser.parse_agents(config_dir)
        print(f"   Found {len(agent_definitions)} agents")
        
        print("📝 Initializing logger...")
        logger = EngineLogger(debug_mode=True)
        
        print("🏃 Initializing sprint runner...")
        sprint_runner = SprintRunner(settings, logger)
        
        print("✅ All components initialized successfully!")
        
        # Test a single sprint
        print("\n🎯 Running a single sprint with mock LLM...")
        success = sprint_runner.run_sprints(agent_definitions)
        
        if success:
            print("🎉 Sprint completed successfully!")
            print("📁 Check the project directory for generated files:")
            print(f"   {settings.work_dir}")
        else:
            print("❌ Sprint failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_mock_engine()
    sys.exit(0 if success else 1)
