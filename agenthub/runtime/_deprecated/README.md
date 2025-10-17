# Deprecated Runtime Code

This directory contains deprecated monolithic implementations that have been refactored into modular architectures.

## Files

- **process_manager_monolithic.py**: Original monolithic process_manager.py file (960+ lines)
  - This was the single-file implementation before refactoring
  - Replaced by the `process_manager/` package with modular architecture
  - Python now loads from `process_manager/__init__.py` (package takes precedence)
  - Kept for reference only

## Refactoring Complete

The ProcessManager has been successfully refactored from a monolithic 960-line file into a clean modular architecture:

```
process_manager/
├── __init__.py              # Package entry point
├── manager.py               # Main orchestration
├── executor.py              # Process execution
├── communication.py         # WebSocket management
├── log_streaming.py         # Real-time log capture
└── monitoring_adapter.py    # Optional monitoring
```

## Verification

- ✅ All 11 ProcessManager tests passing
- ✅ Backward compatibility maintained
- ✅ New architecture in production use
- ✅ Python loads from package (not deprecated file)

## Removal

This deprecated code will be removed in version 3.0.0.
