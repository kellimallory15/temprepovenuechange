from django.contrib import admin
from .models import Package
from .models import MyClubUser
from .models import Event
from django.contrib.auth.models import Group

# admin.site.register(Package, PackageAdmin)
admin.site.register(MyClubUser)

# Remove Groups
admin.site.unregister(Group)


# admin.site.register(Event)

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    ordering = ('name',)
    search_fields = ('name', 'address')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (('name', 'package'), 'event_date', 'description', 'manager', 'approved')
    list_display = ('name', 'event_date', 'package')
    list_filter = ('event_date', 'package')
    ordering = ('event_date',)
