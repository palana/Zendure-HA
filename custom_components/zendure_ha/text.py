"""Interfaces with the Zendure Integration text entities."""

import asyncio
import logging
from collections.abc import Callable

from homeassistant.components.text import TextEntity, TextEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import EntityDevice, EntityZendure

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(_hass: HomeAssistant, _config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the Zendure text."""
    ZendureText.add = async_add_entities


class ZendureText(EntityZendure, TextEntity):
    """Representation of a Zendure text entity."""

    add: AddEntitiesCallback

    def __init__(self, device: EntityDevice, uniqueid: str, onchanged: Callable | None, value: str = "") -> None:
        """Initialize a text entity."""
        super().__init__(device, uniqueid, "text")
        self.entity_description = TextEntityDescription(key=uniqueid, name=uniqueid)
        self._attr_native_value = value
        self.onchanged = onchanged
        self.add([self])

    async def async_set_value(self, value: str) -> None:
        """Set the value."""
        self._attr_native_value = value
        if self.onchanged:
            if asyncio.iscoroutinefunction(self.onchanged):
                await self.onchanged(self, value)
            else:
                self.onchanged(self, value)
        if self.hass and self.hass.loop.is_running():
            self.async_write_ha_state()


class ZendureRestoreText(ZendureText, RestoreEntity):
    """Representation of a Zendure text entity with restore."""

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (state := await self.async_get_last_state()) and state.state not in (None, "", "unknown", "unavailable"):
            self._attr_native_value = state.state

        if self.onchanged:
            if asyncio.iscoroutinefunction(self.onchanged):
                await self.onchanged(self, self._attr_native_value)
            else:
                self.onchanged(self, self._attr_native_value)
