import docker
import logging
from time import sleep
from dhealer.healer import Healer

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting")

    client = docker.client.from_env()
    logging.info("Connected to docker")
    healer = Healer(client)

    while True:
        logging.info("Heal unhealthy containers")
        healer.heal_containers()
        sleep(5 * 60)
