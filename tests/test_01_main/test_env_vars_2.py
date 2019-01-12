import time

import docker
import pytest

from ..utils import (
    CONTAINER_NAME,
    get_config,
    get_process_names,
    stop_previous_container,
)

client = docker.from_env()


@pytest.mark.parametrize(
    "image",
    [
        ("tiangolo/meinheld-gunicorn:python3.6"),
        ("tiangolo/meinheld-gunicorn:python3.7"),
        ("tiangolo/meinheld-gunicorn:latest"),
        ("tiangolo/meinheld-gunicorn:python3.6-alpine3.8"),
        ("tiangolo/meinheld-gunicorn:python3.7-alpine3.8"),
    ],
)
def test_env_vars_2(image):
    stop_previous_container(client)
    container = client.containers.run(
        image,
        name=CONTAINER_NAME,
        environment={"WEB_CONCURRENCY": 1, "HOST": "127.0.0.1"},
        ports={"80": "8000"},
        detach=True,
    )
    time.sleep(1)
    process_names = get_process_names(container)
    config_data = get_config(container)
    assert config_data["workers"] == 1
    assert len(process_names) == 2  # Manager + worker
    assert config_data["host"] == "127.0.0.1"
    assert config_data["port"] == "80"
    assert config_data["loglevel"] == "info"
    assert config_data["bind"] == "127.0.0.1:80"
    container.stop()
    container.remove()
