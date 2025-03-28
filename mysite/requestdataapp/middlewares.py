from django.http import HttpRequest


def set_useragent_on_request_middleware(get_response):

    print("initial call")

    def middleware(request: HttpRequest):
        print("before get response")
        if 'HTTP_USER_AGENT' in request.META:
            request.user_agent = request.META["HTTP_USER_AGENT"]

        response = get_response(request)
        print("after get response")
        return response

    return middleware


