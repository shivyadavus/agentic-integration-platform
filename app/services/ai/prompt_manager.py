"""
Prompt management system for the agentic integration platform.

This module provides centralized management of AI prompts with templating,
versioning, and optimization capabilities.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from jinja2 import Environment, FileSystemLoader, Template

from app.core.logging import get_logger
from app.core.exceptions import ValidationError

logger = get_logger(__name__)


class PromptType(Enum):
    """Types of prompts in the system."""
    
    SYSTEM = "system"
    INTEGRATION_ANALYSIS = "integration_analysis"
    CODE_GENERATION = "code_generation"
    VALIDATION = "validation"
    ERROR_ANALYSIS = "error_analysis"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"


@dataclass
class PromptTemplate:
    """
    Represents a prompt template with metadata.
    """
    
    id: str
    name: str
    type: PromptType
    template: str
    description: str
    version: str = "1.0"
    variables: List[str] = None
    examples: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []
        if self.examples is None:
            self.examples = []
        if self.metadata is None:
            self.metadata = {}


class PromptManager:
    """
    Manages AI prompts with templating and versioning capabilities.
    
    Provides centralized storage, retrieval, and rendering of prompts
    used throughout the agentic integration platform.
    """
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        """
        Initialize the prompt manager.
        
        Args:
            prompts_dir: Directory containing prompt templates
        """
        self.prompts_dir = prompts_dir or Path(__file__).parent / "prompts"
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Jinja2 environment for template rendering
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.prompts_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        )
        
        # In-memory prompt storage
        self._prompts: Dict[str, PromptTemplate] = {}
        
        # Load default prompts
        self._load_default_prompts()
    
    def _load_default_prompts(self) -> None:
        """Load default system prompts."""
        
        default_prompts = [
            PromptTemplate(
                id="system_integration_architect",
                name="Integration Architect System Prompt",
                type=PromptType.SYSTEM,
                template="""You are an expert integration architect specializing in enterprise software integrations.

Your expertise includes:
- API design and integration patterns
- Data transformation and mapping
- Error handling and resilience
- Security and authentication
- Performance optimization
- Code generation in Python, JavaScript, and other languages

You help users create production-ready integrations by:
1. Analyzing natural language requirements
2. Designing appropriate integration architectures
3. Generating clean, maintainable code
4. Implementing proper error handling and logging
5. Ensuring security best practices

Always provide detailed explanations and consider edge cases in your solutions.""",
                description="System prompt for integration architecture tasks",
                variables=[],
            ),
            
            PromptTemplate(
                id="integration_analysis",
                name="Integration Requirements Analysis",
                type=PromptType.INTEGRATION_ANALYSIS,
                template="""Analyze the following integration requirement and provide a structured analysis:

**Requirement:**
{{ requirement }}

{% if source_system %}
**Source System:**
{{ source_system | tojson }}
{% endif %}

{% if target_system %}
**Target System:**
{{ target_system | tojson }}
{% endif %}

Please provide your analysis in the following JSON format:
{
  "integration_type": "sync|async|webhook|batch|realtime|api_proxy|etl|event_driven",
  "data_flow": "unidirectional|bidirectional",
  "complexity": "low|medium|high",
  "estimated_effort_hours": number,
  "key_challenges": ["challenge1", "challenge2"],
  "recommended_approach": "detailed approach description",
  "data_transformations": [
    {
      "source_field": "field_name",
      "target_field": "field_name", 
      "transformation": "transformation_logic"
    }
  ],
  "error_handling_requirements": ["requirement1", "requirement2"],
  "security_considerations": ["consideration1", "consideration2"],
  "performance_requirements": {
    "throughput": "requests_per_second",
    "latency": "max_response_time_ms"
  },
  "dependencies": ["dependency1", "dependency2"],
  "testing_strategy": "testing approach description"
}""",
                description="Analyzes integration requirements and provides structured output",
                variables=["requirement", "source_system", "target_system"],
                examples=[
                    {
                        "requirement": "Sync customer data from Salesforce to ERP when accounts are created",
                        "source_system": {"name": "Salesforce", "type": "crm"},
                        "target_system": {"name": "SAP ERP", "type": "erp"}
                    }
                ]
            ),
            
            PromptTemplate(
                id="python_code_generation",
                name="Python Integration Code Generation",
                type=PromptType.CODE_GENERATION,
                template="""Generate production-ready Python code for the following integration:

**Specification:**
{{ specification }}

**Requirements:**
- Use async/await for all I/O operations
- Include comprehensive error handling with custom exceptions
- Add detailed logging with structured logging
- Include type hints for all functions and variables
- Add docstrings following Google style
- Implement retry logic with exponential backoff
- Include input validation using Pydantic models
- Use dependency injection patterns
- Follow SOLID principles

{% if source_system %}
**Source System Configuration:**
{{ source_system | tojson }}
{% endif %}

{% if target_system %}
**Target System Configuration:**
{{ target_system | tojson }}
{% endif %}

{% if data_mappings %}
**Data Mappings:**
{{ data_mappings | tojson }}
{% endif %}

Generate the complete implementation including:
1. Data models (Pydantic)
2. Service classes
3. Error handling
4. Configuration management
5. Main integration function
6. Unit tests

Ensure the code is modular, testable, and follows Python best practices.""",
                description="Generates Python integration code from specifications",
                variables=["specification", "source_system", "target_system", "data_mappings"],
            ),
            
            PromptTemplate(
                id="code_validation",
                name="Integration Code Validation",
                type=PromptType.VALIDATION,
                template="""Review and validate the following integration code:

**Code:**
```python
{{ code }}
```

**Validation Criteria:**
- Code quality and best practices
- Error handling completeness
- Security vulnerabilities
- Performance considerations
- Maintainability
- Test coverage
- Documentation quality

