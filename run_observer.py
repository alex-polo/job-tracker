import logging

from src.core.conf import (
    ObserverSettings,
    RabbitMQPublisherConfig,
    RabbitMQSettings,
    setup_logging,
)
from src.services.observer.main import run_observer

logging.basicConfig(level=logging.DEBUG)


def main() -> None:
    """Initialize and run the observer service.

    Exceptions:
        KeyboardInterrupt: Shuts down the service when interrupted by user.
        Exception: Logs any unexpected exceptions with full stack trace.
    """
    try:
        log = logging.getLogger(__name__)

        observer_settings = ObserverSettings()  # type: ignore

        setup_logging(settings=observer_settings.logging)
        rabbitmq_settings = RabbitMQSettings()  # type: ignore
        publisher_settings = RabbitMQPublisherConfig()

        run_observer(
            settings=observer_settings,
            rabbitmq_settings=rabbitmq_settings,
            publisher_settings=publisher_settings,
        )
    except KeyboardInterrupt:
        log.warning("Cancelled by user")
    except Exception as e:
        log.exception(e)


if __name__ == "__main__":
    main()
