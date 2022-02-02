from django.contrib import admin
from .models import VoteModel, CandidateModel, VoiceUser, HashVoiceUser
# Register your models here.


class CandidateAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


class VoteEditAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    fields = ("title", "description", "date")


class VoiceUserAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


class HashVoiceUserAdmin(admin.ModelAdmin):
    list_display = ('__str__',)


admin.site.register(VoteModel, VoteEditAdmin)
admin.site.register(CandidateModel, CandidateAdmin)
admin.site.register(VoiceUser, VoiceUserAdmin)
admin.site.register(HashVoiceUser, HashVoiceUserAdmin)
