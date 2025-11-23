from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([
        Frank2LowestPeriodsCount(coordinator, entry),
        Frank2HighestPeriodsCount(coordinator, entry)
    ])

class Frank2LowestPeriodsCount(NumberEntity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._entry = entry
        self._value = entry.data.get("lowest_periods_count", 14)

    @property
    def name(self):
        return "Frank2 Lowest Periods Count"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_lowest_periods_count"

    @property
    def native_value(self):
        return self._value

    @property
    def native_min_value(self):
        return 4

    @property
    def native_max_value(self):
        return 24

    @property
    def native_step(self):
        return 1

    async def async_set_native_value(self, value):
        self._value = int(value)
        new_data = self._entry.data.copy()
        new_data["lowest_periods_count"] = self._value
        self.coordinator.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.coordinator.async_request_refresh()

class Frank2HighestPeriodsCount(NumberEntity):
    def __init__(self, coordinator, entry):
        self.coordinator = coordinator
        self._entry = entry
        self._value = entry.data.get("highest_periods_count", 8)

    @property
    def name(self):
        return "Frank2 Highest Periods Count"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_highest_periods_count"

    @property
    def native_value(self):
        return self._value

    @property
    def native_min_value(self):
        return 4

    @property
    def native_max_value(self):
        return 24

    @property
    def native_step(self):
        return 1

    async def async_set_native_value(self, value):
        self._value = int(value)
        new_data = self._entry.data.copy()
        new_data["highest_periods_count"] = self._value
        self.coordinator.hass.config_entries.async_update_entry(self._entry, data=new_data)
        await self.coordinator.async_request_refresh()