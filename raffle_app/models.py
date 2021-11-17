# from testing.conftest import raffle

from django.db import models 
from django.core.validators import RegexValidator
from mirage import fields

# Create your models here.


ID_REGEX = RegexValidator(r"^[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}$")

class Raffle (models.Model):
    
    MANAGER_IPS=(
        ('123.123.123.123','123.123.123.123'),
        ('127.0.0.2','127.0.0.2')
        )
    id = models.AutoField(primary_key=True)
    raffle_id = models.TextField(validators=[ID_REGEX])
    name = models.CharField(max_length=255)
    total_tickets = models.IntegerField()
    available_tickets = models.IntegerField(null=True, blank=True)
    prizes = models.JSONField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)
    remote_ip = models.GenericIPAddressField(choices=MANAGER_IPS)
    created_time = models.TimeField(auto_now_add=True)
    created_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    winners_drawn = models.BooleanField(default=False)
    

    # class Meta:
    #     # verbose_name = 'Raffle'
    #     ordering= ['-created_date','-created_time']
        
    # def __str__(self):
    #     return str(self.name)
        
 
    
class Prizes(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    raffle = models.ForeignKey(Raffle, on_delete=models.DO_NOTHING,related_name='raffle_prize')
    amount = models.IntegerField(null=True, blank=True)
    amount_left = models.IntegerField(null=True, blank=True)
    created_time = models.TimeField(auto_now_add=True)
    created_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # class Meta:
    #     # verbose_name = 'Prizes'
    #     ordering= ['-created_date','-created_time']
        
    # def __str__(self):
    #     return str(self.name)
    
    
class Tickets(models.Model):
    id = models.AutoField(primary_key=True)
    raffle = models.ForeignKey(Raffle, on_delete=models.DO_NOTHING,related_name='raffle_ticket')
    ticket_number = models.IntegerField()
    verification_code= fields.EncryptedCharField(max_length=100, null=True, blank=True)
    has_won = models.BooleanField(default=False)
    participant_ip = models.CharField(max_length=20, null=True, blank=True)
    participant_name = models.TextField(null=True, blank=True)
    prize = models.ForeignKey(Prizes,on_delete=models.DO_NOTHING, null=True,blank=True)
    created_time = models.TimeField(auto_now_add=True)
    winners_drawn = models.BooleanField(default=False)
    created_date = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # class Meta:
    #     # verbose_name = 'Tickets'
    #     unique_together = ['verification_code']
    #     # ordering= ['-created_date','-created_time']
    #     ordering=  ['-updated_at']
        
        
    # def __str__(self):
    #     return 'Ticket Number: '+str(self.ticket_number)
