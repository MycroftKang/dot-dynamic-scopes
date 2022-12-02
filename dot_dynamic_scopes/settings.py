"""
Settings for the ``dot_dynamic_scopes`` app.
"""

from django.conf import settings

try:
    from django.core.exceptions import ImproperlyConfigured
except ImportError:
    class ImproperlyConfigured(RuntimeError):
        pass

class SettingsObject:
    """
    Object representing a collection of settings.
    Args:
        name: The name of the settings object.
        user_settings: A dictionary of user settings. OPTIONAL. If not given,
                       use ``django.conf.settings.<name>``.
    """
    def __init__(self, name, user_settings = None):
        self.name = name
        if user_settings is None:
            user_settings = getattr(settings, self.name, {})
        self.user_settings = user_settings

class Setting:
    """
    Property descriptor for a setting.
    Args:
        default: Provides a default for the setting. If a callable is given, it
                 is called with the owning py:class:`SettingsObject` as it's only
                 argument. Defaults to ``NO_DEFAULT``.
    """
    #: Sentinel object representing no default. A sentinel is required because
    #: ``None`` is a valid default value.
    NO_DEFAULT = object()

    def __init__(self, default = NO_DEFAULT):
        self.default = default

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        # Settings should be accessed as instance attributes
        if not instance:
            raise TypeError('Settings cannot be accessed as class attributes')
        try:
            return instance.user_settings[self.name]
        except KeyError:
            return self._get_default(instance)

    def _get_default(self, instance):
        # This is provided as a separate method for easier overriding
        if self.default is self.NO_DEFAULT:
            raise ImproperlyConfigured('Required setting: {}.{}'.format(instance.name, self.name))
        elif callable(self.default):
            try:
                return self.default(instance)
            except TypeError:
                return self.default()
        else:
            return self.default

    def __set__(self, instance, value):
        # This method exists so that the descriptor is considered a data-descriptor
        raise AttributeError('Settings are read-only')

class AppSettings(SettingsObject):
    RESOURCE_SERVER_REGISTER_SCOPE_URL = Setting(default = None)
    INTROSPECT_SCOPE = Setting()
    REGISTER_SCOPE_SCOPE = Setting()


app_settings = AppSettings('DOT_DYNAMIC_SCOPES')
