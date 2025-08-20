"""
Sample Custom Methods for Agent Hub

This file contains example custom methods that can be injected into agents.
Each method demonstrates different capabilities and best practices.
"""

import time
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime


# ============================================================================
# TEXT PROCESSING METHODS
# ============================================================================

def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text and return comprehensive statistics.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Dictionary with text analysis results
    """
    if not text:
        return {"error": "Empty text provided"}
    
    # Basic statistics
    char_count = len(text)
    word_count = len(text.split())
    line_count = len(text.splitlines())
    
    # Character analysis
    uppercase_count = sum(1 for c in text if c.isupper())
    lowercase_count = sum(1 for c in text if c.islower())
    digit_count = sum(1 for c in text if c.isdigit())
    space_count = sum(1 for c in text if c.isspace())
    punctuation_count = sum(1 for c in text if c in '.,!?;:')
    
    # Word analysis
    words = text.split()
    unique_words = len(set(words))
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    # Sentiment indicators (simple heuristics)
    positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'horrible']
    
    positive_count = sum(1 for word in words if word.lower() in positive_words)
    negative_count = sum(1 for word in words if word.lower() in negative_words)
    
    return {
        "basic_stats": {
            "characters": char_count,
            "words": word_count,
            "lines": line_count
        },
        "character_analysis": {
            "uppercase": uppercase_count,
            "lowercase": lowercase_count,
            "digits": digit_count,
            "spaces": space_count,
            "punctuation": punctuation_count
        },
        "word_analysis": {
            "unique_words": unique_words,
            "average_word_length": round(avg_word_length, 2),
            "vocabulary_diversity": round(unique_words / word_count, 3) if word_count > 0 else 0
        },
        "sentiment_indicators": {
            "positive_words": positive_count,
            "negative_words": negative_count,
            "sentiment_score": positive_count - negative_count
        },
        "analysis_timestamp": datetime.now().isoformat()
    }


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract various entities from text using regex patterns.
    
    Args:
        text: Input text to extract entities from
        
    Returns:
        Dictionary with extracted entities
    """
    entities = {
        "emails": [],
        "urls": [],
        "phone_numbers": [],
        "dates": [],
        "ip_addresses": [],
        "credit_cards": []
    }
    
    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities["emails"] = re.findall(email_pattern, text)
    
    # URLs
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    entities["urls"] = re.findall(url_pattern, text)
    
    # Phone numbers (various formats)
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    entities["phone_numbers"] = re.findall(phone_pattern, text)
    
    # Dates (various formats)
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'  # Month DD, YYYY
    ]
    
    for pattern in date_patterns:
        entities["dates"].extend(re.findall(pattern, text, re.IGNORECASE))
    
    # IP addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    entities["ip_addresses"] = re.findall(ip_pattern, text)
    
    # Credit card numbers (basic pattern, not comprehensive)
    cc_pattern = r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
    entities["credit_cards"] = re.findall(cc_pattern, text)
    
    return entities


def summarize_text(text: str, max_length: int = 150) -> Dict[str, Any]:
    """
    Generate a summary of text by extracting key sentences.
    
    Args:
        text: Input text to summarize
        max_length: Maximum length of summary
        
    Returns:
        Dictionary with summary and metadata
    """
    if not text:
        return {"error": "Empty text provided"}
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return {"error": "No sentences found"}
    
    # Simple scoring based on word frequency
    words = text.lower().split()
    word_freq = {}
    
    for word in words:
        if len(word) > 3:  # Skip short words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences based on word frequency
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
        sentence_scores.append((sentence, score))
    
    # Sort by score and select top sentences
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    
    summary = ""
    selected_sentences = []
    
    for sentence, score in sentence_scores:
        if len(summary + sentence) <= max_length:
            summary += sentence + ". "
            selected_sentences.append(sentence)
        else:
            break
    
    return {
        "summary": summary.strip(),
        "original_length": len(text),
        "summary_length": len(summary),
        "compression_ratio": round(len(summary) / len(text), 3),
        "selected_sentences": selected_sentences,
        "sentence_count": len(selected_sentences),
        "max_length": max_length
    }


