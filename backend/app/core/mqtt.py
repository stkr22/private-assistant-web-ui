"""MQTT client for publishing device updates."""

import json
import logging
from contextlib import asynccontextmanager
from typing import Any

import aiomqtt
from private_assistant_commons import skill_config

from app.core.config import get_settings

logger = logging.getLogger(__name__)


# AIDEV-NOTE: This client is publish-only. The web-ui does not subscribe
# to MQTT topics; it only publishes device registry updates.
# aiomqtt uses async context managers instead of singleton pattern.


@asynccontextmanager
async def get_mqtt_client():
    """Get MQTT client context manager.

    Yields:
        Connected aiomqtt client instance.

    Raises:
        Exception: If connection to MQTT broker fails.
    """
    settings = get_settings()
    async with aiomqtt.Client(
        hostname=settings.mqtt.HOST,
        port=settings.mqtt.PORT,
        username=settings.mqtt.USERNAME if settings.mqtt.USERNAME else None,
        password=settings.mqtt.PASSWORD if settings.mqtt.PASSWORD else None,
    ) as client:
        logger.info(f"MQTT client connected to {settings.mqtt.HOST}:{settings.mqtt.PORT}")
        yield client


async def publish_device_update(device_id: str, action: str) -> None:
    """Publish device update to MQTT.

    Args:
        device_id: UUID of the device.
        action: Action type: 'created', 'updated', or 'deleted'.

    Raises:
        Exception: If MQTT publish fails.
    """
    topic = skill_config.SkillConfig().device_update_topic
    payload: dict[str, Any] = {
        "device_id": device_id,
        "action": action,
        "source": "web-ui",
    }

    try:
        async with get_mqtt_client() as client:
            await client.publish(topic, json.dumps(payload), qos=1)
            logger.info(f"Published device {action}: {device_id}")
    except Exception as e:
        logger.error(f"Error publishing to MQTT: {e}")
        raise
