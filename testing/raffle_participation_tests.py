from .conftest import unexpected_response_error
from django.urls import reverse


class TestParticipate:
    def test_get_ticket(self, client,default_raffle_participant, raffle):
        """Get a ticket to participate in a raffle"""
        
        participate_raffle_url = reverse('raffle_participate',kwargs={'id':raffle['data'][0]['raffle_id']})
        resp = client.post(participate_raffle_url,data=default_raffle_participant)
        
        assert resp.status_code == 201, unexpected_response_error(resp)
        data = resp.json()
       
        assert  data['ticket'][0]['raffle']== raffle['data'][0]['raffle_id']
        assert 1 <= data['ticket'][0]['ticket_number'] <= raffle['data'][0]['total_tickets']
        assert bool(data['ticket'][0]['verification_code']) is True

    def test_get_ticket_none_left(self, client, raffle,default_raffle_participant, get_ticket, ip_factory):
        """Can't get a ticket if none are left"""
        
        participate_raffle_url = reverse('raffle_participate',kwargs={'id':raffle['data'][0]['raffle_id']})

      
        
        for n in range(raffle['data'][0]['total_tickets'] - 1):
            
            get_ticket(raffle['data'][0]['raffle_id'])
            
            

        
        resp1 = client.post(participate_raffle_url,data=default_raffle_participant,REMOTE_ADDR=ip_factory)
     
        assert resp1.status_code == 201, unexpected_response_error(resp1)
        
        
        resp2 = client.post(participate_raffle_url,data=default_raffle_participant,REMOTE_ADDR=ip_factory)
        assert resp2.status_code == 410, unexpected_response_error(resp2)
        assert b'Tickets to this raffle are no longer available' in resp2.content

    def test_get_second_ticket_from_same_ip(self, client,default_raffle_participant, raffle):
        """Same same ip can't get more than one ticket to a rafffle"""
        
        participate_raffle_url = reverse('raffle_participate',kwargs={'id':raffle['data'][0]['raffle_id']})

        
        resp1 = client.post(participate_raffle_url,data=default_raffle_participant,REMOTE_ADDR='234.234.234.234')
        assert resp1.status_code == 201, unexpected_response_error(resp1)
        
        resp2 = client.post(participate_raffle_url,data=default_raffle_participant,REMOTE_ADDR='234.234.234.234')
        assert resp2.status_code == 403, unexpected_response_error(resp2)
        assert b'Your ip address has already participated in this raffle' in resp2.content

    def test_get_tickets_to_different_raffles_from_same_ip(self, client,default_raffle_participant, raffle_factory):
        """Same ip can participate in multiple raffles"""
        
        participant_ip = '234.234.234.234'
        raffle1 = raffle_factory()
        raffle2 = raffle_factory()
     
        participate_raffle_url = reverse('raffle_participate',kwargs={'id':raffle1['data'][0]['raffle_id']})
        resp1 = client.post(participate_raffle_url,data=default_raffle_participant,REMOTE_ADDR=participant_ip)
        assert resp1.status_code == 201, unexpected_response_error(resp1)
        
        participate_raffle_url = reverse('raffle_participate',kwargs={'id':raffle2['data'][1]['raffle_id']})
        resp2 = client.post(participate_raffle_url,data=default_raffle_participant,REMOTE_ADDR=participant_ip)
        assert resp2.status_code == 201, unexpected_response_error(resp2)
