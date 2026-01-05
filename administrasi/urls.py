from django.urls import path
from . import views

app_name = 'administrasi'

urlpatterns = [
    # Pages
    path('customers/', views.customer_list, name='customer_list'),
    path('correspondence/', views.correspondence_list, name='correspondence_list'),
    path('correspondence/cetak-docx/<int:pk>/', views.print_docx, name='print_docx'),
    path('document-types/', views.document_type_list, name='document_type_list'),
    path('invoices/', views.invoice_list_page, name='invoice_list'),
    path('invoice/print/<int:pk>/', views.print_invoice, name='print_invoice'),
    path('finance/', views.finance_dashboard, name='finance_dashboard'),

    # API CRUD (AJAX)
    path('api/customers/upsert/', views.api_customer_upsert, name='api_customer_upsert'),
    path('api/customers/data/', views.api_customer_data, name='api_customer_data'),
    
    path('api/docs/upsert/', views.api_correspondence_upsert, name='api_docs_upsert'),
    path('api/docs/data/', views.api_correspondence_data, name='api_docs_data'),
    
    path('api/types/upsert/', views.api_document_type_upsert, name='api_type_upsert'),
    path('api/types/data/', views.api_document_type_data, name='api_type_data'),
    
    path('api/expenses/upsert/', views.api_expense_upsert, name='api_expense_upsert'),
    path('api/expenses/data/', views.api_expense_data, name='api_expense_data'),
    
    path('api/invoices/upsert/', views.api_invoice_upsert, name='api_invoice_upsert'),
    path('api/invoices/data/', views.api_invoice_data, name='api_invoice_data'),
    path('api/finance/summary/', views.api_finance_summary, name='api_finance_summary'),

    # Generic Delete
    path('api/delete/<str:model_name>/<int:pk>/', views.api_generic_delete, name='api_delete'),
]