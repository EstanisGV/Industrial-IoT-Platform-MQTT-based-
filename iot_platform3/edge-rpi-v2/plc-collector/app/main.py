from app.config import load_settings
from app.logger import setup_logger
from app.collectors.mock_client import MockCollector
from app.collectors.s7_client import S7Collector
from app.collectors.opcua_client import OpcUaCollector
from app.mqtt.publisher import MqttPublisher
from app.services.polling_service import PollingService
from app.services.heartbeat_service import HeartbeatService


def build_collector(settings):
    protocol = settings["env"]["PLC_PROTOCOL"].lower()
    if protocol == "mock":
        return MockCollector(settings)
    if protocol == "s7":
        return S7Collector(settings)
    if protocol == "opcua":
        return OpcUaCollector(settings)
    raise ValueError(f"Unsupported PLC_PROTOCOL: {protocol}")


def main():
    settings = load_settings()
    logger = setup_logger(settings)

    logger.info("Starting PLC collector service", extra={"event": "service_start"})

    collector = build_collector(settings)
    publisher = MqttPublisher(settings, logger)

    heartbeat_service = HeartbeatService(settings=settings, publisher=publisher, logger=logger)
    heartbeat_service.start()

    polling_service = PollingService(
        settings=settings,
        collector=collector,
        publisher=publisher,
        logger=logger,
    )
    polling_service.run()


if __name__ == "__main__":
    main()
