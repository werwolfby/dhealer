import time
import docker


class Healer:
    """
    :type client: docker.DockerClient
    """
    def __init__(self, client):
        self.client = client

    def heal_containers(self):
        containers = self.client.containers.list()
        for container in containers:
            state = container.attrs['State']
            if 'Health' in state and state['Health']['Status'] == 'unhealthy':
                container.restart()
