"""
CLI commands for custom method management in Agent Hub.

Provides command-line interface for injecting, managing, and validating custom methods.
"""

import click
import json
import logging
from pathlib import Path
from typing import Optional

from agentmanager.core.custom_method_manager import CustomMethodManager
from agentmanager.core.exceptions import (
    MethodValidationError, MethodSecurityError, MethodInjectionError,
    MethodNotFoundError, MethodLanguageNotSupportedError
)

logger = logging.getLogger(__name__)


@click.group()
def method():
    """Manage custom methods for agents."""
    pass


@method.command()
@click.argument('agent_path', type=str)
@click.argument('method_name', type=str)
@click.argument('implementation_file', type=click.Path(exists=True, path_type=Path))
@click.option('--language', '-l', default='python', 
              type=click.Choice(['python', 'javascript', 'shell', 'bash']),
              help='Programming language of the implementation')
@click.option('--security-level', '-s', default='medium',
              type=click.Choice(['low', 'medium', 'high']),
              help='Security level for method validation')
@click.option('--validate-only', is_flag=True,
              help='Only validate the method without injecting it')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output with detailed validation results')
def inject(agent_path: str, method_name: str, implementation_file: Path, 
           language: str, security_level: str, validate_only: bool, verbose: bool):
    """
    Inject a custom method for an agent.
    
    AGENT_PATH: Path to the agent (e.g., "agentplug/coding-agent")
    METHOD_NAME: Name of the method to inject
    IMPLEMENTATION_FILE: File containing the method implementation
    """
    try:
        # Initialize custom method manager
        manager = CustomMethodManager(security_level=security_level)
        
        # Read implementation file
        with open(implementation_file, 'r', encoding='utf-8') as f:
            implementation = f.read()
        
        # Validate method name
        if not method_name.isidentifier():
            raise click.BadParameter(f"Invalid method name: {method_name}. Must be a valid Python identifier.")
        
        click.echo(f"🔍 Validating custom method '{method_name}' for agent '{agent_path}'...")
        
        # Validate the method
        validation_result = manager.method_validator.validate_method(implementation, language)
        
        if verbose:
            click.echo(f"\n📊 Validation Results:")
            click.echo(f"   Valid: {'✅ Yes' if validation_result.is_valid else '❌ No'}")
            click.echo(f"   Security Score: {validation_result.security_score}/100")
            click.echo(f"   Errors: {len(validation_result.errors)}")
            click.echo(f"   Warnings: {len(validation_result.warnings)}")
            
            if validation_result.errors:
                click.echo(f"\n❌ Validation Errors:")
                for error in validation_result.errors:
                    click.echo(f"   • {error}")
            
            if validation_result.warnings:
                click.echo(f"\n⚠️  Validation Warnings:")
                for warning in validation_result.warnings:
                    click.echo(f"   • {warning}")
        
        if not validation_result.is_valid:
            click.echo(f"\n❌ Method validation failed!")
            click.echo(f"   Errors: {len(validation_result.errors)}")
            click.echo(f"   Warnings: {len(validation_result.warnings)}")
            
            if validation_result.errors:
                click.echo(f"\nPlease fix the following errors:")
                for error in validation_result.errors:
                    click.echo(f"   • {error}")
            
            click.echo(f"\n💡 Suggestions for improvement:")
            suggestions = manager.method_validator.suggest_improvements(validation_result)
            for suggestion in suggestions:
                click.echo(f"   • {suggestion}")
            
            raise click.Abort()
        
        if validate_only:
            click.echo(f"\n✅ Method validation passed successfully!")
            click.echo(f"   Security Score: {validation_result.security_score}/100")
            if validation_result.warnings:
                click.echo(f"   Warnings: {len(validation_result.warnings)}")
            return
        
        # Inject the method
        click.echo(f"\n🚀 Injecting custom method '{method_name}'...")
        manager.inject_method(agent_path, method_name, implementation, language)
        
        click.echo(f"\n✅ Successfully injected custom method '{method_name}' for agent '{agent_path}'!")
        click.echo(f"   Language: {language}")
        click.echo(f"   Security Level: {security_level}")
        click.echo(f"   Security Score: {validation_result.security_score}/100")
        
        # Show method info
        method_info = manager.get_method_info(agent_path, method_name)
        if method_info:
            click.echo(f"\n📋 Method Information:")
            click.echo(f"   Name: {method_info.name}")
            click.echo(f"   Language: {method_info.language}")
            click.echo(f"   Injected: {method_info.injected_at}")
            click.echo(f"   Size: {method_info.metadata.get('size_bytes', 'unknown')} bytes")
            
            if method_info.metadata.get('parameters'):
                click.echo(f"   Parameters: {', '.join(method_info.metadata['parameters'])}")
        
    except MethodValidationError as e:
        click.echo(f"\n❌ Method validation failed: {e}")
        raise click.Abort()
    except MethodSecurityError as e:
        click.echo(f"\n🚨 Security validation failed: {e}")
        raise click.Abort()
    except MethodLanguageNotSupportedError as e:
        click.echo(f"\n❌ Language not supported: {e}")
        raise click.Abort()
    except Exception as e:
        click.echo(f"\n💥 Unexpected error: {e}")
        if verbose:
            import traceback
            click.echo(f"\n{traceback.format_exc()}")
        raise click.Abort()


