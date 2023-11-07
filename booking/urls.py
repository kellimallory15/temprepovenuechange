from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='booking'),
    path('booking', views.booking, name='booking'),
    path('booking-submit', views.bookingSubmit, name='bookingSubmit'),
    path('user-panel', views.userPanel, name='userPanel'),
    path('user-update/<int:id>', views.userUpdate, name='userUpdate'),
    path('user-update-submit/<int:id>', views.userUpdateSubmit, name='userUpdateSubmit'),
    path('staff-panel', views.staffPanel, name='staffPanel'),
    path('<int:year>/<str:month>/', views.home, name="home"),
    path('bookings', views.all_events, name="list-events"),
    path('members/', include('members.urls'), name='members'),
]
