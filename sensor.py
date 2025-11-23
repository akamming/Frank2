from homeassistant.components.sensor import SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

import logging
from datetime import datetime, timezone, timedelta

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([
        Frank2AllInSensor(coordinator, entry),
        Frank2CurrentAllInSensor(coordinator, entry),
        Frank2FutureAveragePriceSensor(coordinator, entry),
        Frank2AverageElectricityTodaySensor(coordinator, entry),
        Frank2AverageElectricityTomorrowSensor(coordinator, entry),
        Frank2LowestPeriodsFutureSensor(coordinator, entry),
        Frank2LowestPeriodsTomorrowSensor(coordinator, entry),
        Frank2HighestPeriodsTomorrowSensor(coordinator, entry),
        Frank2PriceDiffFutureSensor(coordinator, entry),
        Frank2HighestPeriodsTodaySensor(coordinator, entry),
        Frank2LowestPeriodsTodaySensor(coordinator, entry),
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

class Frank2FutureAveragePriceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Future Average Price"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_future_average"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            _LOGGER.warning("No data available from coordinator")
            return None
        current_time = datetime.now(timezone.utc)
        future_prices = []
        for date, points in data.items():
            for point in points:
                start = datetime.fromisoformat(point["start"])
                if start > current_time:
                    future_prices.append(point["price"])
        if not future_prices:
            _LOGGER.warning("No future prices found")
            return None
        avg = round(sum(future_prices) / len(future_prices), 5)
        _LOGGER.debug(f"Future Average price: {avg}")
        return avg

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        current_time = datetime.now(timezone.utc)
        future_points = []
        for date, points in data.items():
            for point in points:
                start = datetime.fromisoformat(point["start"])
                if start > current_time:
                    future_points.append(point)
        return {"data": future_points}

class Frank2AverageElectricityTodaySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Average Electricity Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_average_electricity_today"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return None
        points = data[today_str]
        if not points:
            return None
        avg = sum(p["price"] for p in points) / len(points)
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
        return {"data": data[today_str]}

class Frank2AverageElectricityTomorrowSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Average Electricity Tomorrow"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_average_electricity_tomorrow"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return None
        points = data[tomorrow_str]
        if not points:
            return None
        avg = sum(p["price"] for p in points) / len(points)
        return round(avg, 5)

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return {}
        return {"data": data[tomorrow_str]}

class Frank2LowestPeriodsFutureSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Lowest Periods Future"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_lowest_periods_future"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        current_time = datetime.now(timezone.utc)
        future_points = []
        for date, points in data.items():
            for point in points:
                start = datetime.fromisoformat(point["start"])
                if start > current_time:
                    future_points.append(point)
        if not future_points:
            return None
        sorted_points = sorted(future_points, key=lambda p: p["price"])
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
        current_time = datetime.now(timezone.utc)
        future_points = []
        for date, points in data.items():
            for point in points:
                start = datetime.fromisoformat(point["start"])
                if start > current_time:
                    future_points.append(point)
        sorted_points = sorted(future_points, key=lambda p: p["price"])
        count = self._entry.data.get("lowest_periods_count", 14)
        selected = sorted_points[:count]
        return {"data": selected}

class Frank2HighestPeriodsTodaySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Highest Periods Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_highest_periods_today"

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

class Frank2LowestPeriodsTomorrowSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Lowest Periods Tomorrow"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_lowest_periods_tomorrow"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return None
        points = data[tomorrow_str]
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
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return {}
        points = data[tomorrow_str]
        sorted_points = sorted(points, key=lambda p: p["price"])
        count = self._entry.data.get("lowest_periods_count", 14)
        selected = sorted_points[:count]
        return {"data": selected}

class Frank2LowestPeriodsTodaySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Lowest Periods Today"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_lowest_periods_today"

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

class Frank2HighestPeriodsTomorrowSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Highest Periods Tomorrow"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_highest_periods_tomorrow"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return None
        points = data[tomorrow_str]
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
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return {}
        points = data[tomorrow_str]
        sorted_points = sorted(points, key=lambda p: p["price"], reverse=True)
        count = self._entry.data.get("highest_periods_count", 8)
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

class Frank2PriceDiffFutureSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Price Diff Future"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_price_diff_future"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        # Highest periods today
        today_str = datetime.utcnow().date().strftime("%Y%m%d")
        if today_str not in data:
            return None
        points_today = data[today_str]
        sorted_today = sorted(points_today, key=lambda p: p["price"], reverse=True)
        count_high = self._entry.data.get("highest_periods_count", 8)
        selected_high = sorted_today[:count_high]
        if not selected_high:
            return None
        avg_high = sum(p["price"] for p in selected_high) / len(selected_high)

        # Lowest periods tomorrow
        tomorrow_str = (datetime.utcnow().date() + timedelta(days=1)).strftime("%Y%m%d")
        if tomorrow_str not in data:
            return None
        points_tomorrow = data[tomorrow_str]
        sorted_tomorrow = sorted(points_tomorrow, key=lambda p: p["price"])
        count_low = self._entry.data.get("lowest_periods_count", 14)
        selected_low = sorted_tomorrow[:count_low]
        if not selected_low:
            return None
        avg_low = sum(p["price"] for p in selected_low) / len(selected_low)

        diff = avg_high - avg_low
        return round(diff, 5)

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        return {}