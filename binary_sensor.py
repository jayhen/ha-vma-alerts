"""Binary sensor platform for Swedish VMA Alerts integration."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_SHOW_EXPIRED,
    DEFAULT_SHOW_EXPIRED,
    STATUS_ACTUAL,
    MESSAGE_TYPE_ALERT,
    MESSAGE_TYPE_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the VMA binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Add the main binary sensor that indicates if there are any active alerts
    async_add_entities([VMAAlertBinarySensor(coordinator, entry)], True)


class VMAAlertBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for indicating active VMA alerts."""

    _attr_device_class = BinarySensorDeviceClass.SAFETY

    def __init__(self, coordinator, entry):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = f"{DEFAULT_NAME} Active"
        self._attr_unique_id = f"{entry.entry_id}_active"
        self._attr_icon = "mdi:alert-circle"

    @property
    def is_on(self) -> bool:
        """Return True if there are active alerts."""
        if not self.coordinator.data or "alerts" not in self.coordinator.data:
            return False
            
        show_expired = self._entry.data.get(CONF_SHOW_EXPIRED, DEFAULT_SHOW_EXPIRED)
        
        # Check for active alerts
        for alert in self.coordinator.data["alerts"]:
            # Skip if alert is None or not a dictionary
            if not alert or not isinstance(alert, dict):
                continue
                
            # Skip if not an actual alert or update
            if alert.get("status") != STATUS_ACTUAL:
                continue
                
            if alert.get("msgType") not in [MESSAGE_TYPE_ALERT, MESSAGE_TYPE_UPDATE]:
                continue
                
            # Skip expired alerts if show_expired is False
            if not show_expired:
                info_list = alert.get("info", [])
                if not info_list or not isinstance(info_list, list) or len(info_list) == 0:
                    continue
                    
                info = None
                for i in info_list:
                    if i and isinstance(i, dict):
                        info = i
                        break
                        
                if not info:
                    continue
                    
                expires = info.get("expires")
                if expires and datetime.fromisoformat(expires.replace("Z", "+00:00")) < datetime.now():
                    continue
                    
            # If we get here, there's at least one active alert
            return True
                
        return False

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or "alerts" not in self.coordinator.data:
            return {"active_alerts": 0, "alert_ids": []}
            
        show_expired = self._entry.data.get(CONF_SHOW_EXPIRED, DEFAULT_SHOW_EXPIRED)
        
        # Count active alerts
        active_alerts = []
        for alert in self.coordinator.data["alerts"]:
            # Skip if alert is None or missing required fields
            if not alert or not isinstance(alert, dict) or "identifier" not in alert:
                continue
                
            # Skip if not an actual alert or update
            if alert.get("status") != STATUS_ACTUAL:
                continue
                
            if alert.get("msgType") not in [MESSAGE_TYPE_ALERT, MESSAGE_TYPE_UPDATE]:
                continue
                
            # Skip expired alerts if show_expired is False
            if not show_expired:
                info_list = alert.get("info", [])
                if not info_list or not isinstance(info_list, list) or len(info_list) == 0:
                    continue
                    
                info = None
                for i in info_list:
                    if i and isinstance(i, dict):
                        info = i
                        break
                        
                if not info:
                    continue
                    
                expires = info.get("expires")
                if expires and datetime.fromisoformat(expires.replace("Z", "+00:00")) < datetime.now():
                    continue
                    
            active_alerts.append(alert["identifier"])
                
        return {
            "active_alerts": len(active_alerts),
            "alert_ids": active_alerts,
        } 