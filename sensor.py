from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    async_add_entities([Frank2Sensor(coordinator, entry)])

class Frank2Sensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def name(self):
        return "Frank2 Average Electricity Price"

    @property
    def unique_id(self):
        return f"{self._entry.entry_id}_average"

    @property
    def state(self):
        data = self.coordinator.data
        if not data:
            return None
        all_prices = []
        for date, points in data.items():
            all_prices.extend([p["price"] for p in points])
        if not all_prices:
            return None
        return round(sum(all_prices) / len(all_prices), 5)

    @property
    def unit_of_measurement(self):
        return "EUR/kWh"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if not data:
            return {}
        attributes = {"data": {}}
        for date, points in data.items():
            attributes["data"][date] = points
        return attributes