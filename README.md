# ha-vma-alerts
# Swedish VMA Alerts for Home Assistant

This custom component integrates with the Swedish Radio's VMA API (Viktigt Meddelande till Allmänheten - Important Public Announcements) to provide real-time alerts and warnings in Home Assistant.

## What is VMA?

VMA (Viktigt Meddelande till Allmänheten) is a system for warning the public in Sweden about serious incidents that pose an immediate threat to life, health, property, or the environment. These alerts are distributed through radio, TV, SMS, and now through this Home Assistant integration.

## Features

- Real-time monitoring of VMA alerts
- Filter alerts by geographic area (county or municipality)
- Support for both Swedish and English languages
- Binary sensor to indicate if there are active alerts
- Sensor showing the number of active alerts
- Individual sensors for each alert with detailed information
- Configurable update interval
- Option to show or hide expired alerts
- Node-RED integration with events and webhooks
- Ready-to-use example flows for Node-RED

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS > Integrations
3. Click the "+" button
4. Search for "Swedish VMA Alerts"
5. Click Install
6. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `vma_alerts` folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Swedish VMA Alerts"
4. Follow the configuration steps

### Configuration Options

- **Geographic Code**: Optional. Enter a county or municipality code to filter alerts by geographic area. Leave empty to receive all alerts.
- **Preferred Language**: Choose between Swedish (sv-SE) and English (en-US).
- **Show Expired Alerts**: Toggle to show or hide expired alerts.
- **Update Interval**: How often to check for new alerts (in seconds).

## Entities Created

### Binary Sensor

- `binary_sensor.vma_alerts_active`: Indicates if there are any active alerts (ON = active alerts, OFF = no active alerts)

### Sensors

- `sensor.vma_alerts_count`: Shows the number of active alerts
- Individual sensors for each alert with the alert headline as the name and severity as the state

## Dashboard Cards

You can create custom cards to display VMA alerts on your dashboard. Here's an example using a conditional card:

```yaml
type: conditional
conditions:
  - entity: binary_sensor.vma_alerts_active
    state: "on"
card:
  type: markdown
  content: >
    ## ⚠️ Active VMA Alerts ⚠️

    {% for alert_id in state_attr('binary_sensor.vma_alerts_active', 'alert_ids') %}
      {% set alert_entity = 'sensor.' ~ alert_id %}
      {% if states(alert_entity) %}
        ### {{ state_attr(alert_entity, 'headline') }}
        **Severity:** {{ states(alert_entity) }}
        **Areas:** {{ state_attr(alert_entity, 'area')|join(', ') }}
        **Description:** {{ state_attr(alert_entity, 'description') }}
        {% if state_attr(alert_entity, 'instruction') %}
        **Instructions:** {{ state_attr(alert_entity, 'instruction') }}
        {% endif %}
        **Expires:** {{ state_attr(alert_entity, 'expires') }}
        ---
      {% endif %}
    {% endfor %}
```

### Ready-to-Use Dashboards

This integration includes ready-to-use dashboard configurations in the `dashboards` directory:

1. **Main Dashboard** (`dashboards/vma_dashboard_card.yaml`): A comprehensive dashboard that displays active alerts, test alerts, and canceled alerts with all their details.

2. **Test Dashboard** (`dashboards/vma_test_dashboard.yaml`): A diagnostic dashboard that helps troubleshoot issues with the integration by showing detailed information about the entities and their attributes.

To use these dashboards:
1. Go to your Home Assistant dashboard
2. Click "Edit Dashboard"
3. Click "Add Card" at the bottom
4. Choose "Manual"
5. Copy and paste the contents of the desired YAML file
6. Click "Save"

## Node-RED Integration

This integration provides several features to make it easy to use VMA alerts in Node-RED:

### Events

The integration fires events that you can listen for in Node-RED:

- `vma_alerts_new_alert`: Fired when a new alert is received. The event data includes:
  - `alert_id`: The unique identifier of the alert
  - `headline`: The headline of the alert
  - `severity`: The severity level of the alert
  - `area`: The affected areas
  - `description`: Detailed description of the alert
  - `instruction`: Instructions for the public (if available)
  - `sent`: When the alert was sent
  - `expires`: When the alert expires

### Services

The integration provides services that can be called from Node-RED:

- `vma_alerts.refresh`: Manually refresh the alert data
- `vma_alerts.get_alert_details`: Get detailed information about a specific alert
  - Parameters: `alert_id` (required)
  - Fires an event `vma_alerts_alert_details` with the alert details
- `vma_alerts.webhook_alert`: Send alert data to a webhook endpoint
  - Parameters: 
    - `webhook_url` (required): The URL to send the data to
    - `alert_id` (optional): Send a specific alert
    - `include_all` (optional): Send all active alerts

### Example Node-RED Flow

The integration includes an example Node-RED flow in `dashboards/node_red_example_flow.json` that demonstrates:

1. Listening for new alert events
2. Displaying alerts in the Node-RED dashboard
3. Sending notifications for new alerts
4. Setting up a webhook endpoint to receive alert data
5. Acknowledging alerts to prevent duplicate notifications

To import the example flow:

1. Open Node-RED
2. Click the menu in the top-right corner
3. Select "Import"
4. Copy and paste the contents of `node_red_example_flow.json`
5. Click "Import"

### Creating Your Own Node-RED Flows

You can create your own Node-RED flows to handle VMA alerts in various ways:

1. **Listen for events**: Use the "Events: all" node to listen for `vma_alerts_new_alert` events
2. **Call services**: Use the "Call Service" node to call the integration's services
3. **Create a webhook endpoint**: Use the "HTTP In" node to create an endpoint for receiving webhook data
4. **Process alert data**: Use function nodes to process and format alert data
5. **Send notifications**: Use various notification nodes to send alerts to different platforms
6. **Create custom dashboards**: Use the Node-RED dashboard nodes to create custom alert displays

## Automation Examples

### Send a notification when a new alert is received

```yaml
automation:
  - alias: "VMA Alert Notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.vma_alerts_active
        from: "off"
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ VMA Alert"
          message: "There are {{ state_attr('binary_sensor.vma_alerts_active', 'active_alerts') }} active VMA alerts"
          data:
            push:
              sound: default
```

## Geocodes

The VMA API uses numeric codes to identify geographic areas in Sweden. These codes follow the Swedish county and municipality code system.

- County codes are 2 digits (e.g., 01 for Stockholm County)
- Municipality codes are 4 digits (e.g., 0180 for Stockholm Municipality)

You can find a complete list of codes at [SCB (Statistics Sweden)](https://www.scb.se/en/finding-statistics/regional-statistics/regional-divisions/counties-and-municipalities/).

## API Information

This integration uses the official VMA API provided by Sveriges Radio:
- API Endpoint: https://vmaapi.sr.se/api/v2/alerts
- API Documentation: https://vmaapi.sr.se/swagger/v2.0/swagger.json

## Limitations

- This integration only works for alerts in Sweden
- The API may have rate limits that could affect frequent updates
- Geographic filtering is limited to county and municipality codes

## Troubleshooting

If you encounter issues:

1. Check that your configuration is correct
2. Verify your internet connection
3. Increase the logging level for the component:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.vma_alerts: debug
   ```
4. Check the Home Assistant logs for error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This integration is not officially affiliated with Sveriges Radio or the Swedish Civil Contingencies Agency (MSB). It is provided as-is with no warranty. 
>>>>>>> 9bc0571 (Initial commit)
