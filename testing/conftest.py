import ipaddress
import os

import pytest
from rest_framework.test import APIClient
from django.urls import reverse


MANAGER_IP = os.environ.get('MANAGER_IPS', '123.123.123.123,127.0.0.2').split(',')[0]
DEFAULT_RAFFLE = {
    "name": "Foobar raffle",
    "total_tickets": 9,
    "prizes": [
        {"name": "invisibility", "amount": 1},
        {"name": "warm hug", "amount": 3},
        {"name": "firm handshake", "amount": 5},
    ]
}

DEFAULT_PARTICIPANT = {
    'participant_name':'Sunday'
}

create_raffle_url = reverse('raffle-list')


class RaffleClient(APIClient):
    default_format = 'json'


class IncrementingIpFactory:
    def __init__(self):
        self.num = 0x01000000

    def __call__(self):
        self.num += 1
        return ipaddress.IPv4Address._string_from_ip_int(self.num)


make_ip = IncrementingIpFactory()


def unexpected_response_error(resp):
    return f'Unexpected response {resp.status_code} / {resp.content}'


def make_raffle(client, **overrides):
    # resp = client.post("/raffles/",
    #                    data=DEFAULT_RAFFLE | overrides,
    #                    REMOTE_ADDR=MANAGER_IP)
    resp = client.post(create_raffle_url, data=DEFAULT_RAFFLE | overrides,
                       REMOTE_ADDR=MANAGER_IP)

    if resp.status_code != 201:
        raise Exception('Unable to create a raffle')
    return resp.json()


@pytest.fixture
def ip_factory():
    return make_ip()


@pytest.fixture
def client():
    return RaffleClient()


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


@pytest.fixture
def get_ticket(client):
    def _inner(raffle_id):
        
        
        participate_raffle_url = reverse('raffle_participate',kwargs={'id':raffle_id})

        
        resp = client.post(participate_raffle_url,data=DEFAULT_PARTICIPANT,REMOTE_ADDR=make_ip())

        if resp.status_code != 201:
            raise Exception('Unable to get a ticket to the raffle')
        return resp.json()
    return _inner


@pytest.fixture
def raffle(client):
    return make_raffle(client=client)


@pytest.fixture
def raffle_factory(client):
    def _factory(**overrides):
        return make_raffle(client, **overrides)
    return _factory


@pytest.fixture
def default_raffle():
    return DEFAULT_RAFFLE

@pytest.fixture
def default_raffle_participant():
    return DEFAULT_PARTICIPANT

@pytest.fixture
def manager_ip():
    return MANAGER_IP
