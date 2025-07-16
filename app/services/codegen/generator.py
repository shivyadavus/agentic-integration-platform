"""
Code generator for the agentic integration platform.

This module provides AI-powered code generation from natural language
specifications, with support for multiple programming languages and patterns.
"""

import ast
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.ai.base import AIService, AIMessage, AIModelConfig
from app.services.ai.factory import AIServiceFactory
from app.services.ai.prompt_manager import prompt_manager
from app.services.knowledge.pattern_service import PatternService
from app.services.knowledge.entity_service import EntityService
from app.models.integration import Integration, IntegrationType
from app.models.knowledge import Pattern
from app.core.exceptions import CodeGenerationError, ValidationError
from app.core.logging import LoggerMixin


class CodeGenerator(LoggerMixin):
    """
    AI-powered code generator for integration development.
    
    Generates production-ready integration code from natural language
    specifications using AI models and learned patterns.
    """
    
    def __init__(
        self,
        ai_service: Optional[AIService] = None,
        pattern_service: Optional[PatternService] = None,
        entity_service: Optional[EntityService] = None
    ):
        """
        Initialize code generator.
        
        Args:
            ai_service: AI service for code generation
            pattern_service: Pattern service for retrieving patterns
            entity_service: Entity service for context
        """
        self.ai_service = ai_service or AIServiceFactory.get_default_service()
        self.pattern_service = pattern_service or PatternService()
        self.entity_service = entity_service or EntityService()
    
    async def generate_integration_code(
        self,
        specification: str,
        integration_type: IntegrationType,
        source_system: Optional[Dict[str, Any]] = None,
        target_system: Optional[Dict[str, Any]] = None,
        data_mappings: Optional[List[Dict[str, Any]]] = None,
        language: str = "python",
        use_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        Generate integration code from specification.
        
        Args:
            specification: Natural language specification
            integration_type: Type of integration
            source_system: Source system information
            target_system: Target system information
            data_mappings: Data field mappings
            language: Programming language
            use_patterns: Whether to use existing patterns
            
        Returns:
            Dict[str, Any]: Generated code and metadata
        """
        try:
            self.logger.info(
                "Starting code generation",
                integration_type=integration_type.value,
                language=language,
                use_patterns=use_patterns
            )
            
            # Find applicable patterns if enabled
            applicable_patterns = []
            if use_patterns and source_system and target_system:
                # TODO: Implement pattern search with database session
                pass
            
            # Prepare generation context
            context = await self._prepare_generation_context(
                specification=specification,
                integration_type=integration_type,
                source_system=source_system,
                target_system=target_system,
                data_mappings=data_mappings,
                patterns=applicable_patterns
            )
            
            # Generate code using AI
            generated_code = await self._generate_code_with_ai(
                specification=specification,
                context=context,
                language=language
            )
            
            # Validate generated code
            validation_result = await self._validate_generated_code(
                code=generated_code,
                language=language
            )
            
            # Extract metadata from generated code
            metadata = await self._extract_code_metadata(
                code=generated_code,
                language=language
            )
            
            result = {
                "code": generated_code,
                "language": language,
                "validation": validation_result,
                "metadata": metadata,
                "patterns_used": [p.get("id") for p in applicable_patterns],
                "generation_timestamp": datetime.utcnow().isoformat(),
                "ai_model": self.ai_service.default_model,
                "ai_provider": self.ai_service.provider_name,
            }
            
            self.logger.info(
                "Code generation completed",
                code_length=len(generated_code),
                validation_passed=validation_result.get("valid", False),
                patterns_used=len(applicable_patterns)
            )
            
            return result
            
        except Exception as e:
            raise CodeGenerationError(
                f"Code generation failed: {str(e)}",
                generation_stage="generate_integration_code",
                context={
                    "specification": specification[:200] + "..." if len(specification) > 200 else specification,
                    "integration_type": integration_type.value,
                    "language": language
                }
            )
    
    async def _prepare_generation_context(
        self,
        specification: str,
        integration_type: IntegrationType,
        source_system: Optional[Dict[str, Any]],
        target_system: Optional[Dict[str, Any]],
        data_mappings: Optional[List[Dict[str, Any]]],
        patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare context for code generation.
        
        Args:
            specification: Natural language specification
            integration_type: Integration type
            source_system: Source system info
            target_system: Target system info
            data_mappings: Data mappings
            patterns: Applicable patterns
            
        Returns:
            Dict[str, Any]: Generation context
        """
        context = {
            "specification": specification,
            "integration_type": integration_type.value,
            "source_system": source_system or {},
            "target_system": target_system or {},
            "data_mappings": data_mappings or [],
            "patterns": patterns,
            "requirements": {
                "async_support": True,
                "error_handling": True,
                "logging": True,
                "type_hints": True,
                "docstrings": True,
                "testing": True,
                "validation": True,
            }
        }
        
        # Add pattern-specific context
        if patterns:
            context["pattern_examples"] = []
            for pattern in patterns:
                if "code_template" in pattern:
                    context["pattern_examples"].append({
                        "name": pattern.get("name"),
                        "type": pattern.get("pattern_type"),
                        "template": pattern.get("code_template"),
                        "success_rate": pattern.get("success_rate", 0)
                    })
        
        return context
    
    async def _generate_code_with_ai(
        self,
        specification: str,
        context: Dict[str, Any],
        language: str
    ) -> str:
        """
        Generate code using AI service.
        
        Args:
            specification: Natural language specification
            context: Generation context
            language: Programming language
            
        Returns:
            str: Generated code
        """
        # Use appropriate prompt template
        prompt_id = f"{language}_code_generation"
        
        try:
            prompt_text = prompt_manager.render_prompt(
                prompt_id,
                {
                    "specification": specification,
                    "source_system": context.get("source_system"),
                    "target_system": context.get("target_system"),
                    "data_mappings": context.get("data_mappings"),
                    "patterns": context.get("pattern_examples", []),
                    "requirements": context.get("requirements", {})
                }
            )
        except Exception:
            # Fallback to direct generation if prompt not found
            prompt_text = self._create_fallback_prompt(specification, context, language)
        
        # Prepare AI messages
        messages = [
            AIMessage(role="user", content=prompt_text)
        ]
        
        # Configure AI model for code generation
        config = AIModelConfig(
            model=self.ai_service.default_model,
            temperature=0.1,  # Low temperature for deterministic code
            max_tokens=4096
        )
        
        # Generate response
        response = await self.ai_service.generate_response(messages, config)
        
        # Extract code from response
        generated_code = self._extract_code_from_response(response.content, language)
        
        return generated_code
    
    def _create_fallback_prompt(
        self,
        specification: str,
        context: Dict[str, Any],
        language: str
    ) -> str:
        """Create fallback prompt for code generation."""
        prompt = f"""Generate production-ready {language} code for the following integration:

**Specification:**
{specification}

**Requirements:**
- Use async/await for all I/O operations
- Include comprehensive error handling
- Add detailed logging with structured logging
- Include type hints for all functions
- Add docstrings following Google style
- Implement retry logic with exponential backoff
- Include input validation using Pydantic models
- Follow SOLID principles and best practices

**Integration Type:** {context.get('integration_type', 'unknown')}

Generate complete, working code that can be deployed to production."""
        
        if context.get("source_system"):
            prompt += f"\n\n**Source System:** {context['source_system']}"
        
        if context.get("target_system"):
            prompt += f"\n\n**Target System:** {context['target_system']}"
        
        if context.get("data_mappings"):
            prompt += f"\n\n**Data Mappings:** {context['data_mappings']}"
        
        return prompt
    
    def _extract_code_from_response(self, response_content: str, language: str) -> str:
        """
        Extract code from AI response.
        
        Args:
            response_content: AI response content
            language: Programming language
            
        Returns:
            str: Extracted code
        """
        # Look for code blocks
        import re
        
        # Try to find code blocks with language specification
        pattern = rf"```{language}\n(.*?)\n```"
        matches = re.findall(pattern, response_content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Try to find generic code blocks
        pattern = r"```\n(.*?)\n```"
        matches = re.findall(pattern, response_content, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks found, return the entire response
        return response_content.strip()
    
    async def _validate_generated_code(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Validate generated code.
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            Dict[str, Any]: Validation results
        """
        validation_result = {
            "valid": False,
            "syntax_valid": False,
            "issues": [],
            "score": 0.0
        }
        
        try:
            if language == "python":
                # Check Python syntax
                try:
                    ast.parse(code)
                    validation_result["syntax_valid"] = True
                except SyntaxError as e:
                    validation_result["issues"].append({
                        "type": "syntax_error",
                        "message": str(e),
                        "line": getattr(e, "lineno", None)
                    })
            
            # Basic code quality checks
            quality_score = self._assess_code_quality(code, language)
            validation_result["score"] = quality_score
            
            # Consider valid if syntax is correct and quality is reasonable
            validation_result["valid"] = (
                validation_result["syntax_valid"] and
                quality_score >= 0.6
            )
            
        except Exception as e:
            validation_result["issues"].append({
                "type": "validation_error",
                "message": str(e)
            })
        
        return validation_result
    
    def _assess_code_quality(self, code: str, language: str) -> float:
        """
        Assess code quality with basic heuristics.
        
        Args:
            code: Code to assess
            language: Programming language
            
        Returns:
            float: Quality score (0.0 to 1.0)
        """
        if not code.strip():
            return 0.0
        
        score = 0.0
        checks = 0
        
        # Check for async/await usage
        if "async def" in code or "await " in code:
            score += 1
        checks += 1
        
        # Check for error handling
        if "try:" in code and "except" in code:
            score += 1
        checks += 1

        # Check for logging
        if "logging" in code or "logger" in code:
            score += 1
        checks += 1

        # Check for type hints
        if "->" in code and ":" in code:
            score += 1
        checks += 1

        # Check for docstrings
        if '"""' in code or "'''" in code:
            score += 1
        checks += 1

        # Check for imports
        if "import " in code or "from " in code:
            score += 1
        checks += 1

        # Check for classes or functions
        if "def " in code or "class " in code:
            score += 1
        checks += 1
        
        return score / max(checks, 1)
    
    async def _extract_code_metadata(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Extract metadata from generated code.
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            Dict[str, Any]: Code metadata
        """
        metadata = {
            "language": language,
            "line_count": len(code.split("\n")),
            "character_count": len(code),
            "functions": [],
            "classes": [],
            "imports": [],
            "dependencies": []
        }
        
        if language == "python":
            try:
                tree = ast.parse(code)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        metadata["functions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "is_async": isinstance(node, ast.AsyncFunctionDef),
                            "args": [arg.arg for arg in node.args.args]
                        })
                    
                    elif isinstance(node, ast.ClassDef):
                        metadata["classes"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "methods": [
                                n.name for n in node.body
                                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                            ]
                        })
                    
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                metadata["imports"].append(alias.name)
                        else:
                            module = node.module or ""
                            for alias in node.names:
                                metadata["imports"].append(f"{module}.{alias.name}")
            
            except Exception as e:
                self.logger.warning(f"Failed to extract Python metadata: {e}")
        
        # Extract dependencies from imports
        metadata["dependencies"] = list(set([
            imp.split(".")[0] for imp in metadata["imports"]
            if not imp.startswith((".", "app."))
        ]))
        
        return metadata
    
    async def refine_code(
        self,
        code: str,
        feedback: str,
        language: str = "python"
    ) -> str:
        """
        Refine generated code based on feedback.
        
        Args:
            code: Original code
            feedback: Feedback for improvement
            language: Programming language
            
        Returns:
            str: Refined code
        """
        prompt = f"""Improve the following {language} code based on the feedback:

**Original Code:**
```{language}
{code}
```

**Feedback:**
{feedback}

**Requirements:**
- Maintain the original functionality
- Address all feedback points
- Ensure code quality and best practices
- Keep the code production-ready

Generate the improved code:"""
        
        messages = [AIMessage(role="user", content=prompt)]
        
        config = AIModelConfig(
            model=self.ai_service.default_model,
            temperature=0.1,
            max_tokens=4096
        )
        
        response = await self.ai_service.generate_response(messages, config)
        refined_code = self._extract_code_from_response(response.content, language)
        
        self.logger.info("Code refinement completed", original_length=len(code), refined_length=len(refined_code))
        
        return refined_code
