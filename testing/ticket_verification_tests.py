from .conftest import unexpected_response_error


def test_verify_winning_tickets(client, raffle, manager_ip, get_ticket):
    """Verify winner and loser tickets using the verification codes"""
    

    tickets = dict(
        (t['ticket'][0]['ticket_number'], t)
    for t in [get_ticket(raffle['data'][0]['raffle_id']) for _ in range(raffle['data'][0]['total_tickets'])]
    )

   
    wins = client.post(f"/raffles/{raffle['data'][0]['raffle_id']}/winners/",
                       REMOTE_ADDR=manager_ip).json()['winners']
    
   
    for win in wins:
        verification_code = win['verification_code']
        

      
        resp = client.post(f"/raffles/{raffle['data'][0]['raffle_id']}/verify-ticket/", {
            'ticket_number': win['ticket_number'],
            'verification_code': verification_code,
        })
       
        assert resp.status_code == 200, unexpected_response_error(resp)
        data = resp.json()
        
      
        assert data['data']['has_won'] is True
        assert data['data']['prize'] == win['prize']
        del tickets[win['ticket_number']]
        
       

   
    resp = client.post(f"/raffles/{raffle['data'][0]['raffle_id']}/verify-ticket/", {
            'ticket_number': wins[0]['ticket_number'],
            'verification_code': verification_code,
        })
    
    
    
    assert resp.status_code == 400, unexpected_response_error(resp)
    assert b'Invalid verification code' in resp.content

    assert len(tickets) == raffle['data'][0]["total_tickets"] - len(wins), \
        'Unexpected number of losing tickets'

    for _, loser in tickets.items():
     
        resp = client.post(f"/raffles/{raffle['data'][0]['raffle_id']}/verify-ticket/", {
            'ticket_number': loser['ticket_number'],
            'verification_code': loser['verification_code'],
        })
        assert resp.status_code == 200, unexpected_response_error(resp)
        data = resp.json()
        assert data['has_won'] is False
        assert data['prize'] is None
    
  
    
        resp = client.post(f"/raffles/{raffle['data'][0]['raffle_id']}/verify-ticket/", {
            'ticket_number': win['ticket_number'],
            'verification_code': loser['verification_code'],
        })
        assert resp.status_code == 400, unexpected_response_error(resp)
        assert b'Invalid verification code' in resp.content
