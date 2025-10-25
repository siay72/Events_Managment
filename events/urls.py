from django.urls import path
from events.views import home, dashboard, create_event, update_event, delete_event, event_detail, add_participant,add_category

urlpatterns = [
    path('home/', home, name='home'),
    path("dashboard/", dashboard, name="dashboard"),
    path('create_event/',create_event, name='create_event'),
    path('update_event/<int:id>/', update_event, name='update_event'),
    path('delete_event/<int:id>/', delete_event, name='delete_event'),
    path("event/<int:id>/", event_detail, name="event_detail"),
    path('add_participant/', add_participant, name='add_participant'),
    path('add_category/', add_category, name='add_category'),

    


]