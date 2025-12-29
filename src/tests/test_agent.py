"""Tests for the FIRE Pension Planning Agent."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from pension_planning_agent.agent import (
    convert_percentage_to_float,
    generate_final_message,
    fire_calculator,
)


class TestConvertPercentageToFloat:
    """Tests for percentage conversion."""

    @pytest.mark.asyncio
    async def test_percentage_greater_than_one(self):
        """Test converting percentage value > 1."""
        result = await convert_percentage_to_float(33.0)
        assert result == 0.33

    @pytest.mark.asyncio
    async def test_percentage_less_than_one(self):
        """Test that values < 1 are returned as-is."""
        result = await convert_percentage_to_float(0.33)
        assert result == 0.33

    @pytest.mark.asyncio
    async def test_hundred_percent(self):
        """Test converting 100%."""
        result = await convert_percentage_to_float(100.0)
        assert result == 1.0


class TestGenerateFinalMessage:
    """Tests for final message generation."""

    def test_valid_response(self):
        """Test message generation with valid response."""
        response = {"opsparing_ar": 93788.0, "result": -5161782.0}
        message = generate_final_message(response)

        assert "93,788 kr" in message
        assert "-5,161,782 kr" in message
        assert "Hvis du sparer" in message
        assert "penly.dk" in message

    def test_none_response(self):
        """Test message generation with None response."""
        message = generate_final_message(None)
        assert "kunne ikke finde nogle informationer" in message

    def test_empty_dict_response(self):
        """Test message generation with empty dict."""
        message = generate_final_message({})
        assert "kunne ikke finde nogle informationer" in message

    def test_missing_opsparing_ar(self):
        """Test message generation with missing opsparing_ar."""
        response = {"result": 100000.0}
        message = generate_final_message(response)
        assert "kunne ikke beregne pensionsplanen" in message

    def test_missing_result(self):
        """Test message generation with missing result."""
        response = {"opsparing_ar": 100000.0}
        message = generate_final_message(response)
        assert "kunne ikke beregne pensionsplanen" in message

    def test_invalid_type_response(self):
        """Test message generation with invalid type."""
        message = generate_final_message("not a dict")
        assert "kunne ikke finde nogle informationer" in message


class TestFireCalculator:
    """Tests for the FIRE calculator function."""

    @pytest.mark.asyncio
    async def test_valid_input_successful_api_call(self):
        """Test calculator with valid inputs and successful API response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "opsparing_ar": 50000.0,
            "result": 1000000.0,
        }
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                return_value=mock_response
            )

            result = await fire_calculator(
                manedslon=50000.0,
                alder=30,
                pensionInd_ar=60000.0,
                skat_percentage=35.0,
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

            assert "50,000 kr" in result
            assert "1,000,000 kr" in result

    @pytest.mark.asyncio
    async def test_invalid_age_validation(self):
        """Test calculator with invalid age (< 18)."""
        result = await fire_calculator(
            manedslon=50000.0,
            alder=15,  # Invalid: too young
            pensionInd_ar=60000.0,
            skat_percentage=35.0,
            forbrugsmal_md=25000.0,
            frie_midler=100000.0,
            holding_midler=0.0,
            rate_and_liv=500000.0,
            fire_alder=55,
        )

        assert "Invalid input parameters" in result
        assert "alder" in result

    @pytest.mark.asyncio
    async def test_fire_age_less_than_current_age(self):
        """Test calculator with FIRE age less than current age."""
        result = await fire_calculator(
            manedslon=50000.0,
            alder=50,
            pensionInd_ar=60000.0,
            skat_percentage=35.0,
            forbrugsmal_md=25000.0,
            frie_midler=100000.0,
            holding_midler=0.0,
            rate_and_liv=500000.0,
            fire_alder=45,  # Invalid: less than current age
        )

        assert "Invalid input parameters" in result
        assert "fire_alder" in result

    @pytest.mark.asyncio
    async def test_negative_salary(self):
        """Test calculator with negative salary."""
        result = await fire_calculator(
            manedslon=-50000.0,  # Invalid: negative
            alder=30,
            pensionInd_ar=60000.0,
            skat_percentage=35.0,
            forbrugsmal_md=25000.0,
            frie_midler=100000.0,
            holding_midler=0.0,
            rate_and_liv=500000.0,
            fire_alder=55,
        )

        assert "Invalid input parameters" in result
        assert "manedslon" in result

    @pytest.mark.asyncio
    async def test_api_timeout(self):
        """Test calculator behavior on API timeout."""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=__import__("httpx").TimeoutException("Timeout")
            )

            result = await fire_calculator(
                manedslon=50000.0,
                alder=30,
                pensionInd_ar=60000.0,
                skat_percentage=35.0,
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

            assert "timed out" in result.lower()

    @pytest.mark.asyncio
    async def test_api_http_error(self):
        """Test calculator behavior on API HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                side_effect=__import__("httpx").HTTPStatusError(
                    "Error", request=Mock(), response=mock_response
                )
            )

            result = await fire_calculator(
                manedslon=50000.0,
                alder=30,
                pensionInd_ar=60000.0,
                skat_percentage=35.0,
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

            assert "Failed to calculate pension plan" in result
