from drf_yasg import openapi


error_schema = openapi.Schema(type=openapi.TYPE_OBJECT,
                              properties={
                                  'detail': openapi.Schema(type=openapi.TYPE_STRING, description='error message')
                              })
url_schema = openapi.Schema(type=openapi.TYPE_OBJECT,
                            properties={'url': openapi.Schema(type=openapi.TYPE_STRING, description='url to redirect')}
                            )
