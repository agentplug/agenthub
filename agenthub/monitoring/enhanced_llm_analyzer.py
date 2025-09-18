"""
Enhanced LLM-based log analyzer for real-time agent monitoring

Provides context-aware analysis with learning capabilities, pattern recognition,
and agent-specific insights for better monitoring experience.
"""

import json
import time
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any

from agenthub.core.llm.llm_service import CoreLLMService, LogAnalysis


class EnhancedLLMAnalyzer:
    """
    Enhanced LLM-based log analyzer with context and learning
    
    Analyzes agent logs using the Core LLM Component with:
    - Agent-specific context and prompts
    - Learning from previous executions
    - Pattern recognition and anomaly detection
    - Adaptive analysis based on log content
    """

    def __init__(self, core_llm_service: CoreLLMService, config: Optional[Dict] = None):
        """
        Initialize Enhanced LLM Analyzer
        
        Args:
            core_llm_service: Core LLM service instance for log analysis
            config: Optional configuration dictionary
        """
        self.core_llm = core_llm_service
        self.config = config or {}
        
        # Learning and context storage
        self.agent_patterns = {}  # agent_type -> patterns
        self.error_patterns = {}  # error_type -> solutions
        self.success_patterns = {}  # successful execution patterns
        self.execution_history = deque(maxlen=self.config.get('context_window', 50))
        
        # Analysis cache for performance
        self.analysis_cache = {}
        self.cache_ttl = 30  # seconds
        
        # Agent-specific prompts
        self.agent_prompts = self._initialize_agent_prompts()
        
        # Pattern detection
        self.pattern_detectors = {
            'error': self._detect_error_patterns,
            'performance': self._detect_performance_patterns,
            'success': self._detect_success_patterns,
            'tool_usage': self._detect_tool_usage_patterns
        }

    def analyze_with_context(
        self, 
        logs: List[str], 
        agent_type: str, 
        execution_id: str,
        additional_context: Optional[Dict] = None
    ) -> LogAnalysis:
        """
        Enhanced analysis with learning and context
        
        Args:
            logs: List of log lines from agent execution
            agent_type: Type of agent being analyzed
            execution_id: Unique identifier for this execution
            additional_context: Additional context information
            
        Returns:
            Enhanced LogAnalysis object with context-aware insights
        """
        if not logs:
            return self._fallback_analysis([])
        
        # Get agent-specific context
        agent_context = self._get_agent_context(agent_type)
        
        # Detect patterns in current logs
        detected_patterns = self._detect_log_patterns(logs)
        
        # Check cache first
        cache_key = self._generate_cache_key(logs, agent_type, detected_patterns)
        if cache_key in self.analysis_cache:
            cached_result, timestamp = self.analysis_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_result
        
        # Build enhanced prompt with context
        enhanced_prompt = self._build_enhanced_prompt(
            logs, agent_type, agent_context, detected_patterns, additional_context
        )
        
        # Get agent-specific system prompt
        system_prompt = self._get_agent_system_prompt(agent_type)
        
        # Analyze with LLM
        try:
            response = self.core_llm.analyze_text(
                "\n".join(logs), 
                enhanced_prompt, 
                system_prompt,
                return_json=True
            )
            analysis = self._parse_log_analysis_response(response)
        except Exception as e:
            # Fallback to pattern-based analysis
            analysis = self._pattern_based_analysis(logs, detected_patterns)
        
        # Enhance analysis with learned patterns
        analysis = self._enhance_with_learned_patterns(analysis, agent_type, detected_patterns)
        
        # Cache the result
        self.analysis_cache[cache_key] = (analysis, time.time())
        
        # Learn from this execution
        self._learn_from_execution(agent_type, logs, analysis, execution_id)
        
        return analysis

    def _get_agent_context(self, agent_type: str) -> Dict[str, Any]:
        """Get historical context for this agent type"""
        if agent_type not in self.agent_patterns:
            self.agent_patterns[agent_type] = {
                'common_errors': [],
                'success_patterns': [],
                'typical_duration': 0,
                'common_tools': [],
                'error_solutions': {},
                'performance_issues': [],
                'execution_count': 0
            }
        
        return self.agent_patterns[agent_type]

    def _detect_log_patterns(self, logs: List[str]) -> Dict[str, Any]:
        """Detect specific patterns in the logs"""
        patterns = {
            'error_count': 0,
            'warning_count': 0,
            'tool_calls': [],
            'performance_indicators': [],
            'unusual_patterns': [],
            'log_volume': len(logs),
            'error_types': set(),
            'tool_usage': defaultdict(int)
        }
        
        for log in logs:
            log_lower = log.lower()
            
            # Count errors and warnings
            if any(word in log_lower for word in ['error', 'exception', 'failed', 'traceback']):
                patterns['error_count'] += 1
                # Detect specific error types
                if 'timeout' in log_lower:
                    patterns['error_types'].add('timeout')
                elif 'memory' in log_lower:
                    patterns['error_types'].add('memory')
                elif 'permission' in log_lower:
                    patterns['error_types'].add('permission')
                    
            if any(word in log_lower for word in ['warning', 'warn', 'caution']):
                patterns['warning_count'] += 1
            
            # Detect tool calls
            if 'calling tool' in log_lower or 'executing' in log_lower:
                tool_name = self._extract_tool_name(log)
                if tool_name:
                    patterns['tool_calls'].append(tool_name)
                    patterns['tool_usage'][tool_name] += 1
            
            # Detect performance indicators
            if 'timeout' in log_lower:
                patterns['performance_indicators'].append('timeout')
            if 'memory' in log_lower and 'low' in log_lower:
                patterns['performance_indicators'].append('low_memory')
            if 'slow' in log_lower or 'taking long' in log_lower:
                patterns['performance_indicators'].append('slow_execution')
        
        return patterns

    def _build_enhanced_prompt(
        self, 
        logs: List[str], 
        agent_type: str, 
        context: Dict[str, Any],
        patterns: Dict[str, Any],
        additional_context: Optional[Dict] = None
    ) -> str:
        """Build context-aware prompt for LLM analysis"""
        base_prompt = self._get_log_analysis_prompt()
        
        # Add agent-specific context
        context_info = f"""
        Agent Type: {agent_type}
        Common Errors for this agent: {context.get('common_errors', [])}
        Success Patterns: {context.get('success_patterns', [])}
        Typical Duration: {context.get('typical_duration', 0)}s
        Common Tools: {context.get('common_tools', [])}
        Execution Count: {context.get('execution_count', 0)}
        """
        
        # Add pattern analysis
        pattern_info = f"""
        Detected Patterns:
        - Errors: {patterns['error_count']} (types: {list(patterns['error_types'])})
        - Warnings: {patterns['warning_count']}
        - Tools Used: {patterns['tool_calls']}
        - Performance Issues: {patterns['performance_indicators']}
        - Log Volume: {patterns['log_volume']} lines
        """
        
        # Add recent execution context
        recent_executions = list(self.execution_history)[-3:]  # Last 3 executions
        recent_context = ""
        if recent_executions:
            recent_context = f"""
            Recent Executions:
            {self._format_recent_executions(recent_executions)}
            """
        
        # Add additional context if provided
        additional_info = ""
        if additional_context:
            additional_info = f"""
            Additional Context:
            {json.dumps(additional_context, indent=2)}
            """
        
        enhanced_prompt = f"""
        {base_prompt}
        
        {context_info}
        {pattern_info}
        {recent_context}
        {additional_info}
        
        Based on this context, provide more specific and actionable insights.
        Focus on patterns you've seen before and provide agent-specific recommendations.
        """
        
        return enhanced_prompt

    def _get_agent_system_prompt(self, agent_type: str) -> str:
        """Get agent-specific system prompt"""
        agent_prompts = {
            'analysis-agent': """
            You are analyzing logs from a data analysis agent. Focus on:
            - Data processing steps and accuracy
            - Calculation errors and validation issues
            - Tool usage efficiency (especially mathematical tools)
            - Error patterns in data handling
            - Performance bottlenecks in data processing
            - Provide specific suggestions for data analysis improvements
            """,
            'code-generation-agent': """
            You are analyzing logs from a code generation agent. Focus on:
            - Code compilation errors and syntax issues
            - Logic errors and runtime problems
            - Tool integration problems (especially code-related tools)
            - Performance issues in code generation
            - Security vulnerabilities or best practices
            - Provide specific suggestions for code quality improvements
            """,
            'web-scraping-agent': """
            You are analyzing logs from a web scraping agent. Focus on:
            - Network connectivity and timeout issues
            - HTML parsing errors and data extraction problems
            - Rate limiting and anti-bot detection
            - Data validation and cleaning issues
            - Performance bottlenecks in scraping
            - Provide specific suggestions for scraping reliability
            """,
            'default': """
            You are an expert at analyzing agent execution logs. Focus on:
            - What the agent is currently doing
            - Any errors or issues detected
            - Progress estimation and performance
            - Tool usage patterns and efficiency
            - Actionable suggestions for improvement
            - Learning from previous execution patterns
            """
        }
        
        return agent_prompts.get(agent_type, agent_prompts['default'])

    def _get_log_analysis_prompt(self) -> str:
        """Get enhanced log analysis prompt template"""
        return """
            Analyze these agent execution logs and provide a comprehensive summary:

            {text}

            Please provide:
            1. What the agent is currently doing (max 50 characters)
            2. Any errors or issues detected with specific details
            3. Progress estimation (0-100%) based on patterns
            4. Performance insights and bottlenecks
            5. Tool usage efficiency and recommendations
            6. Actionable suggestions if errors found
            7. Confidence level in your analysis (0-100%)

            Format as JSON:
            {{
                "summary": "...",
                "progress": 75,
                "status": "working",
                "errors": ["..."],
                "suggestions": ["..."],
                "performance_insights": ["..."],
                "tool_recommendations": ["..."],
                "confidence": 85
            }}
        """

    def _parse_log_analysis_response(self, response: str) -> LogAnalysis:
        """Parse enhanced log analysis response from LLM"""
        try:
            data = json.loads(response)
            return LogAnalysis(
                summary=data.get("summary", "Working..."),
                progress=data.get("progress", 0),
                status=data.get("status", "working"),
                errors=data.get("errors", []),
                suggestions=data.get("suggestions", []),
                # Additional fields for enhanced analysis
                performance_insights=getattr(data, 'performance_insights', []),
                tool_recommendations=getattr(data, 'tool_recommendations', []),
                confidence=getattr(data, 'confidence', 50)
            )
        except (json.JSONDecodeError, TypeError) as e:
            return self._fallback_analysis([])

    def _pattern_based_analysis(self, logs: List[str], patterns: Dict[str, Any]) -> LogAnalysis:
        """Fallback pattern-based analysis when LLM fails"""
        if not logs:
            return LogAnalysis("🔄 Starting...", 0, "starting", [], [])
        
        log_text = " ".join(logs).lower()
        
        # Error detection
        error_words = ["error", "failed", "exception", "traceback"]
        if any(word in log_text for word in error_words):
            error_type = "unknown"
            if "timeout" in log_text:
                error_type = "timeout"
            elif "memory" in log_text:
                error_type = "memory"
            elif "permission" in log_text:
                error_type = "permission"
                
            return LogAnalysis(
                f"❌ Error detected ({error_type})", 
                0, 
                "error", 
                [f"Error type: {error_type}"], 
                [f"Check {error_type} related issues"]
            )
        
        # Performance issues
        if "slow" in log_text or "taking long" in log_text:
            return LogAnalysis(
                "🐌 Performance issue detected", 
                50, 
                "warning", 
                ["Slow execution"], 
                ["Check for bottlenecks", "Consider optimization"]
            )
        
        # Working state
        working_words = ["processing", "analyzing", "working", "executing"]
        if any(word in log_text for word in working_words):
            progress = min(50 + patterns['log_volume'] * 2, 90)  # Estimate based on log volume
            return LogAnalysis(
                "📊 Processing...", 
                progress, 
                "working", 
                [], 
                []
            )
        
        # Complete state
        complete_words = ["complete", "finished", "done", "success"]
        if any(word in log_text for word in complete_words):
            return LogAnalysis(
                "✅ Complete", 
                100, 
                "complete", 
                [], 
                []
            )
        
        # Starting state
        starting_words = ["starting", "initializing", "loading"]
        if any(word in log_text for word in starting_words):
            return LogAnalysis(
                "🚀 Starting...", 
                10, 
                "starting", 
                [], 
                []
            )
        
        return LogAnalysis("🔄 Working...", 25, "working", [], [])

    def _enhance_with_learned_patterns(
        self, 
        analysis: LogAnalysis, 
        agent_type: str, 
        patterns: Dict[str, Any]
    ) -> LogAnalysis:
        """Enhance analysis with learned patterns"""
        agent_context = self._get_agent_context(agent_type)
        
        # Add learned error solutions
        if analysis.errors:
            enhanced_suggestions = list(analysis.suggestions)
            for error in analysis.errors:
                error_lower = error.lower()
                for known_error, solution in agent_context.get('error_solutions', {}).items():
                    if known_error.lower() in error_lower:
                        enhanced_suggestions.append(f"💡 Known issue: {solution}")
            analysis.suggestions = enhanced_suggestions
        
        # Add performance insights based on history
        if patterns['performance_indicators']:
            perf_insights = []
            for indicator in patterns['performance_indicators']:
                if indicator in agent_context.get('performance_issues', []):
                    perf_insights.append(f"⚠️  Recurring performance issue: {indicator}")
            if hasattr(analysis, 'performance_insights'):
                analysis.performance_insights.extend(perf_insights)
        
        return analysis

    def _learn_from_execution(
        self, 
        agent_type: str, 
        logs: List[str], 
        analysis: LogAnalysis, 
        execution_id: str
    ):
        """Learn from this execution to improve future analysis"""
        # Record this execution
        execution_record = {
            'agent_type': agent_type,
            'logs': logs,
            'analysis': analysis,
            'execution_id': execution_id,
            'timestamp': time.time(),
            'duration': time.time() - getattr(self, '_last_execution_start', time.time())
        }
        
        self.execution_history.append(execution_record)
        self._last_execution_start = time.time()
        
        # Update agent patterns
        agent_patterns = self.agent_patterns[agent_type]
        agent_patterns['execution_count'] += 1
        
        # Learn from errors
        if analysis.errors:
            for error in analysis.errors:
                error_key = self._categorize_error(error)
                if error_key not in agent_patterns['common_errors']:
                    agent_patterns['common_errors'].append(error_key)
                
                # Learn error solutions
                if analysis.suggestions:
                    agent_patterns['error_solutions'][error_key] = analysis.suggestions[0]
        
        # Learn success patterns
        if analysis.status == 'complete' and not analysis.errors:
            success_pattern = self._extract_success_pattern(logs)
            if success_pattern and success_pattern not in agent_patterns['success_patterns']:
                agent_patterns['success_patterns'].append(success_pattern)
        
        # Learn tool usage patterns
        tool_calls = self._extract_tool_calls(logs)
        for tool in tool_calls:
            if tool not in agent_patterns['common_tools']:
                agent_patterns['common_tools'].append(tool)
        
        # Learn performance patterns
        if hasattr(analysis, 'performance_insights') and analysis.performance_insights:
            for insight in analysis.performance_insights:
                if 'slow' in insight.lower() or 'bottleneck' in insight.lower():
                    agent_patterns['performance_issues'].append(insight)

    def _generate_cache_key(self, logs: List[str], agent_type: str, patterns: Dict) -> str:
        """Generate cache key for analysis"""
        # Use log content hash and patterns for cache key
        log_hash = hash(tuple(logs[-10:]))  # Use last 10 logs
        pattern_hash = hash(tuple(sorted(patterns.items())))
        return f"{agent_type}_{log_hash}_{pattern_hash}"

    def _extract_tool_name(self, log: str) -> Optional[str]:
        """Extract tool name from log line"""
        # Simple pattern matching - in practice would be more sophisticated
        if 'calling tool' in log.lower():
            parts = log.split('calling tool')
            if len(parts) > 1:
                tool_part = parts[1].strip()
                return tool_part.split()[0] if tool_part.split() else None
        return None

    def _extract_tool_calls(self, logs: List[str]) -> List[str]:
        """Extract all tool calls from logs"""
        tool_calls = []
        for log in logs:
            tool_name = self._extract_tool_name(log)
            if tool_name:
                tool_calls.append(tool_name)
        return tool_calls

    def _extract_success_pattern(self, logs: List[str]) -> Optional[str]:
        """Extract success pattern from logs"""
        # Look for common success indicators
        success_indicators = ['completed successfully', 'finished', 'done', 'success']
        for log in logs:
            for indicator in success_indicators:
                if indicator in log.lower():
                    return indicator
        return None

    def _categorize_error(self, error: str) -> str:
        """Categorize error for learning"""
        error_lower = error.lower()
        if 'timeout' in error_lower:
            return 'timeout'
        elif 'memory' in error_lower:
            return 'memory'
        elif 'permission' in error_lower:
            return 'permission'
        elif 'network' in error_lower:
            return 'network'
        else:
            return 'general'

    def _format_recent_executions(self, executions: List[Dict]) -> str:
        """Format recent executions for context"""
        if not executions:
            return "No recent executions"
        
        formatted = []
        for exec_data in executions:
            status = exec_data['analysis'].status
            duration = exec_data.get('duration', 0)
            formatted.append(f"  - {status} ({duration:.1f}s)")
        
        return "\n".join(formatted)

    def _detect_error_patterns(self, logs: List[str]) -> List[str]:
        """Detect error patterns in logs"""
        # Implementation for error pattern detection
        return []

    def _detect_performance_patterns(self, logs: List[str]) -> List[str]:
        """Detect performance patterns in logs"""
        # Implementation for performance pattern detection
        return []

    def _detect_success_patterns(self, logs: List[str]) -> List[str]:
        """Detect success patterns in logs"""
        # Implementation for success pattern detection
        return []

    def _detect_tool_usage_patterns(self, logs: List[str]) -> List[str]:
        """Detect tool usage patterns in logs"""
        # Implementation for tool usage pattern detection
        return []

    def _fallback_analysis(self, logs: List[str]) -> LogAnalysis:
        """Fallback analysis when all else fails"""
        if not logs:
            return LogAnalysis("🔄 Starting...", 0, "starting", [], [])
        
        return LogAnalysis("🔄 Working...", 25, "working", [], [])

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learned patterns"""
        return {
            'agent_patterns': {k: {
                'execution_count': v.get('execution_count', 0),
                'common_errors': len(v.get('common_errors', [])),
                'success_patterns': len(v.get('success_patterns', [])),
                'common_tools': len(v.get('common_tools', [])),
                'performance_issues': len(v.get('performance_issues', []))
            } for k, v in self.agent_patterns.items()},
            'total_executions': len(self.execution_history),
            'cache_size': len(self.analysis_cache)
        }
