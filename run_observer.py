import logging

from src.core.conf import ObserverSettings, setup_logging
from src.services.observer.main import run_observer

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    try:
        log = logging.getLogger(__name__)

        observer_settings = ObserverSettings()  # type: ignore

        setup_logging(settings=observer_settings.logging)

        run_observer(settings=observer_settings)
    except KeyboardInterrupt:
        log.warning("Cancelled by user")
    except Exception as e:
        log.exception(e)
