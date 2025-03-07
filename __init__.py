"""The Swedish VMA Alerts integration."""
import asyncio
import logging
import json
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp

from .const import DOMAIN, SCAN_INTERVAL, PLATFORMS, API_ENDPOINT, TEST_API_ENDPOINT, CONF_SCAN_INTERVAL, CONF_GEOCODES, CONF_GEOCODE, CONF_USE_TEST_API
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Swedish VMA Alerts from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Force a reload of the entry data to ensure we have the latest configuration
    entry_data = dict(entry.data)
    
    # Convert old format to new format if needed
    if CONF_GEOCODE in entry_data and entry_data[CONF_GEOCODE] and CONF_GEOCODES not in entry_data:
        entry_data[CONF_GEOCODES] = [entry_data[CONF_GEOCODE]]
        hass.config_entries.async_update_entry(entry, data=entry_data)
    
    coordinator = VMADataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Set up services
    await async_setup_services(hass)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
        # If this is the last entry, unload services
        if not hass.data[DOMAIN]:
            await async_unload_services(hass)

    return unload_ok

class VMADataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching VMA data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the data updater."""
        self.hass = hass
        self.entry = entry
        self.api_endpoint = TEST_API_ENDPOINT if entry.data.get(CONF_USE_TEST_API, False) else API_ENDPOINT
        self.geocodes = entry.data.get(CONF_GEOCODES, [])
        self.previous_alerts = {}
        
        # Get the update interval from the config entry
        update_interval = entry.data.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self):
        """Fetch data from the VMA API."""
        try:
            # If we have geocodes, fetch data for each geocode
            if self.geocodes:
                all_alerts = {}
                for geocode in self.geocodes:
                    alerts = await self._fetch_data_for_geocode(geocode)
                    all_alerts.update(alerts)
                
                # Also fetch alerts without a geocode filter to catch national alerts
                national_alerts = await self._fetch_data_for_geocode()
                all_alerts.update(national_alerts)
                
                # Check for new alerts and fire events
                self._check_for_new_alerts(all_alerts)
                
                return all_alerts
            else:
                # No geocodes specified, fetch all alerts
                alerts = await self._fetch_data_for_geocode()
                
                # Check for new alerts and fire events
                self._check_for_new_alerts(alerts)
                
                return alerts
                
        except Exception as err:
            _LOGGER.error("Error fetching VMA data: %s", err)
            raise UpdateFailed(f"Error fetching VMA data: {err}")
    
    def _check_for_new_alerts(self, current_alerts):
        """Check for new alerts and fire events for them."""
        # Find new alerts that weren't in the previous update
        new_alerts = {
            alert_id: alert_data 
            for alert_id, alert_data in current_alerts.items() 
            if alert_id not in self.previous_alerts
        }
        
        # Fire an event for each new alert
        for alert_id, alert_data in new_alerts.items():
            self.hass.bus.async_fire(
                f"{DOMAIN}_new_alert", 
                {
                    "alert_id": alert_id,
                    "headline": alert_data.get("headline", ""),
                    "severity": alert_data.get("severity", ""),
                    "area": alert_data.get("area", []),
                    "description": alert_data.get("description", ""),
                    "instruction": alert_data.get("instruction", ""),
                    "sent": alert_data.get("sent", ""),
                    "expires": alert_data.get("expires", ""),
                }
            )
            _LOGGER.debug(f"Fired event for new alert: {alert_id}")
        
        # Update previous alerts for next comparison
        self.previous_alerts = current_alerts.copy()

    async def _fetch_data_for_geocode(self, geocode=None):
        """Fetch data from the VMA API for a specific geocode."""
        try:
            async with aiohttp.ClientSession() as session:
                # Use the test API if configured
                use_test_api = self.entry.data.get(CONF_USE_TEST_API, False)
                
                if use_test_api:
                    url = TEST_API_ENDPOINT
                    _LOGGER.debug("Using test API: %s", url)
                else:
                    url = API_ENDPOINT
                    if geocode:
                        # According to the API documentation, geocode should be part of the path
                        url = f"{API_ENDPOINT}/{geocode}"
                
                _LOGGER.debug("Fetching data from %s", url)
                
                async with session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.error("Error communicating with API: %s", response.status)
                        raise UpdateFailed(f"Error communicating with API: {response.status}")
                    
                    try:
                        data = await response.json()
                        
                        # Validate the data structure
                        if not isinstance(data, dict):
                            _LOGGER.error("Invalid data format: not a dictionary")
                            return {"timestamp": None, "alerts": []}
                            
                        if "alerts" not in data:
                            _LOGGER.error("Invalid data format: 'alerts' key missing")
                            data["alerts"] = []
                            
                        if not isinstance(data["alerts"], list):
                            _LOGGER.error("Invalid data format: 'alerts' is not a list")
                            data["alerts"] = []
                            
                        # Validate each alert
                        valid_alerts = []
                        for alert in data["alerts"]:
                            if not alert or not isinstance(alert, dict):
                                _LOGGER.warning("Skipping invalid alert: %s", alert)
                                continue
                                
                            if "identifier" not in alert:
                                _LOGGER.warning("Skipping alert without identifier: %s", alert)
                                continue
                                
                            valid_alerts.append(alert)
                            
                        data["alerts"] = valid_alerts
                            
                        # Log the number of alerts
                        _LOGGER.debug("Received %d alerts from the API for geocode %s", 
                                     len(data["alerts"]), geocode if geocode else "all")
                        
                        return data
                    except json.JSONDecodeError as err:
                        _LOGGER.error("Error decoding JSON: %s", err)
                        raise UpdateFailed(f"Error decoding JSON: {err}") from err
                    
        except aiohttp.ClientError as err:
            _LOGGER.error("Error communicating with API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout communicating with API: %s", err)
            raise UpdateFailed(f"Timeout communicating with API: {err}") from err 