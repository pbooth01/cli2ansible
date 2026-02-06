"""Unit tests for the math_lib module."""

import pytest

from src.math_lib import add, multiply, subtract


class TestAdd:
    """Test cases for the add function."""

    def test_add_positive_numbers(self):
        """Test adding two positive numbers."""
        assert add(2.0, 3.0) == 5.0
        assert add(10.5, 5.5) == 16.0

    def test_add_negative_numbers(self):
        """Test adding two negative numbers."""
        assert add(-2.0, -3.0) == -5.0
        assert add(-10.5, -5.5) == -16.0

    def test_add_mixed_signs(self):
        """Test adding numbers with different signs."""
        assert add(5.0, -3.0) == 2.0
        assert add(-5.0, 3.0) == -2.0

    def test_add_with_zero(self):
        """Test adding zero to a number."""
        assert add(0.0, 0.0) == 0.0
        assert add(5.0, 0.0) == 5.0
        assert add(0.0, 5.0) == 5.0

    def test_add_large_numbers(self):
        """Test adding large numbers."""
        assert add(1e10, 1e10) == 2e10
        assert add(999999.99, 0.01) == 1000000.0

    def test_add_small_numbers(self):
        """Test adding very small numbers."""
        result = add(0.1, 0.2)
        assert abs(result - 0.3) < 1e-10  # Handle floating point precision

    def test_add_integers_as_floats(self):
        """Test that integers work as inputs."""
        assert add(1, 2) == 3
        assert add(100, 200) == 300


class TestSubtract:
    """Test cases for the subtract function."""

    def test_subtract_positive_numbers(self):
        """Test subtracting positive numbers."""
        assert subtract(5.0, 3.0) == 2.0
        assert subtract(10.5, 5.5) == 5.0

    def test_subtract_negative_numbers(self):
        """Test subtracting negative numbers."""
        assert subtract(-5.0, -3.0) == -2.0
        assert subtract(-10.0, -5.0) == -5.0

    def test_subtract_mixed_signs(self):
        """Test subtracting numbers with different signs."""
        assert subtract(5.0, -3.0) == 8.0
        assert subtract(-5.0, 3.0) == -8.0

    def test_subtract_with_zero(self):
        """Test subtracting zero and from zero."""
        assert subtract(0.0, 0.0) == 0.0
        assert subtract(5.0, 0.0) == 5.0
        assert subtract(0.0, 5.0) == -5.0

    def test_subtract_same_number(self):
        """Test subtracting a number from itself."""
        assert subtract(5.0, 5.0) == 0.0
        assert subtract(-5.0, -5.0) == 0.0

    def test_subtract_large_numbers(self):
        """Test subtracting large numbers."""
        assert subtract(1e10, 1e9) == 9e9
        assert subtract(1000000.0, 0.01) == 999999.99

    def test_subtract_integers_as_floats(self):
        """Test that integers work as inputs."""
        assert subtract(10, 3) == 7
        assert subtract(100, 50) == 50


class TestMultiply:
    """Test cases for the multiply function."""

    def test_multiply_positive_numbers(self):
        """Test multiplying two positive numbers."""
        assert multiply(2.0, 3.0) == 6.0
        assert multiply(5.5, 2.0) == 11.0

    def test_multiply_negative_numbers(self):
        """Test multiplying two negative numbers."""
        assert multiply(-2.0, -3.0) == 6.0
        assert multiply(-5.0, -2.0) == 10.0

    def test_multiply_mixed_signs(self):
        """Test multiplying numbers with different signs."""
        assert multiply(5.0, -3.0) == -15.0
        assert multiply(-5.0, 3.0) == -15.0

    def test_multiply_with_zero(self):
        """Test multiplying by zero."""
        assert multiply(0.0, 0.0) == 0.0
        assert multiply(5.0, 0.0) == 0.0
        assert multiply(0.0, 5.0) == 0.0

    def test_multiply_with_one(self):
        """Test multiplying by one (identity)."""
        assert multiply(5.0, 1.0) == 5.0
        assert multiply(1.0, 5.0) == 5.0
        assert multiply(-5.0, 1.0) == -5.0

    def test_multiply_large_numbers(self):
        """Test multiplying large numbers."""
        assert multiply(1e5, 1e5) == 1e10
        assert multiply(1000.0, 1000.0) == 1000000.0

    def test_multiply_small_numbers(self):
        """Test multiplying very small numbers."""
        result = multiply(0.1, 0.1)
        assert abs(result - 0.01) < 1e-10  # Handle floating point precision

    def test_multiply_integers_as_floats(self):
        """Test that integers work as inputs."""
        assert multiply(3, 4) == 12
        assert multiply(10, 10) == 100

    def test_multiply_fractions(self):
        """Test multiplying fractional numbers."""
        assert multiply(0.5, 0.5) == 0.25
        assert multiply(2.5, 4.0) == 10.0

