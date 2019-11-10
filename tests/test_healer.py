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

    @staticmethod
    def _init():
        container1 = Mock()
        container1.id = '1111'
        container1.attrs = {
            'State': {
                'Status': 'running',
            },
            'HostConfig': {
                'NetworkMode': 'host',
            },
        }

        container2 = Mock()
        container2.id = '2222'
        container2.attrs = {
            'State': {
                'Status': 'running',
            },
            'HostConfig': {
                'NetworkMode': 'host',
            },
        }

        client = Mock()
        client.containers = PropertyMock()
        client.containers.list = Mock(return_value=[container1, container2])

        return client, container1, container2