@method.command()
@click.argument('agent_path', type=str)
@click.argument('method_name', type=str)
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output with detailed information')
def remove(agent_path: str, method_name: str, verbose: bool):
    """
    Remove a custom method from an agent.
    
    AGENT_PATH: Path to the agent (e.g., "agentplug/coding-agent")
    METHOD_NAME: Name of the method to remove
    """
    try:
        manager = CustomMethodManager()
        
        # Check if method exists
        if not manager.validate_method_exists(agent_path, method_name):
            click.echo(f"❌ Custom method '{method_name}' not found for agent '{agent_path}'")
            raise click.Abort()
        
        # Get method info before removal
        method_info = manager.get_method_info(agent_path, method_name)
        
        click.echo(f"🗑️  Removing custom method '{method_name}' from agent '{agent_path}'...")
        
        # Remove the method
        manager.remove_method(agent_path, method_name)
        
        click.echo(f"\n✅ Successfully removed custom method '{method_name}' from agent '{agent_path}'!")
        
        if verbose and method_info:
            click.echo(f"\n📋 Removed Method Information:")
            click.echo(f"   Name: {method_info.name}")
            click.echo(f"   Language: {method_info.language}")
            click.echo(f"   Injected: {method_info.injected_at}")
            click.echo(f"   Size: {method_info.metadata.get('size_bytes', 'unknown')} bytes")
        
    except Exception as e:
        click.echo(f"\n💥 Error removing method: {e}")
        raise click.Abort()


