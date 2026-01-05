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
                vol.Required("eb", default=0.1108): vol.Coerce(float),
                vol.Required("btw", default=21.0): vol.Coerce(float),
                vol.Required("lowest_periods_count", default=14): vol.All(vol.Coerce(int), vol.Range(min=4, max=24)),
                vol.Required("highest_periods_count", default=8): vol.All(vol.Coerce(int), vol.Range(min=4, max=24)),
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return Frank2OptionsFlow()


class Frank2OptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            new_data = self.config_entry.data.copy()
            new_data.update(user_input)
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("inkoop", default=self.config_entry.data.get("inkoop", 0.01815)): vol.Coerce(float),
                vol.Required("eb", default=self.config_entry.data.get("eb", 0.1108)): vol.Coerce(float),
                vol.Required("btw", default=self.config_entry.data.get("btw", 21.0)): vol.Coerce(float),
                vol.Required("lowest_periods_count", default=self.config_entry.data.get("lowest_periods_count", 14)): vol.All(vol.Coerce(int), vol.Range(min=4, max=24)),
                vol.Required("highest_periods_count", default=self.config_entry.data.get("highest_periods_count", 8)): vol.All(vol.Coerce(int), vol.Range(min=4, max=24)),
            })
        )