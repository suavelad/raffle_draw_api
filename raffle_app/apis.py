from .utils import get_client_ip,get_random_string
from django.shortcuts import get_object_or_404

from django.db.models import Sum
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework import status,mixins,viewsets
from decouple import config
from  drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Raffle,Prizes,Tickets
from .serializers import RaffleSerializer,PrizeSerializer,GetTicketSerializer,VerifyTicketSerializer,TicketSerializer


MANAGER_IPS = config('MANAGER_IPS')

class RaffleViewSet (mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin, 
                    mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Raffle.objects.all()
    serializer_class = RaffleSerializer
    lookup_field = 'raffle_id'
 
    
    def create(self,request,*args, **kwargs):
        manager_ip = get_client_ip(self.request)
        # print('api manager ip:', manager_ip, MANAGER_IPS)
        if manager_ip in MANAGER_IPS:
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                result = serializer.save()
                # import pdb
                # pdb.set_trace()
            
                prize_items = len(result['prizes'])
                tickets = result['total_tickets']
                no_of_prizes = 0
                
                if prize_items > 0 :
                    for prize in result['prizes']:
                        no_of_prizes += int(prize['amount'] )
                    
                    
                    if no_of_prizes <= tickets:

                        serializer = RaffleSerializer
                        queryset = Raffle.objects.filter(name=result['name'])
    
                        return Response({
                            'status':'success','data':serializer(queryset,many=True).data},status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                        'status':'error','message':'Too many prizes for this Raffle Draw'},status=status.HTTP_400_BAD_REQUEST)
                  
                else:
                    return Response({
                        'status':'error','message':'You cannot create a Raffle without a prize'},status=status.HTTP_400_BAD_REQUEST)
                    
                # return Response({
                #     'status':'success','data':result},status=status.HTTP_201_CREATED)

        else:
            return Response({'status':'error','message':'You are not a Manager'},status=status.HTTP_403_FORBIDDEN)
        

