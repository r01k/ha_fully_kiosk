"""Services for the Fully Kiosk Browser integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.device_registry as dr
from typing import Callable
from fullykiosk import FullyKiosk

from .const import (
    LOGGER,
    ATTR_APPLICATION,
    ATTR_URL,
    ATTR_BRIGHTNESS,
    DOMAIN,
    SERVICE_LOAD_URL,
    SERVICE_START_APPLICATION,
    SERVICE_SET_SCREEN_BRIGHTNESS
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up the services for the Fully Kiosk Browser integration."""

    async def execute_service(
        call: ServiceCall, fully_method: Callable, *args, **kwargs
    ) -> None:
        """
        Execute a Fully service call

        :param call: {ServiceCall} HA service call.
        :param fully_method: {Callable} A method of the FullyKiosk class.
        :param args: Arguments for fully_method.
        :param kwargs: Key work arguments for fully_method.
        :return: None
        """
        LOGGER.debug(f"Calling Fully service {ServiceCall} wtih args: {args}, {kwargs}")
        registry = dr.async_get(hass)
        for target in call.data[ATTR_DEVICE_ID]:
            device = registry.async_get(target)
            if device:
                coordinator = hass.data[DOMAIN][list(device.config_entries)[0]]
                await fully_method(coordinator.fully, *args, **kwargs)

    async def async_load_url(call: ServiceCall) -> None:
        """Load a URL on the Fully Kiosk Browser."""
        await execute_service(
            call, FullyKiosk.loadUrl, call.data[ATTR_URL]
        )

    async def async_start_app(call: ServiceCall) -> None:
        """Start an app on the device."""
        await execute_service(
            call, FullyKiosk.startApplication, call.data[ATTR_APPLICATION]
        )

    async def async_set_brightness(call: ServiceCall) -> None:
        """Set the screen brightness level on the device."""
        await execute_service(
            call, FullyKiosk.setScreenBrightness, call.data[ATTR_BRIGHTNESS]
        )

    # Register all the above services
    service_mapping = [
        (async_load_url, SERVICE_LOAD_URL, ATTR_URL),
        (async_start_app, SERVICE_START_APPLICATION, ATTR_APPLICATION),
        (async_set_brightness, SERVICE_SET_SCREEN_BRIGHTNESS, ATTR_BRIGHTNESS)
    ]
    for service_handler, SERVICE_NAME, ATTRIB in service_mapping:
        hass.services.async_register(
            DOMAIN,
            SERVICE_NAME,
            service_handler,
            schema=vol.Schema(
                vol.All(
                    {vol.Required(ATTR_DEVICE_ID): cv.ensure_list,
                     vol.Required(ATTRIB): cv.string}
                )
            )
        )
