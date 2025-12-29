"""Pydantic models for input validation and type safety."""

from pydantic import BaseModel, Field, field_validator


class FireCalculatorInput(BaseModel):
    """Input schema for the FIRE calculator."""

    manedslon: float = Field(gt=0, description="Monthly salary in DKK")
    alder: int = Field(ge=18, le=100, description="Current age")
    pensionInd_ar: float = Field(
        ge=0, description="Annual pension contributions in DKK"
    )
    skat_percentage: float = Field(ge=0, le=100, description="Tax percentage after AMB")
    forbrugsmal_md: float = Field(gt=0, description="Monthly consumption target in DKK")
    frie_midler: float = Field(ge=0, description="Initial free funds balance in DKK")
    holding_midler: float = Field(ge=0, description="Initial holding balance in DKK")
    rate_and_liv: float = Field(ge=0, description="Rate and annuity pension in DKK")
    fire_alder: int = Field(ge=18, le=100, description="Target FIRE age")

    @field_validator("fire_alder")
    @classmethod
    def fire_age_must_be_greater_than_current_age(cls, v: int, info) -> int:
        """Validate that FIRE age is greater than current age."""
        if "alder" in info.data and v <= info.data["alder"]:
            raise ValueError("FIRE age must be greater than current age")
        return v


class FireCalculatorOutput(BaseModel):
    """Output schema for the FIRE calculator."""

    opsparing_ar: float = Field(description="Annual savings amount in DKK")
    result: float = Field(description="Net profit in free funds at age 95 in DKK")