Provide your validation results in JSON format:
{
  "overall_score": number_out_of_10,
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "security|performance|maintainability|correctness|style",
      "description": "issue description",
      "line_number": number_or_null,
      "suggestion": "how to fix"
    }
  ],
  "strengths": ["strength1", "strength2"],
  "recommendations": ["recommendation1", "recommendation2"],
  "security_score": number_out_of_10,
  "performance_score": number_out_of_10,
  "maintainability_score": number_out_of_10
}""",
                description="Validates generated integration code for quality and security",
                variables=["code"],
            ),
            
            PromptTemplate(
                id="error_analysis",
                name="Integration Error Analysis",
                type=PromptType.ERROR_ANALYSIS,
                template="""Analyze the following integration error and provide solutions:

**Error Details:**
{{ error_message }}

{% if stack_trace %}
**Stack Trace:**
{{ stack_trace }}
{% endif %}

{% if integration_code %}
**Integration Code:**
```python
{{ integration_code }}
```
{% endif %}

{% if context %}
**Additional Context:**
{{ context | tojson }}
{% endif %}

Provide your analysis in JSON format:
{
  "error_type": "authentication|network|data_validation|business_logic|configuration|timeout|rate_limit|other",
  "root_cause": "detailed root cause analysis",
  "severity": "critical|high|medium|low",
  "impact": "description of impact",
  "immediate_actions": ["action1", "action2"],
  "permanent_solutions": [
    {
      "solution": "solution description",
      "implementation": "how to implement",
      "effort": "low|medium|high"
    }
  ],
  "prevention_measures": ["measure1", "measure2"],
  "monitoring_recommendations": ["recommendation1", "recommendation2"]
}""",
                description="Analyzes integration errors and provides solutions",
                variables=["error_message", "stack_trace", "integration_code", "context"],
            )
        ]
        
        for prompt in default_prompts:
            self._prompts[prompt.id] = prompt
        
        logger.info(f"Loaded {len(default_prompts)} default prompts")
    
    def get_prompt(self, prompt_id: str) -> Optional[PromptTemplate]:
        """
        Get a prompt template by ID.
        
        Args:
            prompt_id: Unique prompt identifier
            
        Returns:
            PromptTemplate: The prompt template or None if not found
        """
        return self._prompts.get(prompt_id)
    
    def list_prompts(self, prompt_type: Optional[PromptType] = None) -> List[PromptTemplate]:
        """
        List all available prompts, optionally filtered by type.
        
        Args:
            prompt_type: Optional filter by prompt type
            
        Returns:
            List[PromptTemplate]: List of matching prompts
        """
        prompts = list(self._prompts.values())
        
        if prompt_type:
            prompts = [p for p in prompts if p.type == prompt_type]
        
        return prompts
    
    def render_prompt(
        self,
        prompt_id: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a prompt template with variables.
        
        Args:
            prompt_id: Unique prompt identifier
            variables: Variables to substitute in the template
            
        Returns:
            str: Rendered prompt text
            
        Raises:
            ValidationError: If prompt not found or rendering fails
        """
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            raise ValidationError(f"Prompt not found: {prompt_id}")
        
        try:
            template = Template(prompt.template)
            return template.render(variables or {})
            
        except Exception as e:
            raise ValidationError(
                f"Failed to render prompt {prompt_id}: {str(e)}",
                context={"variables": variables}
            )
    
    def add_prompt(self, prompt: PromptTemplate) -> None:
        """
        Add a new prompt template.
        
        Args:
            prompt: Prompt template to add
        """
        self._prompts[prompt.id] = prompt
        logger.info(f"Added prompt: {prompt.id}")
    
    def update_prompt(self, prompt_id: str, prompt: PromptTemplate) -> None:
        """
        Update an existing prompt template.
        
        Args:
            prompt_id: Prompt ID to update
            prompt: Updated prompt template
        """
        if prompt_id not in self._prompts:
            raise ValidationError(f"Prompt not found: {prompt_id}")
        
        self._prompts[prompt_id] = prompt
        logger.info(f"Updated prompt: {prompt_id}")
    
    def delete_prompt(self, prompt_id: str) -> None:
        """
        Delete a prompt template.
        
        Args:
            prompt_id: Prompt ID to delete
        """
        if prompt_id not in self._prompts:
            raise ValidationError(f"Prompt not found: {prompt_id}")
        
        del self._prompts[prompt_id]
        logger.info(f"Deleted prompt: {prompt_id}")
    
    def save_prompts_to_file(self, file_path: Path) -> None:
        """
        Save all prompts to a JSON file.
        
        Args:
            file_path: Path to save the prompts file
        """
        prompts_data = []
        
        for prompt in self._prompts.values():
            prompt_dict = asdict(prompt)
            prompt_dict["type"] = prompt.type.value  # Convert enum to string
            prompts_data.append(prompt_dict)
        
        with open(file_path, "w") as f:
            json.dump(prompts_data, f, indent=2)
        
        logger.info(f"Saved {len(prompts_data)} prompts to {file_path}")
    
    def load_prompts_from_file(self, file_path: Path) -> None:
        """
        Load prompts from a JSON file.
        
        Args:
            file_path: Path to the prompts file
        """
        with open(file_path, "r") as f:
            prompts_data = json.load(f)
        
        for prompt_dict in prompts_data:
            prompt_dict["type"] = PromptType(prompt_dict["type"])  # Convert string to enum
            prompt = PromptTemplate(**prompt_dict)
            self._prompts[prompt.id] = prompt
        
        logger.info(f"Loaded {len(prompts_data)} prompts from {file_path}")


# Global prompt manager instance
prompt_manager = PromptManager()
