import pytest
from mock import Mock, PropertyMock
from dhealer.healer import Healer


class TestHealer:
    @pytest.mark.parametrize("healthy", [True, False])
    def test_heal_containers(self, healthy):
        client = Mock()
        client.containers = PropertyMock()
        container1 = Mock()
        container1.attrs = {
            'State': {
                'Status': 'running',
            },
        }

        container2 = Mock()
        container2.attrs = {
            'State': {
                'Status': 'running',
                'Health': {
                    "Status": "healthy" if healthy else "unhealthy",
                },
            },
        }

        client.containers.list = Mock(return_value=[container1, container2])

        healer = Healer(client)
        healer.heal_containers()

        container1.restart.assert_not_called()
        if healthy:
            container2.restart.assert_not_called()
        else:
            container2.restart.assert_called()
