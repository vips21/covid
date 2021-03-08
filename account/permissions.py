from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['logout', 'partial_update', 'update', 
                            'list','destroy', 'retrieve', 'getCovidData',
                            'emailCovidData']:
            return request.user.is_authenticated
        elif view.action in ['create', 'login']:
            return True   
        else:
            return False

    def has_object_permission(self, request, view, obj): 
        return True
