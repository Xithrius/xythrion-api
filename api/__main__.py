import logging
import os
import shutil

import uvicorn

from .gunicorn_runner import GunicornApplication
from .logging import EndpointFilter
from .settings import settings


def set_multiproc_dir() -> None:
    shutil.rmtree(settings.prometheus_dir, ignore_errors=True)

    os.makedirs(settings.prometheus_dir, exist_ok=True)

    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(
        settings.prometheus_dir.expanduser().absolute(),
    )
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(
        settings.prometheus_dir.expanduser().absolute(),
    )


def main() -> None:
    set_multiproc_dir()

    if settings.reload:
        logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

        uvicorn.run(
            "api.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        GunicornApplication(
            "api.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',
        ).run()


if __name__ == "__main__":
    main()
