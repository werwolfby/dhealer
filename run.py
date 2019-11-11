import docker
from time import sleep
from dhealer.healer import Healer

if __name__ == '__main__':
    client = docker.client.from_env()
    healer = Healer(client)

    while True:
        healer.heal_containers()
        sleep(5 * 60)
