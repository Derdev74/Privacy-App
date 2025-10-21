# Test Suite

## Running Tests

### All Tests
```bash
cd tests
python test_utils.py
python test_database.py
```

### Using pytest (recommended)
```bash
pip install pytest
pytest tests/
```

## Test Files

- **test_utils.py**: Unit tests for utility functions (validators, extractors, etc.)
- **test_database.py**: Integration tests for database operations

## Requirements

Database tests require:
- Running PostgreSQL instance
- Configured `.env` file with database credentials
- Initialized database schema

## Writing New Tests

Follow these patterns:

```python
def test_feature_name():
    """Test description."""
    # Arrange
    setup_data()

    # Act
    result = function_to_test()

    # Assert
    assert result == expected_value
    print("✓ Test passed")
```
