from django.conf.urls import url
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import list_route
from rest_framework.response import Response
from .permissions import UserPermission
from .serializers import UserCreateSerializer, UserLoginSerializer, UserSerializer
from .models import User
from rest_framework.authtoken.models import Token
from .tasks import get_covid_data, send_data_email


class UserViewSet(viewsets.ModelViewSet):
    """
    User related operations
    """
    queryset = User.objects.filter(is_active=True)
    permission_classes = (UserPermission,)
    filter_backends = (DjangoFilterBackend,)
    authentication_classes = (TokenAuthentication,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'login':
            return UserLoginSerializer      
        return UserSerializer

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.queryset.filter(id=self.request.user.id)
        return self.queryset    
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = serializer.data
            token, created = Token.objects.get_or_create(user_id=data.get('id'))
            data['token'] = token.key
            return Response(data, status=201)   


    @list_route(methods=['post'])
    def login(self, request):
        """
        API for Login as Client
        * __REQUEST BODY__
            ```
            {
                "email" : <string> (required),
                "password": <string> (required)
            }

            ```
        * __EXAMPLE__
            ```
            {
                "email" : "admin@admin.com",
                "password": "Admin@123"
            }

            ```
        """
        email = request.data.get('email')
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
            user = User.objects.get(email = email)
            token,created = Token.objects.get_or_create(user=user)
            data['id'] = user.id
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            data['country_code'] = user.country_code.code
            data['token'] =  token.key
            return Response(data,status=201)  

    
    @list_route(methods=['get'])
    def logout(self, request):
        """
        API for Logout
        * __ADDITIONAL INFORMATION__
            ```
            Logout based on the token in the header for logged in user.
            ```
        """
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Successfully Logged out'},
                        status=status.HTTP_200_OK)


    @list_route(methods=['get'])
    def getCovidData(self, request):
        """
        API for getting covid data
        * __OPTIONAL REQUEST QYERY PARAMS__
            ```
            ?country_code=<string>?date_range=<int>
            ```
        * __EXAMPLE__
            ```
            ?country_code=IN?date_range=15
            ```
        """
        country_code = request.GET.get('country_code')
        date_range = request.GET.get('date_range')
        
        data = get_covid_data(request.user, country_code, date_range)
        return Response(data, status=200)


    @list_route(methods=['get'])
    def emailCovidData(self, request):
        """
        API to email chart represented covid data
        * __OPTIONAL REQUEST QYERY PARAMS__
            ```
            ?country_code=<string>?date_range=<int>
            ```
        * __EXAMPLE__
            ```
            ?country_code=IN?date_range=15
            ```
        """
        country_code = request.GET.get('country_code')
        date_range = request.GET.get('date_range')
        data = get_covid_data(request.user, country_code, date_range)
        send_data_email.delay(data, request.user.email)
        return Response({'message': 'Email sent.'}, status=status.HTTP_200_OK)