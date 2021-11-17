from .conftest import unexpected_response_error
from django.urls import reverse

get_raffle_url = reverse('raffle-list')

def test_raffle_list(client, raffle_factory):
    """List raffles sorted by creation time in descending order"""

    resp= client.get(get_raffle_url)

    assert resp.status_code == 200, unexpected_response_error(resp)
    assert len(resp.json()['results']) == 0

    raffle_factory(name="Glue")
    raffle_factory(name="Bar")
    raffle_factory(name="Foo")

   
    raffles = client.get(get_raffle_url).json()['results']

    
    assert ['Glue', 'Bar', 'Foo'] == [raffle["name"] for raffle in raffles]


def test_raffle_detail(client, raffle_factory, get_ticket):
    """Get raffle details by id counting available tickets"""

    
    raffle = raffle_factory(name="Barfoo", total_tickets=20)
   
  
    resp = client.get(f"/raffles/{raffle['data'][0]['raffle_id']}/")
  

    assert resp.status_code == 200, unexpected_response_error(resp)
    data1 = resp.json()
    assert data1["name"] == "Barfoo"
    assert data1["total_tickets"] == 20
    assert data1["available_tickets"] == 20
    assert data1['winners_drawn'] is False

    get_ticket(raffle['data'][0]['raffle_id'])

   
    data2 = client.get(f"/raffles/{raffle['data'][0]['raffle_id']}/").json()
  
    
    assert data2["total_tickets"] == 20
    assert data2["available_tickets"] == 19
    assert data2['winners_drawn'] is False
