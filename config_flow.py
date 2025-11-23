import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

class Frank2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Frank2", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("token"): str,
                vol.Required("inkoop", default=0.01815): vol.Coerce(float),
                vol.Required("eb", default=0.12286): vol.Coerce(float),
                vol.Required("btw", default=21.0): vol.Coerce(float),
                vol.Required("lowest_periods_count", default=14): vol.All(vol.Coerce(int), vol.Range(min=4, max=24)),
                vol.Required("highest_periods_count", default=8): vol.All(vol.Coerce(int), vol.Range(min=4, max=24)),
            })
        )