@method.command()
@click.argument('agent_path', type=str)
@click.option('--format', '-f', default='table',
              type=click.Choice(['table', 'json', 'yaml']),
              help='Output format')
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output with detailed information')
def list(agent_path: str, format: str, verbose: bool):
    """
    List custom methods for an agent.
    
    AGENT_PATH: Path to the agent (e.g., "agentplug/coding-agent")
    """
    try:
        manager = CustomMethodManager()
        
        # Get custom methods
        custom_methods = manager.list_methods(agent_path)
        
        if not custom_methods:
            click.echo(f"📭 No custom methods found for agent '{agent_path}'")
            return
        
        click.echo(f"🔧 Custom Methods for Agent '{agent_path}':")
        click.echo(f"   Total: {len(custom_methods)} methods")
        
        if format == 'json':
            # JSON output
            output_data = {}
            for method_name, method_info in custom_methods.items():
                output_data[method_name] = {
                    "language": method_info.language,
                    "injected_at": method_info.injected_at,
                    "security_score": getattr(method_info, 'security_score', 'unknown'),
                    "metadata": method_info.metadata
                }
            click.echo(json.dumps(output_data, indent=2, default=str))
            
        elif format == 'yaml':
            # YAML output
            try:
                import yaml
                output_data = {}
                for method_name, method_info in custom_methods.items():
                    output_data[method_name] = {
                        "language": method_info.language,
                        "injected_at": method_info.injected_at,
                        "security_score": getattr(method_info, 'security_score', 'unknown'),
                        "metadata": method_info.metadata
                    }
                click.echo(yaml.dump(output_data, default_flow_style=False, default_representer=str))
            except ImportError:
                click.echo("❌ YAML output requires PyYAML package. Install with: pip install PyYAML")
                raise click.Abort()
                
        else:
            # Table output (default)
            click.echo(f"\n{'Method Name':<20} {'Language':<12} {'Security':<10} {'Size':<10} {'Injected':<20}")
            click.echo("-" * 80)
            
            for method_name, method_info in custom_methods.items():
                security_score = getattr(method_info, 'security_score', 'unknown')
                size_bytes = method_info.metadata.get('size_bytes', 'unknown')
                if isinstance(size_bytes, int):
                    size_str = f"{size_bytes} B"
                else:
                    size_str = str(size_bytes)
                
                click.echo(f"{method_name:<20} {method_info.language:<12} {security_score:<10} {size_str:<10} {method_info.injected_at:<20}")
            
            if verbose:
                click.echo(f"\n📋 Detailed Information:")
                for method_name, method_info in custom_methods.items():
                    click.echo(f"\n🔧 {method_name}:")
                    click.echo(f"   Language: {method_info.language}")
                    click.echo(f"   Injected: {method_info.injected_at}")
                    click.echo(f"   Security Score: {getattr(method_info, 'security_score', 'unknown')}")
                    click.echo(f"   Size: {method_info.metadata.get('size_bytes', 'unknown')} bytes")
                    
                    if method_info.metadata.get('parameters'):
                        click.echo(f"   Parameters: {', '.join(method_info.metadata['parameters'])}")
                    
                    if method_info.metadata.get('docstring'):
                        docstring = method_info.metadata['docstring'].strip()
                        if docstring:
                            click.echo(f"   Description: {docstring[:100]}{'...' if len(docstring) > 100 else ''}")
        
    except Exception as e:
        click.echo(f"\n💥 Error listing methods: {e}")
        raise click.Abort()


@method.command()
@click.argument('agent_path', type=str)
@click.argument('method_name', type=str)
@click.option('--verbose', '-v', is_flag=True,
              help='Verbose output with detailed information')
def info(agent_path: str, method_name: str, verbose: bool):
    """
    Get detailed information about a custom method.
    
    AGENT_PATH: Path to the agent (e.g., "agentplug/coding-agent")
    METHOD_NAME: Name of the method to inspect
    """
    try:
        manager = CustomMethodManager()
        
        # Check if method exists
        if not manager.validate_method_exists(agent_path, method_name):
            click.echo(f"❌ Custom method '{method_name}' not found for agent '{agent_path}'")
            raise click.Abort()
        
        # Get method info
        method_info = manager.get_method_info(agent_path, method_name)
        
        if not method_info:
            click.echo(f"❌ Could not retrieve information for method '{method_name}'")
            raise click.Abort()
        
        click.echo(f"🔍 Custom Method Information:")
        click.echo(f"   Name: {method_info.name}")
        click.echo(f"   Agent: {agent_path}")
        click.echo(f"   Language: {method_info.language}")
        click.echo(f"   Injected: {method_info.injected_at}")
        click.echo(f"   Security Level: {method_info.security_level}")
        click.echo(f"   Checksum: {method_info.checksum}")
        
        click.echo(f"\n📊 Metadata:")
        for key, value in method_info.metadata.items():
            click.echo(f"   {key}: {value}")
        
        if verbose:
            click.echo(f"\n💻 Implementation Preview:")
            implementation = method_info.implementation
            if len(implementation) > 500:
                preview = implementation[:500] + "..."
                click.echo(f"   (Showing first 500 characters)")
            else:
                preview = implementation
            
            click.echo(f"   {preview}")
        
    except Exception as e:
        click.echo(f"\n💥 Error getting method info: {e}")
        raise click.Abort()


