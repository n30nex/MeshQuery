"""Unit tests for distance calculation fixes."""
import pytest
from malla.utils.geo_utils import calculate_distance


class TestDistanceCalculation:
    """Test suite for haversine distance calculations."""
    
    def test_calculate_distance_zero(self):
        """Test distance calculation for same point."""
        distance = calculate_distance(0, 0, 0, 0)
        assert distance == 0.0
    
    def test_calculate_distance_known_values(self):
        """Test distance calculation for known locations."""
        # Distance between San Francisco and Los Angeles
        # SF: 37.7749° N, 122.4194° W
        # LA: 34.0522° N, 118.2437° W
        distance = calculate_distance(37.7749, -122.4194, 34.0522, -118.2437)
        
        # Expected distance is approximately 559 km
        assert 550 < distance < 570, f"Expected ~559 km, got {distance} km"
    
    def test_calculate_distance_equator(self):
        """Test distance calculation along equator."""
        # 1 degree longitude at equator ≈ 111.32 km
        distance = calculate_distance(0, 0, 0, 1)
        assert 110 < distance < 112, f"Expected ~111.32 km, got {distance} km"
    
    def test_calculate_distance_north_south(self):
        """Test distance calculation north-south."""
        # 1 degree latitude ≈ 111.32 km everywhere
        distance = calculate_distance(0, 0, 1, 0)
        assert 110 < distance < 112, f"Expected ~111.32 km, got {distance} km"
    
    def test_calculate_distance_symmetric(self):
        """Test that distance is symmetric (A to B = B to A)."""
        lat1, lon1 = 40.7128, -74.0060  # New York
        lat2, lon2 = 51.5074, -0.1278   # London
        
        distance1 = calculate_distance(lat1, lon1, lat2, lon2)
        distance2 = calculate_distance(lat2, lon2, lat1, lon1)
        
        assert abs(distance1 - distance2) < 0.01, \
            f"Distance should be symmetric: {distance1} vs {distance2}"
    
    def test_calculate_distance_positive(self):
        """Test that distance is always positive."""
        # Various random coordinates
        coords = [
            (45.0, -93.0, 29.7, -95.4),  # Minneapolis to Houston
            (-33.9, 151.2, 35.7, 139.7),  # Sydney to Tokyo
            (52.5, 13.4, 48.9, 2.4),      # Berlin to Paris
        ]
        
        for lat1, lon1, lat2, lon2 in coords:
            distance = calculate_distance(lat1, lon1, lat2, lon2)
            assert distance >= 0, f"Distance should be non-negative, got {distance}"


class TestLongestLinksIntegration:
    """Integration tests for longest links functionality."""
    
    def test_links_have_distance_when_gps_available(self, mock_db_with_positions):
        """Test that links have distance_km when nodes have GPS data."""
        # This would require a mock database
        # Placeholder for future implementation
        pass
    
    def test_links_handle_missing_gps_gracefully(self, mock_db_without_positions):
        """Test that links handle missing GPS data gracefully."""
        # This would require a mock database
        # Placeholder for future implementation
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

