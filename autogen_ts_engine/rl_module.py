"""Reinforcement learning module for the AutoGen TS Engine."""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from gymnasium import spaces

from .schemas import RLConfig


class ActionSpace:
    """Action space for the RL agent."""
    
    ACTIONS = [
        "refactor_code",
        "add_tests", 
        "improve_docs",
        "split_module",
        "reduce_dependencies",
        "optimize_performance",
        "fix_bugs",
        "add_features"
    ]
    
    def __init__(self):
        self.actions = self.ACTIONS
        self.n_actions = len(self.actions)
    
    def sample(self) -> str:
        """Sample a random action."""
        return random.choice(self.actions)
    
    def get_action_index(self, action: str) -> int:
        """Get index of an action."""
        return self.actions.index(action)


class StateSpace:
    """State space for the RL agent."""
    
    def __init__(self, config: RLConfig):
        self.config = config
        self.state_buckets = config.state_buckets
        
        # State dimensions
        self.test_pass_rate_buckets = self.state_buckets
        self.coverage_buckets = self.state_buckets
        self.complexity_buckets = self.state_buckets
        self.dependency_count_buckets = self.state_buckets
        
        self.n_states = (
            self.test_pass_rate_buckets *
            self.coverage_buckets *
            self.complexity_buckets *
            self.dependency_count_buckets
        )
    
    def discretize_state(self, 
                        test_pass_rate: float,
                        coverage: float, 
                        complexity: float,
                        dependency_count: int) -> int:
        """Convert continuous state to discrete state index."""
        # Normalize and bucketize each dimension
        test_bucket = min(int(test_pass_rate * self.test_pass_rate_buckets), 
                         self.test_pass_rate_buckets - 1)
        coverage_bucket = min(int(coverage * self.coverage_buckets), 
                            self.coverage_buckets - 1)
        complexity_bucket = min(int(complexity * self.complexity_buckets), 
                              self.complexity_buckets - 1)
        dependency_bucket = min(dependency_count, self.dependency_count_buckets - 1)
        
        # Convert to single state index
        state_index = (
            test_bucket * self.coverage_buckets * self.complexity_buckets * self.dependency_count_buckets +
            coverage_bucket * self.complexity_buckets * self.dependency_count_buckets +
            complexity_bucket * self.dependency_count_buckets +
            dependency_bucket
        )
        
        return state_index


