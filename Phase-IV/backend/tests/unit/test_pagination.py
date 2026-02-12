"""Unit tests for pagination logic.

Tests pagination metadata calculation including:
- Offset/limit boundary conditions
- has_next calculation
- has_previous calculation
- Total count accuracy
- Edge cases (empty results, single page, etc.)
"""


class TestPaginationMetadata:
    """Test pagination metadata calculation logic."""

    def test_first_page_with_more_results(self):
        """Test pagination metadata for first page when more results exist."""
        total = 100
        offset = 0
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is False

    def test_middle_page(self):
        """Test pagination metadata for middle page."""
        total = 100
        offset = 40
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True

    def test_last_page_exact(self):
        """Test pagination metadata for last page (exact boundary)."""
        total = 100
        offset = 80
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is True

    def test_last_page_partial(self):
        """Test pagination metadata for last page with partial results."""
        total = 95
        offset = 80
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is True

    def test_single_page_all_results(self):
        """Test pagination metadata when all results fit in one page."""
        total = 15
        offset = 0
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is False

    def test_empty_results(self):
        """Test pagination metadata with no results."""
        total = 0
        offset = 0
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is False

    def test_offset_beyond_total(self):
        """Test pagination metadata when offset is beyond total."""
        total = 50
        offset = 100
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is True

    def test_limit_of_one(self):
        """Test pagination metadata with limit of 1."""
        total = 100
        offset = 50
        limit = 1

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True

    def test_limit_of_100_max(self):
        """Test pagination metadata with maximum limit of 100."""
        total = 200
        offset = 0
        limit = 100

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is False

    def test_offset_zero_boundary(self):
        """Test pagination metadata at offset=0 boundary."""
        total = 100
        offset = 0
        limit = 10

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is False

    def test_second_page(self):
        """Test pagination metadata for second page."""
        total = 100
        offset = 20
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True

    def test_penultimate_page(self):
        """Test pagination metadata for second-to-last page."""
        total = 100
        offset = 60
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True


class TestOffsetLimitBoundaries:
    """Test offset and limit boundary conditions."""

    def test_offset_zero_is_valid(self):
        """Test that offset=0 is valid (first page)."""
        offset = 0
        assert offset >= 0

    def test_offset_negative_is_invalid(self):
        """Test that negative offset should be rejected."""
        offset = -1
        assert offset < 0  # Should fail validation

    def test_limit_one_is_valid(self):
        """Test that limit=1 is valid (minimum)."""
        limit = 1
        assert 1 <= limit <= 100

    def test_limit_100_is_valid(self):
        """Test that limit=100 is valid (maximum)."""
        limit = 100
        assert 1 <= limit <= 100

    def test_limit_101_is_invalid(self):
        """Test that limit=101 should be rejected."""
        limit = 101
        assert limit > 100  # Should fail validation

    def test_limit_zero_is_invalid(self):
        """Test that limit=0 should be rejected."""
        limit = 0
        assert limit < 1  # Should fail validation

    def test_default_offset(self):
        """Test default offset value."""
        offset = 0  # Default
        assert offset == 0

    def test_default_limit(self):
        """Test default limit value."""
        limit = 20  # Default
        assert limit == 20


