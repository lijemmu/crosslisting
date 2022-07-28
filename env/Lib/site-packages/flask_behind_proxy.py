

class FlaskBehindProxy:
    def __init__(self, app=None):
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.app.wsgi_app = ReverseProxied(self.app.wsgi_app)
        return self


# Borrow from https://github.com/wilbertom/flask-reverse-proxy
class ReverseProxied:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        return self.app(environ, start_response)
