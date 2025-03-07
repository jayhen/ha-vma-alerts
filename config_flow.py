"""Config flow for Swedish VMA Alerts integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_GEOCODE,
    CONF_GEOCODES,
    CONF_LANGUAGE,
    CONF_SHOW_EXPIRED,
    CONF_SCAN_INTERVAL,
    CONF_USE_TEST_API,
    DEFAULT_LANGUAGE,
    DEFAULT_SHOW_EXPIRED,
    DEFAULT_USE_TEST_API,
    SCAN_INTERVAL,
    API_ENDPOINT,
    COUNTIES,
)

_LOGGER = logging.getLogger(__name__)

class VMAFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Swedish VMA Alerts."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Convert single geocode to list if provided
            if CONF_GEOCODE in user_input and user_input[CONF_GEOCODE]:
                user_input[CONF_GEOCODES] = [user_input[CONF_GEOCODE]]
                del user_input[CONF_GEOCODE]
                
            # Validate the geocodes if provided
            if CONF_GEOCODES in user_input and user_input[CONF_GEOCODES]:
                valid = True
                for geocode in user_input[CONF_GEOCODES]:
                    if not await self._validate_geocode(geocode):
                        valid = False
                        break
                        
                if not valid:
                    errors[CONF_GEOCODES] = "invalid_geocode"

            if not errors:
                return self.async_create_entry(
                    title="Swedish VMA Alerts",
                    data=user_input,
                )

        # Show the form to the user
        schema = vol.Schema(
            {
                vol.Optional(CONF_GEOCODES, default=[]): cv.multi_select(COUNTIES),
                vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(
                    ["sv-SE", "en-US"]
                ),
                vol.Optional(CONF_SHOW_EXPIRED, default=DEFAULT_SHOW_EXPIRED): cv.boolean,
                vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=3600)
                ),
                vol.Optional(CONF_USE_TEST_API, default=DEFAULT_USE_TEST_API): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    async def _validate_geocode(geocode: str) -> bool:
        """Validate the geocode format."""
        # Simple validation - should be a string of numbers
        # For a more comprehensive validation, we would check against a list of valid geocodes
        if not geocode.isdigit():
            return False
        return True

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VMAOptionsFlowHandler(config_entry)


class VMAOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the component."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Convert single geocode to list if provided
            if CONF_GEOCODE in user_input and user_input[CONF_GEOCODE]:
                user_input[CONF_GEOCODES] = [user_input[CONF_GEOCODE]]
                del user_input[CONF_GEOCODE]
                
            # Validate the geocodes if provided
            if CONF_GEOCODES in user_input and user_input[CONF_GEOCODES]:
                valid = True
                for geocode in user_input[CONF_GEOCODES]:
                    if not await self._validate_geocode(geocode):
                        valid = False
                        break
                        
                if not valid:
                    errors[CONF_GEOCODES] = "invalid_geocode"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        # Get current geocodes
        current_geocodes = self.config_entry.options.get(
            CONF_GEOCODES, self.config_entry.data.get(CONF_GEOCODES, [])
        )
        
        # If we have the old single geocode format, convert it
        if not current_geocodes and self.config_entry.data.get(CONF_GEOCODE):
            current_geocodes = [self.config_entry.data.get(CONF_GEOCODE)]

        options = {
            vol.Optional(
                CONF_GEOCODES,
                default=current_geocodes,
            ): cv.multi_select(COUNTIES),
            vol.Optional(
                CONF_LANGUAGE,
                default=self.config_entry.options.get(
                    CONF_LANGUAGE, self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
                ),
            ): vol.In(["sv-SE", "en-US"]),
            vol.Optional(
                CONF_SHOW_EXPIRED,
                default=self.config_entry.options.get(
                    CONF_SHOW_EXPIRED, self.config_entry.data.get(CONF_SHOW_EXPIRED, DEFAULT_SHOW_EXPIRED)
                ),
            ): cv.boolean,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, self.config_entry.data.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
            vol.Optional(
                CONF_USE_TEST_API,
                default=self.config_entry.options.get(
                    CONF_USE_TEST_API, self.config_entry.data.get(CONF_USE_TEST_API, DEFAULT_USE_TEST_API)
                ),
            ): cv.boolean,
        }

        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options), errors=errors
        )

    @staticmethod
    async def _validate_geocode(geocode: str) -> bool:
        """Validate the geocode format."""
        # Simple validation - should be a string of numbers
        if not geocode.isdigit():
            return False
        return True 