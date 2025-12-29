"""Tests for Pydantic validation schemas."""

import pytest
from pydantic import ValidationError

from pension_planning_agent.schemas import FireCalculatorInput, FireCalculatorOutput


class TestFireCalculatorInput:
    """Tests for FireCalculatorInput validation."""

    def test_valid_input(self):
        """Test creating input with all valid values."""
        input_data = FireCalculatorInput(
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

        assert input_data.manedslon == 50000.0
        assert input_data.alder == 30
        assert input_data.fire_alder == 55

    def test_negative_salary_fails(self):
        """Test that negative salary raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
                manedslon=-50000.0,  # Invalid
                alder=30,
                pensionInd_ar=60000.0,
                skat_percentage=35.0,
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("manedslon",) for e in errors)

    def test_age_too_young_fails(self):
        """Test that age < 18 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
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

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("alder",) for e in errors)

    def test_age_too_old_fails(self):
        """Test that age > 100 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
                manedslon=50000.0,
                alder=105,  # Invalid: too old
                pensionInd_ar=60000.0,
                skat_percentage=35.0,
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=110,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("alder",) for e in errors)

    def test_fire_age_less_than_current_age_fails(self):
        """Test that FIRE age <= current age raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
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

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("fire_alder",) for e in errors)

    def test_tax_percentage_over_100_fails(self):
        """Test that tax percentage > 100 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
                manedslon=50000.0,
                alder=30,
                pensionInd_ar=60000.0,
                skat_percentage=150.0,  # Invalid: > 100%
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("skat_percentage",) for e in errors)

    def test_negative_pension_contribution_fails(self):
        """Test that negative pension contribution raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
                manedslon=50000.0,
                alder=30,
                pensionInd_ar=-60000.0,  # Invalid: negative
                skat_percentage=35.0,
                forbrugsmal_md=25000.0,
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("pensionInd_ar",) for e in errors)

    def test_zero_consumption_fails(self):
        """Test that zero consumption target raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            FireCalculatorInput(
                manedslon=50000.0,
                alder=30,
                pensionInd_ar=60000.0,
                skat_percentage=35.0,
                forbrugsmal_md=0.0,  # Invalid: must be > 0
                frie_midler=100000.0,
                holding_midler=0.0,
                rate_and_liv=500000.0,
                fire_alder=55,
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("forbrugsmal_md",) for e in errors)


class TestFireCalculatorOutput:
    """Tests for FireCalculatorOutput validation."""

    def test_valid_output(self):
        """Test creating output with valid values."""
        output = FireCalculatorOutput(opsparing_ar=50000.0, result=1000000.0)

        assert output.opsparing_ar == 50000.0
        assert output.result == 1000000.0

    def test_negative_result_allowed(self):
        """Test that negative result (deficit) is allowed."""
        output = FireCalculatorOutput(opsparing_ar=50000.0, result=-100000.0)

        assert output.result == -100000.0