class TicketViewSet (
    
                   mixins.RetrieveModelMixin, 
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Tickets.objects.all()
    serializer_class = TicketSerializer
   
    
    def get_queryset(self):
        manager_ip = get_client_ip(self.request)
        if manager_ip in MANAGER_IPS:
            ticket = Tickets.objects.all()
            import pdb
            pdb.set_trace()
            return ticket
        
        raise ValidationError ({'status':'error','message':'You are not a Manager'})
    
    
class PrizesViewSet ( mixins.RetrieveModelMixin, 
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset= Prizes.objects.all()
    serializer_class = PrizeSerializer
    
    
    def get_queryset(self):
        manager_ip = get_client_ip(self.request)
        if manager_ip in MANAGER_IPS:
            prizes = Prizes.objects.all()
            return prizes
        
        raise ValidationError ({'status':'error','message':'You are not a Manager'})
    
    
#For participant getting a ticket

class GetTicketView(APIView):
    
    
    @swagger_auto_schema(request_body=GetTicketSerializer)
    def post(self,request,id):
        serializer = GetTicketSerializer(data=request.data)
        if serializer.is_valid():
            participant_name = serializer.validated_data['participant_name']
        
            participant_ip = get_client_ip(self.request)
            
            
            raffle = Raffle.objects.filter(raffle_id=id).first()
            if  raffle :
                
                # import pdb
                # pdb.set_trace()
                raffle_id = raffle.id
                raffle_tickets_left =raffle.available_tickets
                
                is_participant_exist = Tickets.objects.filter(raffle_id=raffle_id,participant_ip=participant_ip).first()
               
                random_ticket = Tickets.objects.filter(raffle_id=raffle_id,verification_code__isnull=True).order_by('?').first()
                                
                verification_code = get_random_string(10)
                is_verification_code_exist = Tickets.objects.filter(raffle_id=raffle_id,verification_code=verification_code)
                
                while is_verification_code_exist == True:
                    is_verification_code_exist = Tickets.objects.filter(raffle_id=raffle_id,verification_code=verification_code)
                    verification_code = get_random_string(10)
                    
            
                # Check the tickets left 
                if raffle_tickets_left  != 0 :
                    
                    # Allow only participant that has not participated in this raffle draw
                    if is_participant_exist is None:
                        
                        # Update the Tickets  participant name ,participant ip, verification code, has_won,prize
                        random_ticket.participant_ip = participant_ip
                        random_ticket.participant_name = participant_name
                        
                        random_ticket.verification_code = verification_code
                        random_ticket.save()
     
                        # update the number of available tickets on the raffle model
                        raffle.available_tickets -= 1
                        raffle.save() 
                        
                        # serializer = GetTicketSerializer
                        queryset = Tickets.objects.filter(id=random_ticket.id)
                    
                        return Response({
                            'status': 'success',
                            'message':'Successfully gotten a Ticket Number',
                            'ticket':GetTicketSerializer(queryset,many=True).data
                        },status=status.HTTP_201_CREATED)
                    
                    
                    else:
                        return Response({
                        'status': 'error',
                        'message':'Your ip address has already participated in this raffle'
                    },status=status.HTTP_403_FORBIDDEN)
                        
                
                else:
                    return Response({
                        'status': 'error',
                        'message':'Tickets to this raffle are no longer available'
                    },status=status.HTTP_410_GONE)
                
            else:
                return Response({
                    'status': 'error',
                    'message':'Raffle id is not valid'
                },status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({
                    'status': 'error',
                    'message':'Invalid Data Passed'
                },status=status.HTTP_400_BAD_REQUEST)



class DrawWinnersView(APIView):
    
    # This api is to Draw the Winners by only managers
    def post(self,request,id):
        
        manager_ip = get_client_ip(self.request)
        if manager_ip in MANAGER_IPS:
            
            try:
               
                raffle = Raffle.objects.filter(raffle_id=id).first()
                raffle_id = raffle.id
                available_tickets = Tickets.objects.filter(raffle_id=raffle_id,verification_code__isnull=True)

                is_raffle_drawn = raffle.winners_drawn
                
                if not is_raffle_drawn :
                    if not available_tickets.exists():
                    
                        valid_tickets = Tickets.objects.filter(raffle_id=raffle_id,verification_code__isnull=False,winners_drawn=False)
                        
                        print (raffle.prizes)
                        for valid_ticket in valid_tickets:
                            random_prize = Prizes.objects.exclude(amount_left=0).filter(raffle_id=raffle_id).order_by('?').first()
                            print (len(Prizes.objects.exclude(amount_left=0).filter(raffle_id=raffle_id)))
                            print(random_prize.name, random_prize.amount, random_prize.amount_left)
                            valid_ticket.has_won = True if random_prize is not None else False 
                            valid_ticket.prize = random_prize if random_prize is not None else None
                            valid_ticket.winners_drawn = True
                            valid_ticket.save()
                        
                            random_prize.amount_left -= 1 if random_prize.amount_left !=0 else 0
                            random_prize.save()
                            

                        raffle.winners_drawn= True
                        raffle.save()
                        
                        serializer = TicketSerializer
                        queryset = Tickets.objects.filter(raffle_id=raffle_id,verification_code__isnull= False,has_won=True)
                       
                        return Response({
                            'status': 'success',
                            'message':'Raffle Draw Successful',
                            'raffle': raffle.name,
                            'winners': serializer(queryset,many=True).data
                        },status=status.HTTP_201_CREATED)

                    else:
                        return Response({
                            'status': 'error',
                            'message':'Winners can\'t be drawn when tickets are still available'
                        },status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({
                        'status': 'error',
                        'message':'Winners for the raffle have already been drawn'
                    },status=status.HTTP_403_FORBIDDEN)
                
            except:
                return Response({
                    'status': 'error',
                    'message':'Invalid id passed .It must be a regex format'
                },status=status.HTTP_403_FORBIDDEN)
        
        else:
            return Response({'status':'error','message':'You are not a Manager'},status=status.HTTP_403_FORBIDDEN)
  
    # This api is to List the Winners
    def get(self,request,id):
        
        try:
            raffle = Raffle.objects.filter(raffle_id=id).first()
            raffle_id = raffle.id
            
            is_raffle_drawn = raffle.winners_drawn
            
            if  is_raffle_drawn :
                    
                serializer = TicketSerializer
                queryset = Tickets.objects.filter(raffle_id=raffle_id,verification_code__isnull= False,has_won=True)
                
                return Response({
                    'status': 'success',
                    'message':'Raffle Draw Winners',
                    'raffle': raffle.name,
                    'winners': serializer(queryset,many=True).data
                },status=status.HTTP_200_OK)

            else:
                return Response({
                    'status': 'error',
                    'message':'Raffle Draw has not been done.Kindly Wait.'
                },status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({
                    'status': 'error',
                    'message':'Invalid id passed .It must be a regex format'
                },status=status.HTTP_400_BAD_REQUEST)
            



class  VerifyTicketView(APIView):
    
    @swagger_auto_schema(request_body=VerifyTicketSerializer)
    def post(self,request,id):
        raffle = Raffle.objects.filter(raffle_id=id).first()
        raffle_id = raffle.id
        verification_code=request.data['verification_code']
        ticket_number = request.data['ticket_number']
        available_tickets = Tickets.objects.filter(raffle_id=raffle_id,verification_code__isnull=True)
        
        if not available_tickets.exists():
        
            if verification_code is not None and type(verification_code) != int :
    
                # try:
                #     verify_ticket_id = Tickets.objects.filter(raffle_id=raffle_id,verification_code=verification_code).first()
                #     return Response({
                #         'status': 'error',
                #         'message':'Invalid verification code'
                #     },status=status.HTTP_400_BAD_REQUEST)
                    
                # except:
                verify_code = Tickets.objects.filter(raffle_id=raffle_id,verification_code=verification_code).first()
                
                # import pdb
                # pdb.set_trace()
                
                if int(ticket_number) == int(verify_code.ticket_number) and verify_code is not None:
                    print(ticket_number)
                    
                
                    if verify_code is not None:
                        has_won = verify_code.has_won
                        
                        if has_won:
                            return Response({
                                'status': 'success',
                                'message':'You Won',
                                'data':{'raffle': verify_code.raffle.name,
                                        'has_won':verify_code.has_won,
                                        'prize': verify_code.prize.name,
                                        'verification_code': verify_code.verification_code,
                                        'ticket_number':verify_code.ticket_number}
                            },status=status.HTTP_200_OK)
                            
                        else:
                            return Response({
                                'status': 'success',
                                'message':'You Lost',
                                'data':{'raffle': verify_code.raffle.name,
                                        'prize': 'None',
                                        'verification_code': verify_code.verification_code,
                                        'ticket_number':verify_code.ticket_number}
                            },status=status.HTTP_200_OK)
                    
                    else:
                        return Response({
                            'status': 'Error',
                            'message':'Invalid verification code'
                        },status=status.HTTP_400_BAD_REQUEST)
                else:
                        return Response({
                            'status': 'Error',
                            'message':'Invalid verification code'
                        },status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'status': 'Error',
                    'message':'Invalid verification code'
                },status=status.HTTP_400_BAD_REQUEST)  
        else:
                return Response({
                    'status': 'error',
                    'message':'Winners for the raffle have not been drawn yet'
                },status=status.HTTP_400_BAD_REQUEST)
                
                