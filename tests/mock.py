from requests_mock import Mocker
from tests import files

mock = Mocker()

with mock:

    mock.get(
        'https://aternos.org/go/',
        content=files.read_html('aternos_go'),
    )

    mock.get(
        'https://aternos.org/servers/',
        content=files.read_html('aternos_servers'),
    )

    mock.get(
        'https://aternos.org/server/',
        content=files.read_html('aternos_server1'),
    )

    mock.get(
        'https://aternos.org/panel/ajax/status.php',
        content=files.read_html('aternos_status'),
    )

    mock.post(
        'https://aternos.org/panel/ajax/account/login.php',
        json={
            'success': True,
            'error': None,
            'message': None,
            'show2FA': False,
        },
        cookies={
            'ATERNOS_SESSION': '0123abcd',
        },
    )

    mock.get(
        'https://aternos.org/players/',
        content=files.read_html('aternos_players'),
    )

    mock.get(
        'https://aternos.org/files/',
        content=files.read_html('aternos_file_root'),
    )
