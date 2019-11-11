import docker
import logging


class Healer:
    """
    :type client: docker.DockerClient
    """
    def __init__(self, client):
        self.client = client

    def heal_containers(self):
        containers = self.client.containers.list()
        restart_containers_ids = []
        for container in containers:
            state = container.attrs['State']
            if 'Health' in state and state['Health']['Status'] == 'unhealthy':
                restart_containers_ids.append(container.id)

        if len(restart_containers_ids) > 0:
            logging.info("Unhealthy containers: [{0}]".format(", ".join(restart_containers_ids)))
            restart_containers_ids = self.reorder_dependencies(restart_containers_ids)
            logging.info("Restarting containers order: [{0}]".format(", ".join(restart_containers_ids)))
            for container_id in restart_containers_ids:
                container = self.client.containers.get(container_id)
                logging.info("Restart container: {0}".format(container_id))
                container.restart()

    def find_dependencies(self, id):
        return self.find_network_dependencies(id)

    def find_network_dependencies(self, id):
        container_network_mode_prefix = "container:"

        container_ids = []

        containers = self.client.containers.list()
        for container in containers:
            network_mode = container.attrs['HostConfig']['NetworkMode']
            if network_mode.startswith(container_network_mode_prefix) and network_mode[len(container_network_mode_prefix):].lower() == id.lower():
                container_ids.append(container.id.lower())

        return container_ids

    def reorder_dependencies(self, ids):
        tree = {id: [] for id in ids}
        root = list(ids)
        new_ids = list(ids)
        while len(new_ids) > 0:
            current_ids = new_ids
            new_ids = []
            for container_id in current_ids:
                dependency_ids = self.find_dependencies(container_id)
                for dependency_id in dependency_ids:
                    if dependency_id in root:
                        root.remove(dependency_id)
                    if dependency_id not in tree:
                        tree[dependency_id] = []
                        new_ids.append(dependency_id)
                    tree[container_id].append(dependency_id)

        def flatten(item):
            result = [item]
            items = tree[item]
            for new_item in items:
                result = result + flatten(new_item)
            return result

        for i in root:
            new_ids = new_ids + flatten(i)

        return new_ids
