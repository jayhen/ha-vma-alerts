# VMA Alerts Dashboards

This directory contains YAML files for Home Assistant dashboards that display VMA alerts.

## Available Dashboards

1. **vma_dashboard_card.yaml** - The main dashboard for displaying VMA alerts, including active alerts, test alerts, and canceled alerts.
2. **vma_test_dashboard.yaml** - A diagnostic dashboard for troubleshooting the VMA alerts integration.

## How to Use

To use these dashboards in Home Assistant:

1. Go to the Home Assistant UI
2. Click on "Overview" in the sidebar
3. Click the three dots in the top right corner
4. Select "Edit Dashboard"
5. Click "Add Card" at the bottom
6. Choose "Manual" card
7. Paste the contents of the desired YAML file
8. Click "Save"

## Dashboard Features

### Main Dashboard (vma_dashboard_card.yaml)

- Displays active VMA alerts with details such as severity, status, type, event, areas, description, etc.
- Shows debug information to help troubleshoot issues
- Lists all SRCAP entities with their attributes
- Provides a comprehensive view of all VMA alert sensors

### Test Dashboard (vma_test_dashboard.yaml)

- Displays binary sensor attributes
- Shows available alert entities
- Provides detailed information about each alert
- Helps diagnose issues with the VMA alerts integration

## Customization

Feel free to customize these dashboards to suit your needs. You can modify the YAML files to change the layout, add or remove sections, or adjust the styling. 