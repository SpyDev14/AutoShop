from django.contrib import admin
from admin_registrar import AdminRegistrar
from rangefilter.filters import DateRangeFilter

from src.apps.feedback import models, apps
from src.shared.admin.export import make_export_to_excel_action


registrar = AdminRegistrar(apps.FeedbackConfig)

@registrar.set_for_model()
class FeedbackRequestAdmin(admin.ModelAdmin):
    actions = [make_export_to_excel_action("Заявки", add_date_to_name = True)]
    list_display = ('request_from', 'phone_number', 'created_at')
    list_filter = (
        ('created_at', DateRangeFilter),
    )
    sortable_by = ('created_at', )
    ordering = ('-created_at', )
    readonly_fields = ('served_at', 'served_by', 'is_served', 'created_at')

    def request_from(self, obj: models.FeedbackRequest) -> str:
        return obj.requestener_name
    request_from.short_description = 'Заявка от' # type: ignore[reportFunctionMemberAccess]

registrar.register()
