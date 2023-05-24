from requests_mock import Mocker

from python_aternos.atconnect import BASE_URL, AJAX_URL
from tests import files

mock = Mocker()

with mock:

    mock.get(
        f'{BASE_URL}/go/',
        content=files.read_html('aternos_go'),
    )

    mock.get(
        f'{BASE_URL}/servers/',
        content=files.read_html('aternos_servers'),
    )

    mock.get(
        f'{BASE_URL}/server/',
        content=files.read_html('aternos_server1'),
    )

    mock.get(
        f'{AJAX_URL}/status.php',
        content=files.read_html('aternos_status'),
    )

    mock.post(
        f'{AJAX_URL}/account/login.php',
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
        f'{BASE_URL}/players/',
        content=files.read_html('aternos_players'),
    )

    mock.get(
        f'{BASE_URL}/files/',
        content=files.read_html('aternos_file_root'),
    )
