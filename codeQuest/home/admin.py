from django.contrib import admin

# Register your models here.
from home.models import question_details,user_question_details,user_code_sub,CodeSubmission

admin.site.register(question_details)
admin.site.register(user_question_details)
admin.site.register(user_code_sub)
admin.site.register(CodeSubmission)

