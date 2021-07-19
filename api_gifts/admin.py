from django.contrib import admin
from . models import Gifts

# Register your models here.


class GiftsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cost', 'bonus',
                    'status', 'available', 'days_to_accept')
    list_display_links = ('id', 'name', 'status')
    list_filter = ('status', 'available')
    search_fields = ('name', 'status')
    list_editable = ('available',)


admin.site.register(Gifts, GiftsAdmin)
