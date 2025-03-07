"""Services for the Swedish VMA Alerts integration."""
import logging
import json
import aiohttp
from typing import Any, Dict

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for VMA Alerts integration."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    async def async_refresh_service(service_call: ServiceCall) -> None:
        """Service to refresh VMA alerts data."""
        target_entities = await component.async_extract_from_service(service_call)
        
        # Get all coordinators
        coordinators = set()
        for entity in target_entities:
            if hasattr(entity, "coordinator"):
                coordinators.add(entity.coordinator)
        
        # Refresh each coordinator
        for coordinator in coordinators:
            await coordinator.async_refresh()
            
        _LOGGER.debug("VMA alerts data refreshed")

    async def async_get_alert_details_service(service_call: ServiceCall) -> None:
        """Service to get detailed information about a specific alert."""
        alert_id = service_call.data.get("alert_id")
        
        if not alert_id:
            _LOGGER.error("No alert_id provided to get_alert_details service")
            return
            
        # Find the alert entity
        alert_entity_id = f"sensor.{alert_id}"
        alert_entity = hass.states.get(alert_entity_id)
        
        if not alert_entity:
            _LOGGER.error(f"Alert entity {alert_entity_id} not found")
            return
            
        # Return the alert details as an event
        alert_data = {
            "id": alert_id,
            "state": alert_entity.state,
            **alert_entity.attributes
        }
        
        hass.bus.async_fire(f"{DOMAIN}_alert_details", alert_data)
        _LOGGER.debug(f"Fired event with details for alert {alert_id}")

    async def async_webhook_alert_service(service_call: ServiceCall) -> None:
        """Service to send alert data to a webhook endpoint."""
        webhook_url = service_call.data.get("webhook_url")
        alert_id = service_call.data.get("alert_id")
        include_all = service_call.data.get("include_all", False)
        
        if not webhook_url:
            _LOGGER.error("No webhook_url provided to webhook_alert service")
            return
            
        # Prepare data to send
        data_to_send = {}
        
        if alert_id:
            # Send specific alert
            alert_entity_id = f"sensor.{alert_id}"
            alert_entity = hass.states.get(alert_entity_id)
            
            if not alert_entity:
                _LOGGER.error(f"Alert entity {alert_entity_id} not found")
                return
                
            data_to_send = {
                "id": alert_id,
                "state": alert_entity.state,
                **alert_entity.attributes
            }
        elif include_all:
            # Send all active alerts
            binary_sensor = hass.states.get("binary_sensor.vma_alerts_active")
            if not binary_sensor:
                _LOGGER.error("VMA Alerts binary sensor not found")
                return
                
            alert_ids = binary_sensor.attributes.get("alert_ids", [])
            alerts = []
            
            for aid in alert_ids:
                alert_entity_id = f"sensor.{aid}"
                alert_entity = hass.states.get(alert_entity_id)
                
                if alert_entity:
                    alerts.append({
                        "id": aid,
                        "state": alert_entity.state,
                        **alert_entity.attributes
                    })
            
            data_to_send = {
                "alerts": alerts,
                "count": len(alerts)
            }
        else:
            _LOGGER.error("Either alert_id or include_all must be provided")
            return
            
        # Send data to webhook
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url, 
                    json=data_to_send,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status < 200 or response.status >= 300:
                        _LOGGER.error(f"Error sending to webhook: {response.status}")
                    else:
                        _LOGGER.debug(f"Successfully sent alert data to webhook")
        except Exception as e:
            _LOGGER.error(f"Failed to send data to webhook: {e}")

    hass.services.async_register(
        DOMAIN, "refresh", async_refresh_service, schema=vol.Schema({
            vol.Optional("entity_id"): cv.entity_ids,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "get_alert_details", async_get_alert_details_service, schema=vol.Schema({
            vol.Required("alert_id"): cv.string,
        })
    )
    
    hass.services.async_register(
        DOMAIN, "webhook_alert", async_webhook_alert_service, schema=vol.Schema({
            vol.Required("webhook_url"): cv.url,
            vol.Optional("alert_id"): cv.string,
            vol.Optional("include_all"): cv.boolean,
        })
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload VMA Alerts services."""
    if hass.services.has_service(DOMAIN, "refresh"):
        hass.services.async_remove(DOMAIN, "refresh")
    
    if hass.services.has_service(DOMAIN, "get_alert_details"):
        hass.services.async_remove(DOMAIN, "get_alert_details")
        
    if hass.services.has_service(DOMAIN, "webhook_alert"):
        hass.services.async_remove(DOMAIN, "webhook_alert") 