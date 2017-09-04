"""
Django models for the dot-dynamic-scopes package.
"""

import logging

from django.db import models
from django.conf import settings

import requests

from oauth2_provider import settings as dot_settings


log = logging.getLogger("dot_dynamic_scopes")


class Scope(models.Model):
    """
    Django model for an OAuth scope.
    """
    #: The application that created the scope
    # NOTE: This is not used to limit access to the scope in any way - we want the
    #       scope to be available to other applications in order to request access
    #       to the resource it protects!
    application = models.ForeignKey(
        # This field is nullable because it is only set for scopes created by
        # external resource servers, which have a corresponding OAuth application
        # record on the authorisation server
        blank = True, null = True,
        dot_settings.APPLICATION_MODEL,
        models.CASCADE,
        help_text = 'The application to which the scope belongs.'
    )
    #: The name of the scope
    name = models.CharField(
        max_length = 255,
        unique = True,
        help_text = 'The name of the scope.'
    )
    #: A brief description of the scope
    description = models.TextField(
        help_text = 'A brief description of the scope. This text is displayed '
                    'to users when authorising access for the scope.'
    )
    is_default = models.BooleanField(
        default = False,
        help_text = 'Indicates if this scope should be included in the default scopes.'
    )

    @classmethod
    def register(cls, name, description, is_default = False):
        """
        Registers a scope with the given values. It always creates an instance in
        the local database, but if this resource server has an external authorisation
        server, it will also register the scope there.

        Returns ``True`` on success. Should raise on failure.
        """
        endpoint = getattr(settings, 'DOT_DYNAMIC_SCOPES', {}).get(
            'RESOURCE_SERVER_REGISTER_SCOPE_URL',
            None
        )
        if endpoint:
            # If the endpoint is set, make the callout to the authz server
            token = "Bearer {}".format(dot_settings.RESOURCE_SERVER_AUTH_TOKEN)
            # Let any failures bubble up
            # The idea is to call this method during deployment as a post-migrate
            # hook, so we want failures to halt the deployment
            response = requests.post(
                endpoint,
                json = {
                    'name': name,
                    'description': description,
                    'is_default': is_default
                },
                headers = { "Authorization": token }
            )
            # Raise the exception for anything other than 20x responses
            response.raise_for_status()
        # Always create/update the scope record locally
        _ = Scope.objects.update_or_create(
            name = name,
            defaults = { 'description': description, 'is_default': is_default }
        )
        return True