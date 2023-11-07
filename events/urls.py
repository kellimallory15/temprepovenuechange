from django.urls import path
from . import views

urlpatterns = [
    # Path Converters
    # int: numbers
    # str: strings
    # path: whole urls /
    # slug: hyphen-and_underscores_stuff
    # UUID: universally unique identifier

    path('', views.home, name="home"),
    path('<int:year>/<str:month>/', views.home, name="home"),
    path('bookings', views.all_events, name="list-events"),
    path('add_package', views.add_package, name='add-package'),
    path('list_packages', views.list_packages, name='list-packages'),
    path('show_package/<package_id>', views.show_package, name='show-package'),
    path('search_packages', views.search_packages, name='search-packages'),
    path('update_package/<package_id>', views.update_package, name='update-package'),
    path('update_booking/<event_id>', views.update_event, name='update-event'),
    path('add_booking', views.add_event, name='add-event'),
    path('delete_booking/<event_id>', views.delete_event, name='delete-event'),
    path('delete_package/<package_id>', views.delete_package, name='delete-package'),
    path('package_text', views.package_text, name='package_text'),
    path('package_csv', views.package_csv, name='package_csv'),
    path('package_pdf', views.package_pdf, name='package_pdf'),
    path('my_bookings', views.my_events, name='my_events'),
    path('search_bookings', views.search_events, name='search_events'),
    path('admin_approval', views.admin_approval, name='admin_approval'),
    path('package_bookings/<package_id>', views.package_events, name='package-events'),
    path('show_booking/<event_id>', views.show_event, name='show-event'),
]
