"""Define the Nanoleaf data coordinator."""

from datetime import timedelta
import logging
from typing import override

from aionanoleaf2 import InvalidToken, Nanoleaf, Unavailable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import RESERVED_EFFECTS

_LOGGER = logging.getLogger(__name__)

type NanoleafConfigEntry = ConfigEntry[NanoleafCoordinator]


class NanoleafCoordinator(DataUpdateCoordinator[None]):
    """Class to manage fetching Nanoleaf data."""

    config_entry: NanoleafConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: NanoleafConfigEntry, nanoleaf: Nanoleaf
    ) -> None:
        """Initialize the Nanoleaf data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="Nanoleaf",
            update_interval=timedelta(minutes=1),
        )
        self.nanoleaf = nanoleaf

    async def async_update_effect_details(self) -> None:
        """Update details for the currently selected effect."""
        if (
            self.nanoleaf.is_on
            and (effect := self.nanoleaf.selected_effect) is not None
            and effect not in RESERVED_EFFECTS
        ):
            await self.nanoleaf.get_effect_details(effect)

    @override
    async def _async_update_data(self) -> None:
        try:
            await self.nanoleaf.get_info()
            await self.async_update_effect_details()
        except Unavailable as err:
            raise UpdateFailed from err
        except InvalidToken as err:
            raise ConfigEntryAuthFailed from err
