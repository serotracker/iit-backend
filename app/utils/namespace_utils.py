import importlib


def init_namespace(namespaces, api_app):
    for ns in namespaces:
        ns_obj = importlib.import_module('app.namespaces.{}'.format(ns))
        ns_controller = getattr(ns_obj, "{}_ns".format(ns))
        api_app.add_namespace(ns_controller)
    return api_app