# ============================================================================
# DATA PROCESSING METHODS
# ============================================================================

def process_numerical_data(data: List[float], operation: str = "stats") -> Dict[str, Any]:
    """
    Process numerical data with various statistical operations.
    
    Args:
        data: List of numerical values
        operation: Type of operation to perform
        
    Returns:
        Dictionary with processing results
    """
    if not data:
        return {"error": "Empty dataset provided"}
    
    if not all(isinstance(x, (int, float)) for x in data):
        return {"error": "All values must be numerical"}
    
    result = {
        "dataset_size": len(data),
        "operation": operation,
        "timestamp": datetime.now().isoformat()
    }
    
    if operation == "stats":
        result.update({
            "min": min(data),
            "max": max(data),
            "sum": sum(data),
            "mean": sum(data) / len(data),
            "range": max(data) - min(data)
        })
        
        # Calculate median
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            median = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
        else:
            median = sorted_data[n//2]
        
        result["median"] = median
        
        # Calculate variance and standard deviation
        mean = result["mean"]
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        result["variance"] = variance
        result["std_deviation"] = variance ** 0.5
        
    elif operation == "filter":
        # Filter data based on criteria
        positive = [x for x in data if x > 0]
        negative = [x for x in data if x < 0]
        zero = [x for x in data if x == 0]
        
        result.update({
            "positive_count": len(positive),
            "negative_count": len(negative),
            "zero_count": len(zero),
            "positive_sum": sum(positive),
            "negative_sum": sum(negative)
        })
        
    elif operation == "transform":
        # Transform data
        result.update({
            "squared": [x**2 for x in data],
            "absolute": [abs(x) for x in data],
            "rounded": [round(x, 2) for x in data],
            "normalized": [(x - min(data)) / (max(data) - min(data)) for x in data]
        })
        
    else:
        result["error"] = f"Unknown operation: {operation}"
    
    return result


def analyze_data_structure(data: Any) -> Dict[str, Any]:
    """
    Analyze the structure and content of data.
    
    Args:
        data: Data to analyze
        
    Returns:
        Dictionary with structure analysis
    """
    analysis = {
        "type": type(data).__name__,
        "size": None,
        "structure": {},
        "content_sample": None,
        "timestamp": datetime.now().isoformat()
    }
    
    if isinstance(data, (str, bytes)):
        analysis["size"] = len(data)
        analysis["content_sample"] = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
        
    elif isinstance(data, (list, tuple)):
        analysis["size"] = len(data)
        analysis["structure"]["item_types"] = list(set(type(item).__name__ for item in data))
        analysis["structure"]["nested"] = any(isinstance(item, (list, dict, tuple)) for item in data)
        analysis["content_sample"] = data[:5] if len(data) > 5 else data
        
    elif isinstance(data, dict):
        analysis["size"] = len(data)
        analysis["structure"]["key_types"] = list(set(type(k).__name__ for k in data.keys()))
        analysis["structure"]["value_types"] = list(set(type(v).__name__ for v in data.values()))
        analysis["structure"]["nested"] = any(isinstance(v, (list, dict, tuple)) for v in data.values())
        analysis["content_sample"] = dict(list(data.items())[:5])
        
    elif isinstance(data, (int, float)):
        analysis["size"] = 1
        analysis["content_sample"] = data
        
    elif data is None:
        analysis["size"] = 0
        analysis["content_sample"] = None
        
    else:
        analysis["size"] = "unknown"
        analysis["content_sample"] = str(data)[:100] + "..." if len(str(data)) > 100 else str(data)
    
    return analysis


# ============================================================================
# UTILITY METHODS
# ============================================================================

def format_timestamp(timestamp: Optional[float] = None, format_type: str = "iso") -> Dict[str, Any]:
    """
    Format timestamp in various formats.
    
    Args:
        timestamp: Unix timestamp (uses current time if None)
        format_type: Type of format to use
        
    Returns:
        Dictionary with formatted timestamps
    """
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    
    formats = {
        "iso": dt.isoformat(),
        "rfc2822": dt.strftime("%a, %d %b %Y %H:%M:%S %z"),
        "human": dt.strftime("%B %d, %Y at %I:%M %p"),
        "short": dt.strftime("%Y-%m-%d %H:%M"),
        "date_only": dt.strftime("%Y-%m-%d"),
        "time_only": dt.strftime("%H:%M:%S")
    }
    
    return {
        "unix_timestamp": timestamp,
        "formatted": formats.get(format_type, formats["iso"]),
        "all_formats": formats,
        "datetime_object": {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
            "minute": dt.minute,
            "second": dt.second,
            "microsecond": dt.microsecond
        }
    }


def validate_input(data: Any, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate input data against specified rules.
    
    Args:
        data: Data to validate
        validation_rules: Dictionary specifying validation rules
        
    Returns:
        Dictionary with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "validation_timestamp": datetime.now().isoformat()
    }
    
    # Type validation
    if "type" in validation_rules:
        expected_type = validation_rules["type"]
        if not isinstance(data, expected_type):
            results["valid"] = False
            results["errors"].append(f"Expected type {expected_type.__name__}, got {type(data).__name__}")
    
    # Length validation
    if "min_length" in validation_rules and hasattr(data, "__len__"):
        if len(data) < validation_rules["min_length"]:
            results["valid"] = False
            results["errors"].append(f"Length {len(data)} is below minimum {validation_rules['min_length']}")
    
    if "max_length" in validation_rules and hasattr(data, "__len__"):
        if len(data) > validation_rules["max_length"]:
            results["valid"] = False
            results["errors"].append(f"Length {len(data)} exceeds maximum {validation_rules['max_length']}")
    
    # Value validation
    if "min_value" in validation_rules and isinstance(data, (int, float)):
        if data < validation_rules["min_value"]:
            results["valid"] = False
            results["errors"].append(f"Value {data} is below minimum {validation_rules['min_value']}")
    
    if "max_value" in validation_rules and isinstance(data, (int, float)):
        if data > validation_rules["max_value"]:
            results["valid"] = False
            results["errors"].append(f"Value {data} exceeds maximum {validation_rules['max_value']}")
    
    # Pattern validation (for strings)
    if "pattern" in validation_rules and isinstance(data, str):
        import re
        if not re.match(validation_rules["pattern"], data):
            results["valid"] = False
            results["errors"].append(f"String does not match pattern: {validation_rules['pattern']}")
    
    # Custom validation function
    if "custom_validator" in validation_rules and callable(validation_rules["custom_validator"]):
        try:
            custom_result = validation_rules["custom_validator"](data)
            if not custom_result:
                results["valid"] = False
                results["errors"].append("Custom validation failed")
        except Exception as e:
            results["valid"] = False
            results["errors"].append(f"Custom validation error: {str(e)}")
    
    # Warnings for non-critical issues
    if "warn_empty" in validation_rules and validation_rules["warn_empty"]:
        if hasattr(data, "__len__") and len(data) == 0:
            results["warnings"].append("Data is empty")
    
    return results


def generate_report(data: Any, report_type: str = "summary") -> Dict[str, Any]:
    """
    Generate various types of reports from data.
    
    Args:
        data: Data to generate report from
        report_type: Type of report to generate
        
    Returns:
        Dictionary with generated report
    """
    report = {
        "report_type": report_type,
        "generated_at": datetime.now().isoformat(),
        "data_type": type(data).__name__,
        "content": {}
    }
    
    if report_type == "summary":
        if isinstance(data, (list, tuple)):
            report["content"] = {
                "count": len(data),
                "types": list(set(type(item).__name__ for item in data)),
                "sample": data[:5] if len(data) > 5 else data
            }
        elif isinstance(data, dict):
            report["content"] = {
                "keys": list(data.keys()),
                "key_count": len(data),
                "value_types": list(set(type(v).__name__ for v in data.values())),
                "sample": dict(list(data.items())[:5])
            }
        elif isinstance(data, str):
            report["content"] = {
                "length": len(data),
                "word_count": len(data.split()),
                "line_count": len(data.splitlines()),
                "sample": data[:100] + "..." if len(data) > 100 else data
            }
        else:
            report["content"] = {
                "value": data,
                "representation": str(data)
            }
    
    elif report_type == "statistics":
        if isinstance(data, (list, tuple)) and all(isinstance(x, (int, float)) for x in data):
            report["content"] = {
                "count": len(data),
                "sum": sum(data),
                "mean": sum(data) / len(data),
                "min": min(data),
                "max": max(data),
                "range": max(data) - min(data)
            }
        else:
            report["content"] = {"error": "Statistics report requires numerical data"}
    
    elif report_type == "json":
        try:
            # Try to convert to JSON
            if hasattr(data, '__dict__'):
                json_data = json.dumps(data.__dict__, default=str, indent=2)
            else:
                json_data = json.dumps(data, default=str, indent=2)
            
            report["content"] = {
                "json_string": json_data,
                "json_size": len(json_data)
            }
        except Exception as e:
            report["content"] = {"error": f"Failed to convert to JSON: {str(e)}"}
    
    else:
        report["content"] = {"error": f"Unknown report type: {report_type}"}
    
    return report


# ============================================================================
# ADVANCED METHODS
# ============================================================================

def batch_processor(items: List[Any], processor_func: str, batch_size: int = 10) -> Dict[str, Any]:
    """
    Process items in batches with progress tracking.
    
    Args:
        items: List of items to process
        processor_func: Name of the function to apply to each item
        batch_size: Size of each batch
        
    Returns:
        Dictionary with processing results and progress
    """
    if not items:
        return {"error": "No items provided"}
    
    total_items = len(items)
    processed_items = []
    failed_items = []
    start_time = time.time()
    
    # Process in batches
    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        batch_start = time.time()
        
        for item in batch:
            try:
                # Apply processor function (simplified - in real usage, this would be more dynamic)
                if processor_func == "uppercase" and isinstance(item, str):
                    processed_items.append(item.upper())
                elif processor_func == "double" and isinstance(item, (int, float)):
                    processed_items.append(item * 2)
                elif processor_func == "length" and hasattr(item, "__len__"):
                    processed_items.append(len(item))
                else:
                    processed_items.append(f"Processed: {item}")
                    
            except Exception as e:
                failed_items.append({"item": item, "error": str(e)})
        
        batch_time = time.time() - batch_start
        
        # Progress update
        progress = min(100, (i + len(batch)) / total_items * 100)
        
        if progress % 25 == 0:  # Log every 25%
            print(f"Progress: {progress:.1f}% - Batch processed in {batch_time:.3f}s")
    
    total_time = time.time() - start_time
    
    return {
        "total_items": total_items,
        "processed_count": len(processed_items),
        "failed_count": len(failed_items),
        "success_rate": round((len(processed_items) / total_items) * 100, 2),
        "processing_time": round(total_time, 3),
        "average_time_per_item": round(total_time / total_items, 4),
        "processed_items": processed_items,
        "failed_items": failed_items,
        "processor_function": processor_func,
        "batch_size": batch_size
    }


def data_transformer(data: Any, transformation: str, **kwargs) -> Dict[str, Any]:
    """
    Transform data using various transformation methods.
    
    Args:
        data: Data to transform
        transformation: Type of transformation to apply
        **kwargs: Additional transformation parameters
        
    Returns:
        Dictionary with transformation results
    """
    result = {
        "original_data": data,
        "transformation": transformation,
        "parameters": kwargs,
        "transformed_data": None,
        "transformation_time": None,
        "success": False
    }
    
    start_time = time.time()
    
    try:
        if transformation == "reverse":
            if isinstance(data, str):
                result["transformed_data"] = data[::-1]
            elif isinstance(data, (list, tuple)):
                result["transformed_data"] = list(reversed(data))
            else:
                raise ValueError("Reverse transformation requires string or sequence")
        
        elif transformation == "sort":
            if isinstance(data, (list, tuple)):
                reverse = kwargs.get("reverse", False)
                key_func = kwargs.get("key", None)
                result["transformed_data"] = sorted(data, reverse=reverse, key=key_func)
            else:
                raise ValueError("Sort transformation requires sequence")
        
        elif transformation == "filter":
            if isinstance(data, (list, tuple)):
                filter_func = kwargs.get("filter_func", lambda x: bool(x))
                result["transformed_data"] = [item for item in data if filter_func(item)]
            else:
                raise ValueError("Filter transformation requires sequence")
        
        elif transformation == "map":
            if isinstance(data, (list, tuple)):
                map_func = kwargs.get("map_func", lambda x: x)
                result["transformed_data"] = [map_func(item) for item in data]
            else:
                raise ValueError("Map transformation requires sequence")
        
        elif transformation == "group":
            if isinstance(data, (list, tuple)):
                key_func = kwargs.get("key_func", lambda x: type(x).__name__)
                groups = {}
                for item in data:
                    key = key_func(item)
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(item)
                result["transformed_data"] = groups
            else:
                raise ValueError("Group transformation requires sequence")
        
        elif transformation == "flatten":
            if isinstance(data, (list, tuple)):
                flattened = []
                for item in data:
                    if isinstance(item, (list, tuple)):
                        flattened.extend(item)
                    else:
                        flattened.append(item)
                result["transformed_data"] = flattened
            else:
                raise ValueError("Flatten transformation requires sequence")
        
        else:
            raise ValueError(f"Unknown transformation: {transformation}")
        
        result["success"] = True
        
    except Exception as e:
        result["error"] = str(e)
        result["success"] = False
    
    result["transformation_time"] = time.time() - start_time
    
    return result


# ============================================================================
# SECURITY-FOCUSED METHODS
# ============================================================================

def sanitize_input(user_input: str, sanitization_level: str = "medium") -> Dict[str, Any]:
    """
    Sanitize user input to prevent security issues.
    
    Args:
        user_input: Input string to sanitize
        sanitization_level: Level of sanitization (low, medium, high)
        
    Returns:
        Dictionary with sanitization results
    """
    if not isinstance(user_input, str):
        return {"error": "Input must be a string"}
    
    original = user_input
    sanitized = user_input
    removed_patterns = []
    
    # Define patterns to remove based on security level
    patterns = {
        "low": [
            (r'<script.*?</script>', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'vbscript:', 'VBScript protocol')
        ],
        "medium": [
            (r'<script.*?</script>', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'vbscript:', 'VBScript protocol'),
            (r'<iframe.*?</iframe>', 'IFrame tags'),
            (r'<object.*?</object>', 'Object tags'),
            (r'<embed.*?</embed>', 'Embed tags'),
            (r'<form.*?</form>', 'Form tags'),
            (r'on\w+\s*=', 'Event handlers'),
            (r'<.*?>', 'HTML tags')
        ],
        "high": [
            (r'<script.*?</script>', 'Script tags'),
            (r'javascript:', 'JavaScript protocol'),
            (r'vbscript:', 'VBScript protocol'),
            (r'<iframe.*?</iframe>', 'IFrame tags'),
            (r'<object.*?</embed>', 'Object tags'),
            (r'<embed.*?</embed>', 'Embed tags'),
            (r'<form.*?</form>', 'Form tags'),
            (r'on\w+\s*=', 'Event handlers'),
            (r'<.*?>', 'HTML tags'),
            (r'[<>]', 'Angle brackets'),
            (r'&', 'Ampersands'),
            (r'"', 'Double quotes'),
            (r"'", 'Single quotes')
        ]
    }
    
    if sanitization_level not in patterns:
        sanitization_level = "medium"
    
    # Apply sanitization patterns
    for pattern, description in patterns[sanitization_level]:
        matches = re.findall(pattern, sanitized, re.IGNORECASE)
        if matches:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            removed_patterns.append(f"{description}: {len(matches)} found")
    
    # Additional high-level sanitization
    if sanitization_level == "high":
        # Remove all non-alphanumeric characters except spaces and basic punctuation
        sanitized = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', sanitized)
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
    
    return {
        "original_input": original,
        "sanitized_input": sanitized,
        "sanitization_level": sanitization_level,
        "removed_patterns": removed_patterns,
        "input_length": len(original),
        "sanitized_length": len(sanitized),
        "characters_removed": len(original) - len(sanitized),
        "sanitization_timestamp": datetime.now().isoformat()
    }


def validate_file_upload(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate file upload information for security.
    
    Args:
        file_info: Dictionary containing file information
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "file_info": file_info,
        "validation_timestamp": datetime.now().isoformat()
    }
    
    # Check required fields
    required_fields = ["filename", "size", "content_type"]
    for field in required_fields:
        if field not in file_info:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing required field: {field}")
    
    if not validation_result["valid"]:
        return validation_result
    
    filename = file_info.get("filename", "")
    size = file_info.get("size", 0)
    content_type = file_info.get("content_type", "")
    
    # File size validation
    max_size = file_info.get("max_size", 10 * 1024 * 1024)  # 10MB default
    if size > max_size:
        validation_result["valid"] = False
        validation_result["errors"].append(f"File size {size} exceeds maximum {max_size}")
    
    # File extension validation
    allowed_extensions = file_info.get("allowed_extensions", [".txt", ".pdf", ".doc", ".docx"])
    file_ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    
    if file_ext and file_ext not in allowed_extensions:
        validation_result["valid"] = False
        validation_result["errors"].append(f"File extension {file_ext} not allowed")
    
    # Content type validation
    allowed_types = file_info.get("allowed_types", ["text/plain", "application/pdf", "application/msword"])
    if content_type not in allowed_types:
        validation_result["warnings"].append(f"Content type {content_type} not in allowed list")
    
    # Filename security checks
    dangerous_patterns = [
        r'\.\.',  # Directory traversal
        r'[<>:"|?*]',  # Invalid characters
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Reserved names
        r'\.(exe|bat|cmd|com|pif|scr|vbs|js)$'  # Executable extensions
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            validation_result["valid"] = False
            validation_result["errors"].append(f"Dangerous filename pattern detected: {pattern}")
    
    # Additional security checks
    if len(filename) > 255:
        validation_result["warnings"].append("Filename is very long")
    
    if filename.startswith("."):
        validation_result["warnings"].append("Hidden file detected")
    
    return validation_result


# ============================================================================
# PERFORMANCE MONITORING METHODS
# ============================================================================

def performance_monitor(func_name: str, execution_time: float, memory_usage: Optional[float] = None) -> Dict[str, Any]:
    """
    Monitor and log performance metrics for function execution.
    
    Args:
        func_name: Name of the function being monitored
        execution_time: Execution time in seconds
        memory_usage: Memory usage in MB (optional)
        
    Returns:
        Dictionary with performance metrics
    """
    metrics = {
        "function_name": func_name,
        "execution_time": execution_time,
        "memory_usage_mb": memory_usage,
        "timestamp": datetime.now().isoformat(),
        "performance_rating": "unknown",
        "recommendations": []
    }
    
    # Performance rating based on execution time
    if execution_time < 0.1:
        metrics["performance_rating"] = "excellent"
    elif execution_time < 1.0:
        metrics["performance_rating"] = "good"
    elif execution_time < 5.0:
        metrics["performance_rating"] = "acceptable"
    elif execution_time < 10.0:
        metrics["performance_rating"] = "slow"
    else:
        metrics["performance_rating"] = "very_slow"
    
    # Generate recommendations
    if execution_time > 1.0:
        metrics["recommendations"].append("Consider optimizing algorithm complexity")
    
    if execution_time > 5.0:
        metrics["recommendations"].append("Consider implementing caching")
        metrics["recommendations"].append("Consider breaking into smaller functions")
    
    if memory_usage and memory_usage > 100:
        metrics["recommendations"].append("Consider memory optimization")
        metrics["recommendations"].append("Check for memory leaks")
    
    # Performance thresholds
    thresholds = {
        "warning": 1.0,
        "critical": 5.0
    }
    
    if execution_time > thresholds["critical"]:
        metrics["status"] = "critical"
    elif execution_time > thresholds["warning"]:
        metrics["status"] = "warning"
    else:
        metrics["status"] = "normal"
    
    return metrics


def resource_usage_monitor() -> Dict[str, Any]:
    """
    Monitor current system resource usage.
    
    Returns:
        Dictionary with resource usage information
    """
    import psutil
    
    try:
        # CPU information
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Memory information
        memory = psutil.virtual_memory()
        
        # Disk information
        disk = psutil.disk_usage('/')
        
        # Network information
        network = psutil.net_io_counters()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "frequency_mhz": cpu_freq.current if cpu_freq else None
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round((disk.used / disk.total) * 100, 2)
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
        
    except ImportError:
        return {
            "error": "psutil library not available",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Failed to monitor resources: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# EXPORT ALL METHODS
# ============================================================================

# List of all available methods for easy discovery
AVAILABLE_METHODS = {
    # Text processing
    "analyze_text": analyze_text,
    "extract_entities": extract_entities,
    "summarize_text": summarize_text,
    
    # Data processing
    "process_numerical_data": process_numerical_data,
    "analyze_data_structure": analyze_data_structure,
    
    # Utilities
    "format_timestamp": format_timestamp,
    "validate_input": validate_input,
    "generate_report": generate_report,
    
    # Advanced
    "batch_processor": batch_processor,
    "data_transformer": data_transformer,
    
    # Security
    "sanitize_input": sanitize_input,
    "validate_file_upload": validate_file_upload,
    
    # Performance
    "performance_monitor": performance_monitor,
    "resource_usage_monitor": resource_usage_monitor
}

# Method categories for organization
METHOD_CATEGORIES = {
    "text_processing": ["analyze_text", "extract_entities", "summarize_text"],
    "data_processing": ["process_numerical_data", "analyze_data_structure"],
    "utilities": ["format_timestamp", "validate_input", "generate_report"],
    "advanced": ["batch_processor", "data_transformer"],
    "security": ["sanitize_input", "validate_file_upload"],
    "performance": ["performance_monitor", "resource_usage_monitor"]
}

# Method metadata for documentation
METHOD_METADATA = {
    "analyze_text": {
        "description": "Analyze text and return comprehensive statistics",
        "parameters": ["text"],
        "returns": "Dictionary with text analysis results",
        "category": "text_processing"
    },
    "extract_entities": {
        "description": "Extract various entities from text using regex patterns",
        "parameters": ["text"],
        "returns": "Dictionary with extracted entities",
        "category": "text_processing"
    },
    "summarize_text": {
        "description": "Generate a summary of text by extracting key sentences",
        "parameters": ["text", "max_length"],
        "returns": "Dictionary with summary and metadata",
        "category": "text_processing"
    }
    # ... additional metadata can be added for each method
}
