"""Example custom tools for AgentHub.

This file demonstrates how to create custom tools that can be used
with AgentHub agents. These tools show various patterns and best practices.
"""

from typing import Dict, List, Any, Optional
from agenthub.core.tools import tool


@tool(
    name="text_analyzer",
    description="Analyze text for various linguistic features",
    version="1.0.0"
)
def text_analyzer(
    text: str,
    analysis_type: str = "sentiment"
) -> Dict[str, Any]:
    """
    Analyze text for sentiment, entities, keywords, and other features.
    
    Args:
        text (str): The text to analyze
        analysis_type (str): Type of analysis (sentiment, entities, keywords, summary)
    
    Returns:
        Dict[str, Any]: Analysis results
    """
    if not text or not isinstance(text, str):
        return {
            "success": False,
            "error": "Text must be a non-empty string"
        }
    
    try:
        if analysis_type == "sentiment":
            # Mock sentiment analysis
            positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = 0.7
            elif negative_count > positive_count:
                sentiment = "negative"
                score = -0.7
            else:
                sentiment = "neutral"
                score = 0.0
            
            return {
                "success": True,
                "analysis_type": "sentiment",
                "sentiment": sentiment,
                "score": score,
                "positive_words_found": positive_count,
                "negative_words_found": negative_count
            }
        
        elif analysis_type == "entities":
            # Mock entity extraction
            import re
            
            # Simple regex-based entity extraction
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b'
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            
            emails = re.findall(email_pattern, text)
            phones = re.findall(phone_pattern, text)
            urls = re.findall(url_pattern, text)
            
            return {
                "success": True,
                "analysis_type": "entities",
                "emails": emails,
                "phone_numbers": phones,
                "urls": urls,
                "total_entities": len(emails) + len(phones) + len(urls)
            }
        
        elif analysis_type == "keywords":
            # Mock keyword extraction
            import re
            
            # Simple keyword extraction (remove common words)
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            keywords = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Count word frequency
            from collections import Counter
            keyword_counts = Counter(keywords)
            
            return {
                "success": True,
                "analysis_type": "keywords",
                "top_keywords": dict(keyword_counts.most_common(10)),
                "total_unique_keywords": len(keyword_counts),
                "total_words": len(words)
            }
        
        elif analysis_type == "summary":
            # Mock text summarization
            sentences = text.split('.')
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 2:
                summary = text
            else:
                # Simple extractive summarization (first and last sentences)
                summary = sentences[0] + ". " + sentences[-1] + "."
            
            return {
                "success": True,
                "analysis_type": "summary",
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary),
                "compression_ratio": len(summary) / len(text)
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown analysis type: {analysis_type}. "
                         "Supported types: sentiment, entities, keywords, summary"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis failed: {str(e)}"
        }


@tool(
    name="data_transformer",
    description="Transform data between different formats",
    version="1.0.0"
)
def data_transformer(
    data: str,
    input_format: str,
    output_format: str
) -> Dict[str, Any]:
    """
    Transform data between JSON, CSV, and XML formats.
    
    Args:
        data (str): The data to transform
        input_format (str): Input format (json, csv, xml)
        output_format (str): Output format (json, csv, xml)
    
    Returns:
        Dict[str, Any]: Transformed data
    """
    if not data or not isinstance(data, str):
        return {
            "success": False,
            "error": "Data must be a non-empty string"
        }
    
    if input_format not in ["json", "csv", "xml"]:
        return {
            "success": False,
            "error": f"Unsupported input format: {input_format}. "
                     "Supported formats: json, csv, xml"
        }
    
    if output_format not in ["json", "csv", "xml"]:
        return {
            "success": False,
            "error": f"Unsupported output format: {output_format}. "
                     "Supported formats: json, csv, xml"
        }
    
    try:
        import json
        import csv
        import io
        
        # Parse input data
        if input_format == "json":
            parsed_data = json.loads(data)
        elif input_format == "csv":
            reader = csv.DictReader(io.StringIO(data))
            parsed_data = list(reader)
        elif input_format == "xml":
            # Simple XML parsing (for demo purposes)
            return {
                "success": False,
                "error": "XML parsing not implemented in this example"
            }
        
        # Transform to output format
        if output_format == "json":
            output_data = json.dumps(parsed_data, indent=2)
        elif output_format == "csv":
            if isinstance(parsed_data, list) and parsed_data:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=parsed_data[0].keys())
                writer.writeheader()
                writer.writerows(parsed_data)
                output_data = output.getvalue()
            else:
                return {
                    "success": False,
                    "error": "Cannot convert to CSV: data is not a list of dictionaries"
                }
        elif output_format == "xml":
            return {
                "success": False,
                "error": "XML output not implemented in this example"
            }
        
        return {
            "success": True,
            "input_format": input_format,
            "output_format": output_format,
            "transformed_data": output_data,
            "original_size": len(data),
            "transformed_size": len(output_data)
        }
    
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parsing error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Transformation failed: {str(e)}"
        }


