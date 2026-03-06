# Deprecated Code

This directory contains deprecated code that has been replaced by the new modular architecture.

## Files

- **process_manager_legacy.py**: Original monolithic ProcessManager implementation (960 lines)
  - Replaced by modular architecture in parent directory
  - Kept for reference during migration period
  - Will be removed in future version

## New Modular Architecture

The monolithic ProcessManager has been refactored into focused modules:

- `manager.py`: Main orchestration (ProcessManager class)
- `executor.py`: Process execution logic
- `communication.py`: WebSocket communication management
- `log_streaming.py`: Real-time log capture and filtering
- `monitoring_adapter.py`: Optional monitoring integration

## Migration Status

- ✅ All modules extracted and tested
- ✅ Backward compatibility verified (11/11 tests passing)
- ✅ All imports updated to use new architecture
- ⏳ Legacy code moved to deprecated directory

## Removal Timeline

The legacy code in this directory will be removed in version 3.0.0 after:
1. All integration tests pass
2. Production usage confirms stability
3. Documentation is updated

## References

- Design document: `/docs/.implementation_design/phase3.4_realtime_communication/process_manager_refactoring.md`
- Version: 2.0.0 (refactoring complete)
