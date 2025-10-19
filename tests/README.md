# MeshQuery Tests

## Running Tests

### Integration Tests (Recommended)
Run integration tests against the running Docker containers:

```bash
python tests/test_fixes.py
```

This will test:
- Pagination on all API endpoints
- Longest links with distance calculations
- Dashboard analytics
- Map locations and traceroute links
- All frontend pages

### Unit Tests
Unit tests require the `malla` package to be installed. Run them inside Docker:

```bash
docker-compose exec malla-web python -m pytest tests/unit/ -v
```

Or install the package locally first:

```bash
pip install -e .
pytest tests/unit/ -v
```

## Test Coverage

### Integration Tests (`tests/test_fixes.py`)
- ✅ API pagination (packets, nodes, traceroute)
- ✅ Longest links functionality
- ✅ Dashboard analytics with top nodes
- ✅ Map locations and links
- ✅ Frontend page loading

### Unit Tests (`tests/unit/test_distance_calculation.py`)
- ✅ Haversine distance formula accuracy
- ✅ Edge cases (same point, equator, poles)
- ✅ Symmetry property
- ✅ Known real-world distances

## Test Requirements

### Prerequisites
- Docker and Docker Compose installed
- Services running (`docker-compose up -d`)
- At least 1-2 minutes of data collection for meaningful tests

### Python Dependencies
- `requests` - for API testing
- `pytest` - for unit testing
- `malla` package - installed inside Docker containers

## Continuous Integration

For CI/CD pipelines, use this sequence:

```bash
# Start services
docker-compose up -d

# Wait for services to be ready
sleep 60

# Run integration tests
python tests/test_fixes.py

# Run unit tests inside Docker
docker-compose exec -T malla-web python -m pytest tests/unit/ -v

# Cleanup
docker-compose down
```

## Writing New Tests

### Integration Test Example
```python
def test_new_feature(runner: TestRunner):
    """Test a new feature."""
    resp = requests.get(f"{BASE_URL}/api/new-feature")
    runner.test("New feature responds", resp.status_code == 200)
    
    data = resp.json()
    runner.test("New feature has data", len(data) > 0)
```

### Unit Test Example
```python
def test_new_function():
    """Test a new utility function."""
    from malla.utils import new_function
    
    result = new_function(input_data)
    assert result == expected_output
```

## Debugging Failed Tests

1. **Check service status**: `docker-compose ps`
2. **View logs**: `docker-compose logs malla-web malla-capture`
3. **Verify database**: 
   ```bash
   docker-compose exec postgres psql -U malla -d malla -c "SELECT COUNT(*) FROM packet_history;"
   ```
4. **Test API manually**: `curl http://localhost:8080/api/stats`
5. **Check browser console**: Open http://localhost:8080 and check for JS errors

## Performance Benchmarks

Expected response times (with ~1000 packets):
- `/api/packets/data`: < 500ms
- `/api/longest-links`: < 2000ms
- `/api/analytics`: < 1500ms
- `/api/locations`: < 1000ms

If tests timeout, check:
- Database query performance
- MQTT ingestion rate
- Docker resource limits

