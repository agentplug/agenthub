"""File operations tools."""

import os
from pathlib import Path
from typing import Dict, Any

from ...decorator import tool


@tool(
    name="file_operations",
    description="Read, write, and manipulate files on the local system",
    version="1.0.0"
)
def file_operations(operation: str, path: str, content: str = None) -> Dict[str, Any]:
    """
    Perform file operations on the local system.

    Args:
        operation (str): The operation to perform (read, write, append, delete, exists, list)
        path (str): The file or directory path
        content (str, optional): Content to write (for write/append operations)

    Returns:
        Dict[str, Any]: Operation result with status and data
    """
    try:
        path_obj = Path(path)
        
        if operation == "read":
            if not path_obj.exists():
                return {"success": False, "error": "File does not exist"}
            
            if not path_obj.is_file():
                return {"success": False, "error": "Path is not a file"}
            
            try:
                with open(path_obj, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "success": True,
                    "operation": "read",
                    "path": str(path_obj),
                    "content": content,
                    "size": len(content)
                }
            except UnicodeDecodeError:
                # Try reading as binary
                with open(path_obj, 'rb') as f:
                    content = f.read()
                return {
                    "success": True,
                    "operation": "read",
                    "path": str(path_obj),
                    "content": content.decode('utf-8', errors='ignore'),
                    "size": len(content),
                    "note": "File was read as binary and decoded with errors ignored"
                }
        
        elif operation == "write":
            if content is None:
                return {"success": False, "error": "Content is required for write operation"}
            
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "operation": "write",
                "path": str(path_obj),
                "size": len(content)
            }
        
        elif operation == "append":
            if content is None:
                return {"success": False, "error": "Content is required for append operation"}
            
            # Create parent directories if they don't exist
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path_obj, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "operation": "append",
                "path": str(path_obj),
                "appended_size": len(content)
            }
        
        elif operation == "delete":
            if not path_obj.exists():
                return {"success": False, "error": "Path does not exist"}
            
            if path_obj.is_file():
                path_obj.unlink()
                return {
                    "success": True,
                    "operation": "delete",
                    "path": str(path_obj),
                    "type": "file"
                }
            elif path_obj.is_dir():
                path_obj.rmdir()
                return {
                    "success": True,
                    "operation": "delete",
                    "path": str(path_obj),
                    "type": "directory"
                }
            else:
                return {"success": False, "error": "Path is neither file nor directory"}
        
        elif operation == "exists":
            return {
                "success": True,
                "operation": "exists",
                "path": str(path_obj),
                "exists": path_obj.exists(),
                "is_file": path_obj.is_file() if path_obj.exists() else False,
                "is_dir": path_obj.is_dir() if path_obj.exists() else False
            }
        
        elif operation == "list":
            if not path_obj.exists():
                return {"success": False, "error": "Path does not exist"}
            
            if not path_obj.is_dir():
                return {"success": False, "error": "Path is not a directory"}
            
            try:
                items = []
                for item in path_obj.iterdir():
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "is_file": item.is_file(),
                        "is_dir": item.is_dir(),
                        "size": item.stat().st_size if item.is_file() else None
                    })
                
                return {
                    "success": True,
                    "operation": "list",
                    "path": str(path_obj),
                    "items": items,
                    "count": len(items)
                }
            except PermissionError:
                return {"success": False, "error": "Permission denied"}
        
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. "
                         "Supported operations: read, write, append, delete, exists, list"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Operation failed: {str(e)}"
        }
