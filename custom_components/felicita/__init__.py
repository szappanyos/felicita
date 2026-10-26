"""Initialize the Felicita component."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import FelicitaCoordinator

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = ["button", "sensor", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Felicita as config entry."""
    
    # Remove existing instance if already exists (prevents multiple instances on reload)
    if config_entry.entry_id in hass.data.get(DOMAIN, {}):
        await async_unload_entry(hass, config_entry)

    coordinator = FelicitaCoordinator(hass, config_entry)
    hass.data.setdefault(DOMAIN, {})[config_entry.entry_id] = coordinator

    await coordinator.async_config_entry_first_refresh()

    # Load platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    # Reload this entry when its options/data change. HA manages the config
    # entry state transitions for us, so we must NOT call async_setup_entry
    # ourselves (that leaves the entry in LOADED state and breaks
    # async_config_entry_first_refresh on the next setup).
    config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_listener)
    )

    return True


async def _async_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle options update by reloading the config entry the proper way."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    
    # Properly unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unload_ok:
        # Ensure the coordinator is properly removed
        hass.data[DOMAIN].pop(config_entry.entry_id, None)
    
    return unload_ok