@tool(
    name="url_shortener",
    description="Shorten URLs using a simple hash-based approach",
    version="1.0.0"
)
def url_shortener(
    url: str,
    custom_alias: Optional[str] = None
) -> Dict[str, str]:
    """
    Shorten URLs using a simple hash-based approach.
    
    Args:
        url (str): The URL to shorten
        custom_alias (str, optional): Custom short alias
    
    Returns:
        Dict[str, str]: Shortened URL information
    """
    import hashlib
    import re
    
    # Basic URL validation
    url_pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
    if not re.match(url_pattern, url):
        return {
            "success": "false",
            "error": "Invalid URL format"
        }
    
    try:
        if custom_alias:
            # Use custom alias if provided
            short_code = custom_alias
        else:
            # Generate hash-based short code
            hash_object = hashlib.md5(url.encode())
            short_code = hash_object.hexdigest()[:8]
        
        # Create shortened URL (mock service)
        base_url = "https://short.ly"
        short_url = f"{base_url}/{short_code}"
        
        return {
            "success": "true",
            "original_url": url,
            "short_url": short_url,
            "short_code": short_code,
            "alias": custom_alias or "auto-generated"
        }
    
    except Exception as e:
        return {
            "success": "false",
            "error": f"URL shortening failed: {str(e)}"
        }


@tool(
    name="password_generator",
    description="Generate secure passwords with customizable options",
    version="1.0.0"
)
def password_generator(
    length: int = 12,
    include_symbols: bool = True,
    include_numbers: bool = True,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    exclude_ambiguous: bool = True
) -> Dict[str, Any]:
    """
    Generate secure passwords with customizable options.
    
    Args:
        length (int): Password length (default: 12, min: 4, max: 128)
        include_symbols (bool): Include special symbols (default: True)
        include_numbers (bool): Include numbers (default: True)
        include_uppercase (bool): Include uppercase letters (default: True)
        include_lowercase (bool): Include lowercase letters (default: True)
        exclude_ambiguous (bool): Exclude ambiguous characters (default: True)
    
    Returns:
        Dict[str, Any]: Generated password and metadata
    """
    import random
    import string
    
    # Validate length
    if length < 4 or length > 128:
        return {
            "success": False,
            "error": "Password length must be between 4 and 128 characters"
        }
    
    # Check if at least one character type is enabled
    if not any([include_symbols, include_numbers, include_uppercase, include_lowercase]):
        return {
            "success": False,
            "error": "At least one character type must be enabled"
        }
    
    try:
        # Define character sets
        characters = ""
        
        if include_lowercase:
            characters += string.ascii_lowercase
        if include_uppercase:
            characters += string.ascii_uppercase
        if include_numbers:
            characters += string.digits
        if include_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Remove ambiguous characters if requested
        if exclude_ambiguous:
            ambiguous_chars = "0O1lI"
            characters = ''.join(c for c in characters if c not in ambiguous_chars)
        
        # Ensure at least one character from each enabled type
        password_parts = []
        
        if include_lowercase:
            password_parts.append(random.choice(string.ascii_lowercase))
        if include_uppercase:
            password_parts.append(random.choice(string.ascii_uppercase))
        if include_numbers:
            password_parts.append(random.choice(string.digits))
        if include_symbols:
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if exclude_ambiguous:
                symbols = ''.join(c for c in symbols if c not in ambiguous_chars)
            password_parts.append(random.choice(symbols))
        
        # Fill remaining length with random characters
        remaining_length = length - len(password_parts)
        for _ in range(remaining_length):
            password_parts.append(random.choice(characters))
        
        # Shuffle the password
        random.shuffle(password_parts)
        password = ''.join(password_parts)
        
        # Calculate password strength
        strength_score = 0
        if include_lowercase:
            strength_score += 1
        if include_uppercase:
            strength_score += 1
        if include_numbers:
            strength_score += 1
        if include_symbols:
            strength_score += 1
        if length >= 12:
            strength_score += 1
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(strength_score, len(strength_levels) - 1)]
        
        return {
            "success": True,
            "password": password,
            "length": len(password),
            "character_types": {
                "lowercase": include_lowercase,
                "uppercase": include_uppercase,
                "numbers": include_numbers,
                "symbols": include_symbols
            },
            "exclude_ambiguous": exclude_ambiguous,
            "strength": strength,
            "strength_score": strength_score
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Password generation failed: {str(e)}"
        }


# Example usage
if __name__ == "__main__":
    # Test text analyzer
    print("Testing text analyzer:")
    result = text_analyzer("This is a great product! I love it.", "sentiment")
    print(result)
    
    # Test data transformer
    print("\nTesting data transformer:")
    json_data = '[{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]'
    result = data_transformer(json_data, "json", "csv")
    print(result)
    
    # Test URL shortener
    print("\nTesting URL shortener:")
    result = url_shortener("https://www.example.com/very/long/url/path")
    print(result)
    
    # Test password generator
    print("\nTesting password generator:")
    result = password_generator(length=16, exclude_ambiguous=True)
    print(result)
