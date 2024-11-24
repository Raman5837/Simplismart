from django.urls import path

import core.views as views

urlpatterns = [
    path("auth/", views.TokenAPIView.as_view(), name="auth"),
    path("clusters/", views.ClusterAPIView.as_view(), name="clusters"),
    path("deployments/", views.DeploymentAPIView.as_view(), name="deployments"),
    path("memberships/", views.MembershipAPIView.as_view(), name="memberships"),
    path("organizations/", views.OrganizationAPIView.as_view(), name="organizations"),
    path("allocations/", views.ResourceAllocationAPIView.as_view(), name="allocations"),
]