@method.command()
@click.argument('agent_path', type=str)
@click.option('--max-age-hours', default=24, type=int,
              help='Maximum age in hours before cleanup')
@click.option('--dry-run', is_flag=True,
              help='Show what would be cleaned up without actually doing it')
def cleanup(agent_path: str, max_age_hours: int, dry_run: bool):
    """
    Clean up expired custom methods for an agent.
    
    AGENT_PATH: Path to the agent (e.g., "agentplug/coding-agent")
    """
    try:
        manager = CustomMethodManager()
        
        # Get current custom methods
        current_methods = manager.list_methods(agent_path)
        
        if not current_methods:
            click.echo(f"📭 No custom methods found for agent '{agent_path}'")
            return
        
        click.echo(f"🧹 Cleanup Analysis for Agent '{agent_path}':")
        click.echo(f"   Total methods: {len(current_methods)}")
        click.echo(f"   Max age: {max_age_hours} hours")
        
        # Analyze expired methods
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        expired_methods = []
        
        for method_name, method_info in current_methods.items():
            if current_time - method_info.injected_at > max_age_seconds:
                expired_methods.append((method_name, method_info))
        
        if not expired_methods:
            click.echo(f"   ✅ No expired methods found")
            return
        
        click.echo(f"   ⏰ Expired methods: {len(expired_methods)}")
        
        if dry_run:
            click.echo(f"\n📋 Methods that would be cleaned up (DRY RUN):")
            for method_name, method_info in expired_methods:
                age_hours = (current_time - method_info.injected_at) / 3600
                click.echo(f"   • {method_name} (age: {age_hours:.1f} hours)")
        else:
            click.echo(f"\n🗑️  Cleaning up expired methods...")
            
            # Perform cleanup
            cleaned_count = manager.cleanup_expired_methods(max_age_hours)
            
            click.echo(f"   ✅ Cleaned up {cleaned_count} expired methods")
            
            # Show remaining methods
            remaining_methods = manager.list_methods(agent_path)
            click.echo(f"   📊 Remaining methods: {len(remaining_methods)}")
        
    except Exception as e:
        click.echo(f"\n💥 Error during cleanup: {e}")
        raise click.Abort()


@method.command()
@click.argument('implementation_file', type=click.Path(exists=True, path_type=Path))
@click.option('--language', '-l', default='python',
              type=click.Choice(['python', 'javascript', 'shell', 'bash']),
              help='Programming language of the implementation')
@click.option('--security-level', '-s', default='medium',
              type=click.Choice(['low', 'medium', 'high']),
              help='Security level for validation')
@click.option('--output-format', '-f', default='human',
              type=click.Choice(['human', 'json', 'yaml']),
              help='Output format for validation results')
def validate(implementation_file: Path, language: str, security_level: str, output_format: str):
    """
    Validate a method implementation without injecting it.
    
    IMPLEMENTATION_FILE: File containing the method implementation to validate
    """
    try:
        manager = CustomMethodManager(security_level=security_level)
        
        # Read implementation file
        with open(implementation_file, 'r', encoding='utf-8') as f:
            implementation = f.read()
        
        click.echo(f"🔍 Validating method implementation...")
        click.echo(f"   File: {implementation_file}")
        click.echo(f"   Language: {language}")
        click.echo(f"   Security Level: {security_level}")
        
        # Validate the method
        validation_result = manager.method_validator.validate_method(implementation, language)
        
        if output_format == 'json':
            click.echo(json.dumps(validation_result.to_dict(), indent=2, default=str))
        elif output_format == 'yaml':
            try:
                import yaml
                click.echo(yaml.dump(validation_result.to_dict(), default_flow_style=False, default_representer=str))
            except ImportError:
                click.echo("❌ YAML output requires PyYAML package. Install with: pip install PyYAML")
                raise click.Abort()
        else:
            # Human-readable output
            click.echo(f"\n📊 Validation Results:")
            click.echo(f"   Valid: {'✅ Yes' if validation_result.is_valid else '❌ No'}")
            click.echo(f"   Security Score: {validation_result.security_score}/100")
            click.echo(f"   Total Issues: {validation_result.total_issues}")
            
            if validation_result.errors:
                click.echo(f"\n❌ Validation Errors ({len(validation_result.errors)}):")
                for error in validation_result.errors:
                    click.echo(f"   • {error}")
            
            if validation_result.warnings:
                click.echo(f"\n⚠️  Validation Warnings ({len(validation_result.warnings)}):")
                for warning in validation_result.warnings:
                    click.echo(f"   • {warning}")
            
            if validation_result.is_valid:
                click.echo(f"\n✅ Method validation passed successfully!")
                if validation_result.warnings:
                    click.echo(f"   Note: {len(validation_result.warnings)} warnings were found")
            else:
                click.echo(f"\n❌ Method validation failed!")
                click.echo(f"   Please fix the errors before using this method")
            
            # Show suggestions
            suggestions = manager.method_validator.suggest_improvements(validation_result)
            if suggestions:
                click.echo(f"\n💡 Suggestions for improvement:")
                for suggestion in suggestions:
                    click.echo(f"   • {suggestion}")
        
        # Exit with appropriate code
        if not validation_result.is_valid:
            raise click.Abort()
        
    except Exception as e:
        click.echo(f"\n💥 Error during validation: {e}")
        raise click.Abort()


