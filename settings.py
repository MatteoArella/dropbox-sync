from yaml import load
import json
import os

class Settings:
    class NestedWrapper(object):
        def __init__(self, dictionary):
            def _traverse(key, element):
                if isinstance(element, dict):
                    return key, Settings.NestedWrapper(element)
                else:
                    return key, element

            objd = dict(_traverse(k, v) for k, v in dictionary.items())
            self.__dict__.update(objd)

    def __init__(self, **kwargs):
        default_settings_file = os.path.join(os.path.dirname(__file__), 'settings.yml')
        settings_file = kwargs.get('settings_file', default_settings_file)
        with open(settings_file) as file:
            self.settings = Settings.NestedWrapper(load(file))
            
    def __getattr__(self, attr):
        return getattr(self.settings, attr, None)

    def __dict__(self):
        return json.loads(json.dumps(self.settings, default=lambda o: o.__dict__))

    def __str__(self):
        return str(self.__dict__())

    def __repr__(self):
        return self.__str__()