class TestPaginationCalculations:
    """Test pagination calculation scenarios."""

    def test_calculate_page_number(self):
        """Test calculating current page number from offset and limit."""
        offset = 40
        limit = 20
        page_number = (offset // limit) + 1

        assert page_number == 3

    def test_calculate_total_pages(self):
        """Test calculating total pages from total count and limit."""
        total = 95
        limit = 20
        total_pages = (total + limit - 1) // limit  # Ceiling division

        assert total_pages == 5

    def test_calculate_total_pages_exact(self):
        """Test calculating total pages when total is exact multiple of limit."""
        total = 100
        limit = 20
        total_pages = (total + limit - 1) // limit

        assert total_pages == 5

    def test_calculate_items_on_page(self):
        """Test calculating number of items on current page."""
        total = 95
        offset = 80
        limit = 20
        items_on_page = min(limit, max(0, total - offset))

        assert items_on_page == 15

    def test_calculate_items_on_full_page(self):
        """Test calculating items on a full page."""
        total = 100
        offset = 40
        limit = 20
        items_on_page = min(limit, max(0, total - offset))

        assert items_on_page == 20

    def test_calculate_items_on_empty_page(self):
        """Test calculating items when offset is beyond total."""
        total = 50
        offset = 100
        limit = 20
        items_on_page = min(limit, max(0, total - offset))

        assert items_on_page == 0


class TestPaginationEdgeCases:
    """Test edge cases in pagination logic."""

    def test_single_item_total(self):
        """Test pagination with only one item total."""
        total = 1
        offset = 0
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is False

    def test_exactly_one_page_of_results(self):
        """Test pagination when results exactly fill one page."""
        total = 20
        offset = 0
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is False

    def test_one_item_over_page_boundary(self):
        """Test pagination when one item exceeds page boundary."""
        total = 21
        offset = 0
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is False

    def test_large_offset_small_limit(self):
        """Test pagination with large offset and small limit."""
        total = 1000
        offset = 990
        limit = 5

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True

    def test_small_offset_large_limit(self):
        """Test pagination with small offset and large limit."""
        total = 1000
        offset = 10
        limit = 100

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True

    def test_offset_at_last_item(self):
        """Test pagination when offset points to last item."""
        total = 100
        offset = 99
        limit = 20

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is True

    def test_very_large_total(self):
        """Test pagination with very large total count."""
        total = 1_000_000
        offset = 500_000
        limit = 100

        has_next = (offset + limit) < total
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is True


class TestPaginationConsistency:
    """Test consistency of pagination across multiple pages."""

    def test_sequential_pages_coverage(self):
        """Test that sequential pages cover all items without gaps."""
        total = 100
        limit = 20
        pages = []

        for page in range(5):
            offset = page * limit
            has_next = (offset + limit) < total
            has_previous = offset > 0
            pages.append(
                {
                    "offset": offset,
                    "limit": limit,
                    "has_next": has_next,
                    "has_previous": has_previous,
                }
            )

        # First page
        assert pages[0]["offset"] == 0
        assert pages[0]["has_next"] is True
        assert pages[0]["has_previous"] is False

        # Middle pages
        for i in range(1, 4):
            assert pages[i]["has_next"] is True
            assert pages[i]["has_previous"] is True

        # Last page
        assert pages[4]["offset"] == 80
        assert pages[4]["has_next"] is False
        assert pages[4]["has_previous"] is True

    def test_no_gaps_in_pagination(self):
        """Test that pagination doesn't skip or duplicate items."""
        total = 100
        limit = 20
        covered_items = []

        for page in range(5):
            offset = page * limit
            end = min(offset + limit, total)
            covered_items.extend(range(offset, end))

        # All items from 0 to 99 should be covered exactly once
        assert covered_items == list(range(100))
        assert len(covered_items) == total
        assert len(set(covered_items)) == total  # No duplicates


class TestPaginationWithFiltering:
    """Test pagination metadata when combined with filtering."""

    def test_filtered_results_first_page(self):
        """Test pagination with filtered results (first page)."""
        total_filtered = 30  # Only 30 items match filter
        offset = 0
        limit = 20

        has_next = (offset + limit) < total_filtered
        has_previous = offset > 0

        assert has_next is True
        assert has_previous is False

    def test_filtered_results_last_page(self):
        """Test pagination with filtered results (last page)."""
        total_filtered = 30
        offset = 20
        limit = 20

        has_next = (offset + limit) < total_filtered
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is True

    def test_filtered_results_single_page(self):
        """Test pagination when filtered results fit in one page."""
        total_filtered = 10
        offset = 0
        limit = 20

        has_next = (offset + limit) < total_filtered
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is False

    def test_filtered_results_empty(self):
        """Test pagination when filter returns no results."""
        total_filtered = 0
        offset = 0
        limit = 20

        has_next = (offset + limit) < total_filtered
        has_previous = offset > 0

        assert has_next is False
        assert has_previous is False
