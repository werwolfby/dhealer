import pytest
from mock import Mock, PropertyMock
from dhealer.healer import Healer


class TestHealer:
    @pytest.mark.parametrize("healthy", [True, False])
    def test_heal_containers(self, healthy):
        (client, container1, container2) = TestHealer._init()
        container1 = Mock()

        container2.attrs['State']['Health'] = {
                    "Status": "healthy" if healthy else "unhealthy",
                }

        healer = Healer(client)
        healer.heal_containers()

        container1.restart.assert_not_called()
        if healthy:
            container2.restart.assert_not_called()
        else:
            container2.restart.assert_called()

    def test_find_network_dependencies_no_dependencies(self):
        (client, container1, container2) = TestHealer._init()

        healer = Healer(client)
        dependencies = healer.find_network_dependencies(container1.id)

        assert len(dependencies) == 0

    def test_find_network_dependencies_single_dependencies(self):
        (client, container1, container2) = TestHealer._init()

        container2.attrs['HostConfig']['NetworkMode'] = 'container:' + container1.id

        healer = Healer(client)
        dependencies = healer.find_network_dependencies(container1.id)

        assert len(dependencies) == 1
        assert dependencies[0] == container2.id

    def test_reorder_dependencies_no_dependencies(self):
        (client, container1, container2) = TestHealer._init()

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container1.id])

        assert len(dependencies) == 1
        assert dependencies[0] == container1.id

    def test_reorder_dependencies_single_dependencies(self):
        (client, container1, container2) = TestHealer._init()

        container2.attrs['HostConfig']['NetworkMode'] = 'container:' + container1.id

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container1.id])

        assert len(dependencies) == 2
        assert dependencies[0] == container1.id
        assert dependencies[1] == container2.id

    def test_reorder_dependencies_multiple_dependencies(self):
        (client, container1, container2, container3) = TestHealer._init(3)

        container2.attrs['HostConfig']['NetworkMode'] = 'container:' + container1.id
        container3.attrs['HostConfig']['NetworkMode'] = 'container:' + container1.id

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container1.id])

        assert len(dependencies) == 3
        assert dependencies[0] == container1.id
        assert dependencies[1] == container2.id
        assert dependencies[2] == container3.id

    def test_reorder_dependencies_multiple_deep_dependencies(self):
        (client, container1, container2, container3) = TestHealer._init(3)

        container2.attrs['HostConfig']['NetworkMode'] = 'container:' + container1.id
        container3.attrs['HostConfig']['NetworkMode'] = 'container:' + container2.id

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container1.id])

        assert len(dependencies) == 3
        assert dependencies[0] == container1.id
        assert dependencies[1] == container2.id
        assert dependencies[2] == container3.id

    def test_reorder_dependencies_multiple_unhealthy_different_dependencies(self):
        (client, container1, container2, container3, container4) = TestHealer._init(4)

        container1.attrs['State']['Health'] = {
                    "Status": "unhealthy",
                }
        container3.attrs['State']['Health'] = {
                    "Status": "unhealthy",
                }
        container2.attrs['HostConfig']['NetworkMode'] = 'container:' + container1.id
        container4.attrs['HostConfig']['NetworkMode'] = 'container:' + container3.id

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container1.id, container3.id])

        assert len(dependencies) == 4
        assert dependencies[0] == container1.id
        assert dependencies[1] == container2.id
        assert dependencies[2] == container3.id
        assert dependencies[3] == container4.id

    def test_reorder_dependencies_cross_dependencies(self):
        (client, container1, container2, container3) = TestHealer._init(3)

        container1.attrs['HostConfig']['NetworkMode'] = 'container:' + container3.id

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container1.id, container3.id])

        assert len(dependencies) == 2
        assert dependencies[0] == container3.id
        assert dependencies[1] == container1.id

    def test_reorder_dependencies_multiple_cross_deep_dependencies(self):
        (client, container1, container2, container3, container4) = TestHealer._init(4)

        container1.attrs['HostConfig']['NetworkMode'] = 'container:' + container2.id
        container2.attrs['HostConfig']['NetworkMode'] = 'container:' + container4.id
        container3.attrs['HostConfig']['NetworkMode'] = 'container:' + container4.id

        healer = Healer(client)
        dependencies = healer.reorder_dependencies([container4.id])

        assert len(dependencies) == 4
        assert dependencies[0] == container4.id
        assert dependencies[1] == container2.id
        assert dependencies[2] == container1.id
        assert dependencies[3] == container3.id

    @staticmethod
    def _init(count=2):
        containers = []

        for i in range(count):
            container = Mock()
            container.id = str(i + 1) * 6
            container.attrs = {
                'State': {
                    'Status': 'running',
                },
                'HostConfig': {
                    'NetworkMode': 'host',
                },
            }
            containers.append(container)

        def get_container(id):
            for container in containers:
                if container.id == id:
                    return container
            raise KeyError('Can\'t find container by id')

        client = Mock()
        client.containers = PropertyMock()
        client.containers.list = Mock(return_value=containers)
        client.containers.get = Mock(side_effect=get_container)

        return tuple([client] + containers)
