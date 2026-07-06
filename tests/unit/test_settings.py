"""Unit tests for ZEN-europe's concrete settings categories.

These are registered as zen_creator SettingsCategory subclasses (see
zen_europe/settings/) and become queryable as model.settings.<name>.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

import zen_europe.settings  # noqa: F401  (registers the categories)
from zen_creator.utils.settings import Settings


def test_time_settings_defaults() -> None:
    settings = Settings()

    assert settings.time_settings.years_in_rolling_horizon == 2
    assert settings.time_settings.reference_year == 2022


def test_investment_settings_defaults() -> None:
    settings = Settings()

    assert settings.investment_settings.allow_investment is True
    assert settings.investment_settings.knowledge_depreciation_rate == 0.1


def test_settings_override_from_dict() -> None:
    settings = Settings.model_validate(
        {"time_settings": {"years_in_rolling_horizon": 5}}
    )

    assert settings.time_settings.years_in_rolling_horizon == 5
    assert settings.time_settings.reference_year == 2022


def test_settings_rejects_wrong_type() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"time_settings": {"years_in_rolling_horizon": "five"}})


def test_settings_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"time_settings": {"bogus_field": 1}})


def test_config_yaml_loads_time_settings() -> None:
    config_path = Path(__file__).parents[2] / "data" / "config.yaml"
    settings = Settings.load_from_yaml(config_path)

    assert settings.time_settings.reference_year == 2022
    assert settings.time_settings.optimized_years == 15


if __name__ == "__main__":
    pytest.main([__file__])
