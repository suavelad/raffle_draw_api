import exrex

from rest_framework import serializers
from raffle_app.models import Raffle,Tickets,Prizes
# from .models import 
from rest_framework.generics import get_object_or_404
from .utils import get_client_ip,get_random_string
from decouple import config


MANAGER_IPS = config('MANAGER_IPS')

class PrizeSerializer(serializers.ModelSerializer):
        
    class Meta:
        model = Prizes
        read_only_fields =('id','raffle','amount_left','created_date','created_time','updated_at')
        fields = ['id', 'raffle','name','amount','amount_left','created_date','created_time','updated_at']





class  RaffleSerializer(serializers.ModelSerializer):
    prizes = PrizeSerializer(required=True, many=True)
    total_tickets = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)
    # raffleid = serializers.SerializerMethodField(read_only=True)
    
    
    # def get_raffleid(self,obj):
    #     # d=hypothesis.strategies.from_regex(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
    #     # new_id = d.example()
    #     new_id  = exrex.getone(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
    #     ids = Raffle.objects.filter(id=new_id).exists()
    #     if ids:
    #         # d=hypothesis.strategies.from_regex(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
    #         # new_id = d.example()
    #         new_id  = exrex.getone(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
    #         ids = Raffle.objects.filter(id=new_id).exists()
    #     else:
    #         return new_id
            
        
    def create(self, validated_data):
        total_tickets = validated_data['total_tickets']
        prizes = validated_data['prizes']
        request= self.context.get('request')
        current_ip = get_client_ip(request)
        
        new_id  = exrex.getone(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
        ids = Raffle.objects.filter(raffle_id=new_id).exists()
        if ids:
            # d=hypothesis.strategies.from_regex(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
            # new_id = d.example()
            new_id  = exrex.getone(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")
            ids = Raffle.objects.filter(raffle_id=new_id).exists()
        else:
            raffleid= new_id
        raffleid= new_id
        # raffle =  Raffle.objects.create(raffle_id=raffle_id,remote_ip=current_ip,available_tickets=total_tickets,**validated_data)
        raffle =  Raffle.objects.create(raffle_id=raffleid,remote_ip=current_ip,available_tickets=total_tickets,**validated_data)
        raffle.save()
       
        # raffle_id = raffle.id
        # print (raffle_id )
        
 
        # Store the generated Tickets for a particular raffle draw
        for ticket_number in range(1,total_tickets+1):
            ticket = Tickets.objects.create(raffle=raffle,ticket_number=ticket_number)
            ticket.save()
        
        # Store the Prizes for a particular raffle draw
        
        
        for prize in prizes:
            d_prize = Prizes.objects.create(raffle=raffle,name=prize['name'],amount=prize['amount'],amount_left=prize['amount'])
            d_prize.save()
                
        return validated_data
    

    
    class Meta:
        model = Raffle
        read_only_fields=('id','raffle_id','available_tickets','remote_ip','created_date','created_time','winners_drawn','updated_at')
        fields = [ 'id','raffle_id','name','total_tickets','prizes','available_tickets','winners_drawn','remote_ip','created_date','created_time','updated_at']
        lookup_field = "raffle_id"
        
        
class TicketSerializer(serializers.ModelSerializer):
    prize = serializers.SerializerMethodField(read_only=True)
    raffle = serializers.SerializerMethodField(read_only=True)

    
    def get_prize(self,data):
       
        if data.prize is not None:
            
            prize = get_object_or_404(Prizes,name=data.prize.id)
           
            return prize.name
        else:
            return 'None'
    
    
    def get_raffle(self, data):
        
        raffle = get_object_or_404(Raffle,id=data.id)
        
        return raffle.name
    
    class Meta:
        model = Tickets
        read_only_fields= ('id','ticket_number','verification_code','participant_ip','winners_drawn','has_won','prize','raffle','created_date','created_time','updated_at')
        fields = [ 'ticket_number','participant_name','participant_ip','raffle','prize','winners_drawn','has_won','verification_code','has_won','created_date','created_time','updated_at']
     

class GetTicketSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(required=True)
    prize = serializers.SerializerMethodField(read_only=True)
    raffle = serializers.SerializerMethodField(read_only=True)

    def get_prize(self,data):
        if data.prize is not None:
            prize = get_object_or_404(Prizes,id=data.prize.id)
            return prize.name
        else:
            return 'None'
    
    
    def get_raffle(self, data):
        raffle = get_object_or_404(Raffle,id=data.raffle.id)
        return raffle.raffle_id
    
    class Meta:
        model = Tickets
        read_only_fields= ('id','ticket_number','verification_code','participant_ip','has_won','prize','raffle','created_date','created_time','updated_at')
        fields = [ 'id', 'ticket_number','participant_name','participant_ip','raffle','prize','has_won','verification_code','has_won','created_date','created_time','updated_at']



class VerifyTicketSerializer(serializers.ModelSerializer):
    verification_code = serializers.CharField(required=True)
    ticket_number = serializers.CharField(required=True)
    
    prize = serializers.SerializerMethodField(read_only=True)
    raffle = serializers.SerializerMethodField(read_only=True)

    def get_prize(self,data):
        if data.prize is not None:
            prize = get_object_or_404(Prizes,id=data.prize.id)
            return prize.name
        else:
            return 'None'
    
    
    def get_raffle(self, data):
        raffle = get_object_or_404(Raffle,id=data.raffle.id)
        return raffle.name
    
    class Meta:
        model = Tickets
        read_only_fields= ('id','ticket_number','verification_code','participant_name','raffle','prize','participant_ip','has_won','prize','raffle','created_date','created_time','updated_at')
        fields = [ 'id', 'ticket_number','participant_name','participant_ip','raffle','prize','has_won','verification_code','has_won','created_date','created_time','updated_at']

    
    
    
    
    