class QLearningAgent:
    """Q-learning agent for inner loop action selection."""
    
    def __init__(self, config: RLConfig, state_space: StateSpace, action_space: ActionSpace):
        self.config = config
        self.state_space = state_space
        self.action_space = action_space
        
        # Q-table: state -> action -> value
        self.q_table = np.zeros((state_space.n_states, action_space.n_actions))
        
        # Learning parameters
        self.epsilon = config.epsilon  # Exploration rate
        self.alpha = config.alpha      # Learning rate
        self.gamma = config.gamma      # Discount factor
    
    def select_action(self, state: int) -> str:
        """Select action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            # Exploration: random action
            return self.action_space.sample()
        else:
            # Exploitation: best action
            return self.action_space.actions[np.argmax(self.q_table[state])]
    
    def update(self, state: int, action: str, reward: float, next_state: int) -> None:
        """Update Q-table using Q-learning update rule."""
        action_idx = self.action_space.get_action_index(action)
        
        # Q-learning update
        current_q = self.q_table[state, action_idx]
        max_next_q = np.max(self.q_table[next_state])
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state, action_idx] = new_q
    
    def get_policy(self, state: int) -> Dict[str, float]:
        """Get action probabilities for a state."""
        q_values = self.q_table[state]
        max_q = np.max(q_values)
        
        # Softmax probabilities
        exp_q = np.exp(q_values - max_q)
        probabilities = exp_q / np.sum(exp_q)
        
        return dict(zip(self.action_space.actions, probabilities))
    
    def save(self, file_path: Path) -> None:
        """Save Q-table to file."""
        data = {
            "q_table": self.q_table.tolist(),
            "config": self.config.dict(),
            "state_space": {
                "state_buckets": self.state_space.state_buckets
            },
            "action_space": {
                "actions": self.action_space.actions
            }
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, file_path: Path) -> None:
        """Load Q-table from file."""
        if file_path.exists():
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.q_table = np.array(data["q_table"])


class OuterLoopPolicy:
    """Outer loop policy for sprint-level decisions."""
    
    def __init__(self, config: RLConfig):
        self.config = config
        self.sprint_rewards = []
        self.policy_weights = {
            "test_focus": 1.0,
            "feature_focus": 1.0,
            "refactor_focus": 1.0,
            "documentation_focus": 1.0
        }
    
    def update_policy(self, sprint_reward: float, sprint_metrics: Dict) -> None:
        """Update outer loop policy based on sprint results."""
        self.sprint_rewards.append(sprint_reward)
        
        # Simple policy update based on trends
        if len(self.sprint_rewards) >= 2:
            recent_trend = self.sprint_rewards[-1] - self.sprint_rewards[-2]
            
            # Adjust weights based on what worked
            if recent_trend > 0:
                # Positive trend - reinforce current focus
                if sprint_metrics.get("test_coverage", 0) > 0.8:
                    self.policy_weights["test_focus"] *= 1.1
                if sprint_metrics.get("features_added", 0) > 0:
                    self.policy_weights["feature_focus"] *= 1.1
                if sprint_metrics.get("refactoring_done", 0) > 0:
                    self.policy_weights["refactor_focus"] *= 1.1
                if sprint_metrics.get("docs_updated", 0) > 0:
                    self.policy_weights["documentation_focus"] *= 1.1
            else:
                # Negative trend - try different focus
                self.policy_weights["test_focus"] *= 0.9
                self.policy_weights["feature_focus"] *= 0.9
                self.policy_weights["refactor_focus"] *= 0.9
                self.policy_weights["documentation_focus"] *= 0.9
    
    def get_sprint_focus(self) -> str:
        """Get the focus area for the next sprint."""
        weights = list(self.policy_weights.values())
        focus_areas = list(self.policy_weights.keys())
        
        # Sample based on weights
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(focus_areas)
        
        r = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for i, weight in enumerate(weights):
            cumulative_weight += weight
            if r <= cumulative_weight:
                return focus_areas[i]
        
        return focus_areas[-1]


class RewardCalculator:
    """Calculate rewards for RL training."""
    
    def __init__(self):
        self.baseline_metrics = None
    
    def set_baseline(self, metrics: Dict) -> None:
        """Set baseline metrics for reward calculation."""
        self.baseline_metrics = metrics.copy()
    
    def calculate_reward(self, current_metrics: Dict, action: str) -> float:
        """Calculate reward based on current metrics and action taken."""
        if self.baseline_metrics is None:
            self.baseline_metrics = current_metrics.copy()
            return 0.0
        
        reward = 0.0
        
        # Test pass rate improvement
        current_pass_rate = current_metrics.get("test_pass_rate", 0.0)
        baseline_pass_rate = self.baseline_metrics.get("test_pass_rate", 0.0)
        pass_rate_improvement = current_pass_rate - baseline_pass_rate
        reward += pass_rate_improvement * 10.0
        
        # Coverage improvement
        current_coverage = current_metrics.get("test_coverage", 0.0)
        baseline_coverage = self.baseline_metrics.get("test_coverage", 0.0)
        coverage_improvement = current_coverage - baseline_coverage
        reward += coverage_improvement * 5.0
        
        # Code quality improvements
        current_complexity = current_metrics.get("code_complexity", 1.0)
        baseline_complexity = self.baseline_metrics.get("code_complexity", 1.0)
        complexity_improvement = baseline_complexity - current_complexity  # Lower is better
        reward += complexity_improvement * 2.0
        
        # Dependency reduction
        current_deps = current_metrics.get("dependency_count", 0)
        baseline_deps = self.baseline_metrics.get("dependency_count", 0)
        dep_reduction = baseline_deps - current_deps
        reward += dep_reduction * 0.5
        
        # Action-specific rewards
        action_rewards = {
            "add_tests": 1.0 if current_pass_rate > baseline_pass_rate else -0.5,
            "refactor_code": 1.0 if current_complexity < baseline_complexity else -0.5,
            "improve_docs": 0.5,  # Always positive for docs
            "split_module": 1.0 if current_complexity < baseline_complexity else -0.5,
            "reduce_dependencies": 1.0 if current_deps < baseline_deps else -0.5,
            "optimize_performance": 0.5,  # Neutral reward
            "fix_bugs": 2.0 if current_pass_rate > baseline_pass_rate else -1.0,
            "add_features": 0.5  # Neutral reward
        }
        
        reward += action_rewards.get(action, 0.0)
        
        # Penalize for breaking things
        if current_pass_rate < baseline_pass_rate - 0.1:
            reward -= 5.0
        
        return reward


class RLModule:
    """Main RL module coordinating inner and outer loop learning."""
    
    def __init__(self, config: RLConfig, rl_data_path: Path):
        self.config = config
        self.rl_data_path = rl_data_path
        self.rl_data_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.state_space = StateSpace(config)
        self.action_space = ActionSpace()
        self.q_agent = QLearningAgent(config, self.state_space, self.action_space)
        self.outer_policy = OuterLoopPolicy(config)
        self.reward_calculator = RewardCalculator()
        
        # Load existing Q-table if available
        q_table_path = self.rl_data_path / "q_table.json"
        if q_table_path.exists():
            self.q_agent.load(q_table_path)
    
    def select_action(self, metrics: Dict) -> str:
        """Select next action based on current state."""
        # Discretize current state
        state = self.state_space.discretize_state(
            test_pass_rate=metrics.get("test_pass_rate", 0.0),
            coverage=metrics.get("test_coverage", 0.0),
            complexity=metrics.get("code_complexity", 0.5),
            dependency_count=metrics.get("dependency_count", 0)
        )
        
        return self.q_agent.select_action(state)
    
    def update_inner_loop(self, state_metrics: Dict, action: str, 
                         next_state_metrics: Dict) -> float:
        """Update inner loop policy and return reward."""
        # Calculate reward
        reward = self.reward_calculator.calculate_reward(next_state_metrics, action)
        
        # Discretize states
        current_state = self.state_space.discretize_state(
            test_pass_rate=state_metrics.get("test_pass_rate", 0.0),
            coverage=state_metrics.get("test_coverage", 0.0),
            complexity=state_metrics.get("code_complexity", 0.5),
            dependency_count=state_metrics.get("dependency_count", 0)
        )
        
        next_state = self.state_space.discretize_state(
            test_pass_rate=next_state_metrics.get("test_pass_rate", 0.0),
            coverage=next_state_metrics.get("test_coverage", 0.0),
            complexity=next_state_metrics.get("code_complexity", 0.5),
            dependency_count=next_state_metrics.get("dependency_count", 0)
        )
        
        # Update Q-table
        self.q_agent.update(current_state, action, reward, next_state)
        
        return reward
    
    def update_outer_loop(self, sprint_reward: float, sprint_metrics: Dict) -> None:
        """Update outer loop policy."""
        self.outer_policy.update_policy(sprint_reward, sprint_metrics)
    
    def get_sprint_focus(self) -> str:
        """Get focus area for next sprint."""
        return self.outer_policy.get_sprint_focus()
    
    def save_state(self) -> None:
        """Save RL state to disk."""
        # Save Q-table
        q_table_path = self.rl_data_path / "q_table.json"
        self.q_agent.save(q_table_path)
        
        # Save outer loop policy
        policy_path = self.rl_data_path / "outer_policy.json"
        policy_data = {
            "sprint_rewards": self.outer_policy.sprint_rewards,
            "policy_weights": self.outer_policy.policy_weights
        }
        
        with open(policy_path, 'w') as f:
            json.dump(policy_data, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get RL statistics."""
        return {
            "q_table_shape": self.q_agent.q_table.shape,
            "epsilon": self.q_agent.epsilon,
            "sprint_rewards": self.outer_policy.sprint_rewards,
            "policy_weights": self.outer_policy.policy_weights
        }
