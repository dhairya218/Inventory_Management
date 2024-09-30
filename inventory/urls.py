from django.urls import path
from .views import (Index,Chart,daily_additions
,DownloadPDFView,AddCompanyAndGeneratePDFView,CustomPasswordResetView ,DeactivateProductView,ActivateProductView,ToggleProductStatusView, UnitView,  TodayTransactionsView, DashboardView,ProductListBulkDeleteView, LoginView, Add_User, LogoutView, SettingsView, EditHistoryQuantityView, ChangePasswordView, ProductListView, ProfileView, AddProductView, RecentBuyView, RecentSellView, ProductStockView, ProductHistoryView,    EditQuantityView, ReturnQuantityView)
# ProductHistoryEditView,DailyAdditionsView,UnitView,UnitCreateView,YourView
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('history/', ProductHistoryView.as_view(), name='product-history'),
    path('products/add/', AddProductView.as_view(), name='add-product'),
    # path('product-history/edit/<int:id>/', ProductHistoryEditView.as_view(), name='product-history-edit'),
    path('Add-User/', Add_User.as_view(), name='Add-User'),
    path('stock/', ProductStockView.as_view(), name='product-stock'),
    path('edit-quantity/', EditQuantityView.as_view(), name='edit-quantity'),
    path('return-quantity/', ReturnQuantityView.as_view(), name='return-quantity'),
    path('recent-buy/', RecentBuyView.as_view(), name='recent-buy'),
    path('recent-sell/', RecentSellView.as_view(), name='recent-sell'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('stock/add/', ProductStockView.as_view(), name='add-stock'), 
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('change_password/', ChangePasswordView.as_view(), name='change_password'),
    path('edit-history-quantity/', EditHistoryQuantityView.as_view(), name='edit-history-quantity'),
    path('chart/', Chart.as_view(), name='chart'),
    path('daily-additions/', views.daily_additions, name='product_daily_addition'),
    path('today-transactions/', TodayTransactionsView.as_view(), name='today-transactions'),
    path('products/bulk-delete/', ProductListBulkDeleteView.as_view(), name='product-list-bulk-delete'),
    path('units/', UnitView.as_view(), name='units'),  # URL for listing and creating units
    # path('units/create/', UnitCreateView.as_view(), name='unit-create'),
    path('product/activate/<int:product_id>/', ActivateProductView.as_view(), name='activate-product'),
    path('deactivate-product/<int:product_id>/', DeactivateProductView.as_view(), name='deactivate-product'),
    path('product/toggle-status/<int:product_id>/', ToggleProductStatusView.as_view(), name='toggle-product-status'),
    path('download-pdf/', DownloadPDFView.as_view(), name='download-pdf'),
    path('add_company_and_pdf/', AddCompanyAndGeneratePDFView.as_view(), name='add_company_and_pdf'),
    # path('save-columns/', YourView.as_view(), name='save_columns')
    # path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    # path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    # path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
        path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetView.as_view(), name='password_reset_confirm'),

    # Keep these views for password reset done and complete
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]
