import re

from .conftest import unexpected_response_error
from django.urls import reverse


ID_PATTERN = re.compile(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")

create_raffle_url = reverse('raffle-list')

def test_create_raffle_trusted_ip(client, default_raffle, manager_ip):
    """Create raffle from whitelisted manager ip address"""

    resp = client.post(create_raffle_url, data=default_raffle, REMOTE_ADDR=manager_ip)

 
    assert resp.status_code == 201, unexpected_response_error(resp)
    data = resp.json()
    assert data['data'][0]["name"] == "Foobar raffle"
    assert data['data'][0]["total_tickets"] == default_raffle['total_tickets']
    assert data['data'][0]["available_tickets"] == default_raffle['total_tickets']
    assert data['data'][0]['winners_drawn'] is False
    assert ID_PATTERN.match(data['data'][0]['raffle_id']), "Unexpected raffle id format"


def test_create_raffle_untrusted_ip(client, default_raffle):
    """Can't create raffle from a non-manager ip address"""

  
    resp = client.post(create_raffle_url, data=default_raffle,
                       REMOTE_ADDR="123.234.123.234")
    assert resp.status_code == 403, unexpected_response_error(resp)


def test_create_raffle_with_no_prizes(client, manager_ip):
    """Can't create raffle with no prizes"""

   
    resp = client.post(create_raffle_url,
                       data={'name': 'Lack of prizes',
                             'total_tickets': 30,
                             'prizes': []},
                       REMOTE_ADDR=manager_ip)
    assert resp.status_code == 400, unexpected_response_error(resp)


def test_create_raffle_with_too_many_prizes(client, manager_ip):
    """Can't create raffle with more prizes than tickets"""


    resp = client.post(create_raffle_url,
                       data={'name': 'Lack of tickets',
                             'total_tickets': 30,
                             'prizes': [{'name': 'funny hat', 'amount': 50}]},
                       REMOTE_ADDR=manager_ip)
    assert resp.status_code == 400, unexpected_response_error(resp)
    assert b'Too many prizes' in resp.content
