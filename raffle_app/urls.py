from django.urls import path

from rest_framework.routers import DefaultRouter

from .apis import RaffleViewSet, TicketViewSet, PrizesViewSet,GetTicketView,DrawWinnersView,VerifyTicketView


routers = DefaultRouter()



routers.register('raffles',RaffleViewSet,'raffle')
# routers.register('ticket',TicketViewSet,'ticket')
# routers.register('prize',PrizesViewSet,'prize')


urlpatterns = routers.urls

urlpatterns += [
    path('raffles/<id>/participate/', GetTicketView.as_view(), name='raffle_participate'),
    path('raffles/<id>/winners/', DrawWinnersView.as_view(), name='raffle_draw_winners'),
    path('raffles/<id>/verify-ticket/', VerifyTicketView.as_view(), name='raffle_verify_ticket'),
    
    
]
