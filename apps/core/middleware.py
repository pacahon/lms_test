from django.conf import settings
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import redirect

from core.exceptions import Redirect
from core.utils import is_club_site
from .context_processors import cities


class CurrentCityMiddleware(object):
    """
    Attach city code to request object:
        * On compsciclub.ru always resolve city from sub domain
        * If view contains `city_aware` keyword argument, get city code from
          URL parameters
        * If not, try to cast sub domain to city code.
        * Otherwise, fallback to `settings.DEFAULT_CITY_CODE`. It makes
          sense in case of `www` or empty sub domain.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        url_aware_of_the_city = bool(view_kwargs.get("city_aware", False))
        if url_aware_of_the_city and not is_club_site():
            # No need in delimiter if we always explicitly set city code
            use_delimiter = view_kwargs.get("use_delimiter", True)
            delimiter = view_kwargs.get("city_delimiter", None)
            city_code = view_kwargs["city_code"]
            if not city_code:
                if use_delimiter and delimiter:
                    # For default city delimiter must be empty
                    raise Http404
                city_code = settings.DEFAULT_CITY_CODE
            elif city_code not in settings.TIME_ZONES or (use_delimiter and
                                                          not delimiter):
                # None-empty delimiter if valid city code provided
                raise Http404
        else:
            if url_aware_of_the_city:
                # FIXME: Подразумевается, что никогда не используем в url?
                if view_kwargs["city_code"] or view_kwargs["city_delimiter"]:
                    raise Http404
            # Assume we have only 1 lvl sub domains
            sub_domain = request.get_host().rsplit('.', 2)[:-2]
            if sub_domain:
                current = sub_domain[0].lower()
            else:
                current = None
            for city in cities(request)['CITY_LIST']:
                if city.code == current:
                    city_code = current
                    break
            else:
                city_code = settings.DEFAULT_CITY_CODE
        request.city_code = city_code
        return None


class RedirectMiddleware(object):
    """
    You must add this middleware to MIDDLEWARE list,
    to make work Redirect exception. All arguments passed to
    Redirect will be passed to django built in redirect function.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if not isinstance(exception, Redirect):
            return
        redirect_to = exception.kwargs.pop("to")
        if isinstance(redirect_to, HttpResponseRedirect):
            redirect_to = redirect_to.url
        return redirect(redirect_to, **exception.kwargs)