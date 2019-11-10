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

    def find_network_dependencies(self, id):
        container_network_mode_prefix = "container:"

        container_ids = []

        containers = self.client.containers.list()
        for container in containers:
            network_mode = container.attrs['HostConfig']['NetworkMode']
            if network_mode.startswith(container_network_mode_prefix) and network_mode[len(container_network_mode_prefix):].lower() == id.lower():
                container_ids.append(container.id.lower())

        return container_ids