@method.command()
@click.option('--format', '-f', default='table',
              type=click.Choice(['table', 'json', 'yaml']),
              help='Output format')
def languages(format: str):
    """List supported programming languages for custom methods."""
    try:
        manager = CustomMethodManager()
        supported_languages = manager.allowed_languages
        
        click.echo(f"🌐 Supported Programming Languages:")
        click.echo(f"   Total: {len(supported_languages)} languages")
        
        if format == 'json':
            click.echo(json.dumps(list(supported_languages), indent=2))
        elif format == 'yaml':
            try:
                import yaml
                click.echo(yaml.dump(list(supported_languages), default_flow_style=False))
            except ImportError:
                click.echo("❌ YAML output requires PyYAML package. Install with: pip install PyYAML")
                raise click.Abort()
        else:
            click.echo(f"\n📋 Available Languages:")
            for lang in sorted(supported_languages):
                click.echo(f"   • {lang}")
            
            click.echo(f"\n💡 Language-specific features:")
            click.echo(f"   • Python: Full function support with security validation")
            click.echo(f"   • JavaScript: Node.js execution with parameter passing")
            click.echo(f"   • Shell/Bash: Script execution with environment variables")
        
    except Exception as e:
        click.echo(f"\n💥 Error listing languages: {e}")
        raise click.Abort()


@method.command()
@click.option('--format', '-f', default='table',
              type=click.Choice(['table', 'json', 'yaml']),
              help='Output format')
def security_patterns(format: str):
    """Show security patterns that are checked during validation."""
    try:
        manager = CustomMethodManager()
        
        click.echo(f"🔒 Security Patterns Checked During Validation:")
        
        if format == 'json':
            output_data = {}
            for lang, patterns in manager.forbidden_patterns.items():
                output_data[lang] = list(patterns)
            click.echo(json.dumps(output_data, indent=2))
        elif format == 'yaml':
            try:
                import yaml
                output_data = {}
                for lang, patterns in manager.forbidden_patterns.items():
                    output_data[lang] = list(patterns)
                click.echo(yaml.dump(output_data, default_flow_style=False))
            except ImportError:
                click.echo("❌ YAML output requires PyYAML package. Install with: pip install PyYAML")
                raise click.Abort()
        else:
            for language, patterns in manager.forbidden_patterns.items():
                click.echo(f"\n🚨 {language.upper()} Forbidden Patterns:")
                for pattern in sorted(patterns):
                    click.echo(f"   • {pattern}")
            
            click.echo(f"\n💡 Security Features:")
            click.echo(f"   • Pattern-based detection of dangerous code")
            click.echo(f"   • AST analysis for Python code")
            click.echo(f"   • Resource usage monitoring")
            click.echo(f"   • Configurable security levels (low/medium/high)")
        
    except Exception as e:
        click.echo(f"\n💥 Error showing security patterns: {e}")
        raise click.Abort()
