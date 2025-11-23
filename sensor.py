from homeassistant.components.sensor import SensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

import logging
from datetime import datetime, timezone

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([
        Frank2AllInSensor(coordinator, entry),
        Frank2CurrentAllInSensor(coordinator, entry),
        Frank2LowestPeriodsCount(coordinator, entry),
        Frank2HighestPeriodsCount(coordinator, entry),
        Frank2HighestPeriodTodaySensor(coordinator, entry),
        Frank2LowestPeriodTodaySensor(coordinator, entry),
        Frank2InHighestPeriod(coordinator, entry),
        Frank2InLowestPeriod(coordinator, entry)
    ])

class Frank2AllInSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Electricity Price"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_all_in"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            _LOGGER.warning("No data available from coordinator")
            return None
        all_prices = []
        for date, points in data.items():
            all_prices.extend([p["price"] for p in points])
        if not all_prices:
            _LOGGER.warning("No prices found in data")
            return None
        avg = round(sum(all_prices) / len(all_prices), 5)
        _LOGGER.debug(f"All In Average price: {avg}")
        return avg

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        all_points = []
        for date, points in data.items():
            all_points.extend(points)
        return {"data": all_points}

class Frank2CurrentAllInSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Current Electricity Price"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_current_all_in"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            _LOGGER.warning("No data available from coordinator")
            return None
        current_time = datetime.now(timezone.utc)
        for date, points in data.items():
            for point in points:
                start = datetime.fromisoformat(point["start"])
                end = datetime.fromisoformat(point["end"])
                if start <= current_time < end:
                    return point["price"]
        _LOGGER.warning("No current price found")
        return None

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        return {}

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
        await self.coordinator.hass.config_entries.async_update_entry(self._entry, data=new_data)

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
        await self.coordinator.hass.config_entries.async_update_entry(self._entry, data=new_data)

class Frank2HighestPeriodTodaySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Highest Period Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_highest_period_today"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return None
        points = data[today_str]
        sorted_points = sorted(points, key=lambda p: p["price"], reverse=True)
        count = self._entry.data.get("highest_periods_count", 8)
        selected = sorted_points[:count]
        if not selected:
            return None
        avg = sum(p["price"] for p in selected) / len(selected)
        return round(avg, 5)

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return {}
        points = data[today_str]
        sorted_points = sorted(points, key=lambda p: p["price"], reverse=True)
        count = self._entry.data.get("highest_periods_count", 8)
        selected = sorted_points[:count]
        return {"data": selected}

class Frank2LowestPeriodTodaySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Lowest Period Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_lowest_period_today"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return None
        points = data[today_str]
        sorted_points = sorted(points, key=lambda p: p["price"])
        count = self._entry.data.get("lowest_periods_count", 14)
        selected = sorted_points[:count]
        if not selected:
            return None
        avg = sum(p["price"] for p in selected) / len(selected)
        return round(avg, 5)

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return {}
        points = data[today_str]
        sorted_points = sorted(points, key=lambda p: p["price"])
        count = self._entry.data.get("lowest_periods_count", 14)
        selected = sorted_points[:count]
        return {"data": selected}

class Frank2InHighestPeriod(BinarySensorEntity, CoordinatorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 In Highest Period Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_in_highest_period"

    @property
    def is_on(self):
        data = self.coordinator.data
        if not data:
            return False
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return False
        points = data[today_str]
        sorted_points = sorted(points, key=lambda p: p["price"], reverse=True)
        count = self._entry.data.get("highest_periods_count", 8)
        selected = sorted_points[:count]
        current_time = datetime.now(timezone.utc)
        for point in selected:
            start = datetime.fromisoformat(point["start"])
            end = datetime.fromisoformat(point["end"])
            if start <= current_time < end:
                return True
        return False

class Frank2InLowestPeriod(BinarySensorEntity, CoordinatorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 In Lowest Period Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_in_lowest_period"

    @property
    def is_on(self):
        data = self.coordinator.data
        if not data:
            return False
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return False
        points = data[today_str]
        sorted_points = sorted(points, key=lambda p: p["price"])
        count = self._entry.data.get("lowest_periods_count", 14)
        selected = sorted_points[:count]
        current_time = datetime.now(timezone.utc)
        for point in selected:
            start = datetime.fromisoformat(point["start"])
            end = datetime.fromisoformat(point["end"])
            if start <= current_time < end:
                return True
        return False