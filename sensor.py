"""Sensor platform for Swedish VMA Alerts integration."""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_LANGUAGE,
    CONF_SHOW_EXPIRED,
    DEFAULT_LANGUAGE,
    DEFAULT_SHOW_EXPIRED,
    ATTR_HEADLINE,
    ATTR_DESCRIPTION,
    ATTR_INSTRUCTION,
    ATTR_AREA,
    ATTR_SENT,
    ATTR_EFFECTIVE,
    ATTR_EXPIRES,
    ATTR_STATUS,
    ATTR_MESSAGE_TYPE,
    ATTR_SEVERITY,
    ATTR_URGENCY,
    ATTR_CERTAINTY,
    ATTR_EVENT,
    ATTR_SENDER_NAME,
    ATTR_WEB,
    ATTR_CONTACT,
    ATTR_PARAMETERS,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the VMA sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    language = entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
    show_expired = entry.data.get(CONF_SHOW_EXPIRED, DEFAULT_SHOW_EXPIRED)
    
    # Create a list to hold our entities
    entities = []
    
    # Add the main sensor that shows the number of active alerts
    entities.append(VMAAlertCountSensor(coordinator, entry, language))
    
    # Add individual alert sensors
    if coordinator.data and "alerts" in coordinator.data:
        for alert in coordinator.data["alerts"]:
            # Skip expired alerts if show_expired is False
            if not show_expired:
                expires = alert.get("info", [{}])[0].get("expires")
                if expires and datetime.fromisoformat(expires.replace("Z", "+00:00")) < datetime.now():
                    continue
                    
            entities.append(VMAAlertSensor(coordinator, entry, alert["identifier"], language))
    
    async_add_entities(entities, True)


class VMAAlertCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for counting active VMA alerts."""

    def __init__(self, coordinator, entry, language):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._language = language
        self._attr_name = f"{DEFAULT_NAME} Count"
        self._attr_unique_id = f"{entry.entry_id}_count"
        self._attr_icon = "mdi:alert"

    @property
    def native_value(self) -> int:
        """Return the number of active alerts."""
        if not self.coordinator.data or "alerts" not in self.coordinator.data:
            return 0
            
        show_expired = self._entry.data.get(CONF_SHOW_EXPIRED, DEFAULT_SHOW_EXPIRED)
        
        if show_expired:
            return len(self.coordinator.data["alerts"])
        
        # Count only non-expired alerts
        count = 0
        for alert in self.coordinator.data["alerts"]:
            expires = alert.get("info", [{}])[0].get("expires")
            if not expires or datetime.fromisoformat(expires.replace("Z", "+00:00")) >= datetime.now():
                count += 1
                
        return count

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return {
            "alerts": [alert["identifier"] for alert in self.coordinator.data.get("alerts", [])] if self.coordinator.data else []
        }


class VMAAlertSensor(CoordinatorEntity, SensorEntity):
    """Sensor for individual VMA alerts."""

    def __init__(self, coordinator, entry, alert_id, language):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._alert_id = alert_id
        self._language = language
        self._attr_unique_id = f"{entry.entry_id}_{alert_id}"
        self._attr_entity_id = f"sensor.{alert_id.lower()}"
        self._attr_icon = "mdi:alert-octagon"
        
        # Set initial state
        self._update_attributes()

    def _update_attributes(self) -> None:
        """Update the sensor attributes based on the alert data."""
        if not self.coordinator.data or "alerts" not in self.coordinator.data:
            self._attr_native_value = "Unknown"
            self._attr_extra_state_attributes = {}
            return
            
        # Find the alert with matching ID
        alert = None
        for a in self.coordinator.data["alerts"]:
            if not a or not isinstance(a, dict):
                continue
                
            if "identifier" in a and a["identifier"] == self._alert_id:
                alert = a
                break
                
        if not alert:
            self._attr_native_value = "Unknown"
            self._attr_extra_state_attributes = {}
            return
            
        # Get the info in the preferred language, or the first info if not available
        info = None
        info_list = alert.get("info", [])
        
        # Handle the case where info is None (Cancel messages)
        if info_list is None:
            self._attr_name = f"Alert {self._alert_id}"
            self._attr_native_value = "Canceled"
            
            # Set basic attributes for cancel messages
            self._attr_extra_state_attributes = {
                ATTR_STATUS: alert.get("status"),
                ATTR_MESSAGE_TYPE: alert.get("msgType"),
                ATTR_SENT: alert.get("sent"),
                ATTR_EVENT: "Alert Canceled",
            }
            return
            
        if not isinstance(info_list, list) or len(info_list) == 0:
            self._attr_native_value = "Unknown"
            self._attr_extra_state_attributes = {}
            return
            
        for i in info_list:
            if not i or not isinstance(i, dict):
                continue
                
            if "language" in i and i["language"] == self._language:
                info = i
                break
                
        if not info and info_list:
            # Get the first valid info object
            for i in info_list:
                if i and isinstance(i, dict):
                    info = i
                    break
            
        if not info:
            self._attr_native_value = "Unknown"
            self._attr_extra_state_attributes = {}
            return
            
        # Set the sensor name and state
        headline = info.get("headline")
        if headline:
            self._attr_name = headline
        else:
            event = info.get("event")
            if event:
                self._attr_name = f"{event} - {self._alert_id}"
            else:
                self._attr_name = f"Alert {self._alert_id}"
                
        severity = info.get("severity")
        if severity:
            self._attr_native_value = severity
        else:
            self._attr_native_value = "Unknown"
        
        # Set attributes
        attributes = {
            ATTR_HEADLINE: info.get("headline"),
            ATTR_DESCRIPTION: info.get("description"),
            ATTR_INSTRUCTION: info.get("instruction"),
            ATTR_AREA: [area.get("areaDesc") for area in info.get("area", []) if area and isinstance(area, dict)],
            ATTR_SENT: alert.get("sent"),
            ATTR_EFFECTIVE: info.get("effective"),
            ATTR_EXPIRES: info.get("expires"),
            ATTR_STATUS: alert.get("status"),
            ATTR_MESSAGE_TYPE: alert.get("msgType"),
            ATTR_SEVERITY: info.get("severity"),
            ATTR_URGENCY: info.get("urgency"),
            ATTR_CERTAINTY: info.get("certainty"),
            ATTR_EVENT: info.get("event"),
            ATTR_SENDER_NAME: alert.get("sender", {}).get("name") if alert.get("sender") and isinstance(alert.get("sender"), dict) else None,
            ATTR_WEB: info.get("web"),
            ATTR_CONTACT: info.get("contact"),
        }
        
        # Add parameters if available
        if info and "parameter" in info and isinstance(info["parameter"], list):
            parameters = {}
            for param in info["parameter"]:
                if param and isinstance(param, dict) and "valueName" in param and "value" in param:
                    parameters[param["valueName"]] = param["value"]
            attributes[ATTR_PARAMETERS] = parameters
            
        self._attr_extra_state_attributes = attributes

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attributes()
        super()._handle_coordinator_update() 