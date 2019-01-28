'''
.. autoclass:: TenableIO

.. automodule:: tenable.io.agent_config
.. automodule:: tenable.io.agent_exclusions
.. automodule:: tenable.io.agent_groups
.. automodule:: tenable.io.agents
.. automodule:: tenable.io.assets
.. automodule:: tenable.io.audit_log
.. automodule:: tenable.io.editor
.. automodule:: tenable.io.exclusions
.. automodule:: tenable.io.exports
.. automodule:: tenable.io.files
.. automodule:: tenable.io.filters
.. automodule:: tenable.io.folders
.. automodule:: tenable.io.groups
.. automodule:: tenable.io.permissions
.. automodule:: tenable.io.plugins
.. automodule:: tenable.io.policies
.. automodule:: tenable.io.scanner_groups
.. automodule:: tenable.io.scanners
.. automodule:: tenable.io.scans
.. automodule:: tenable.io.server
.. automodule:: tenable.io.session
.. automodule:: tenable.io.target_groups
.. automodule:: tenable.io.users
.. automodule:: tenable.io.workbenches

Raw HTTP Calls
==============

Even though the ``TenableIO`` object pythonizes the Tenable.io API for you,
there may still bee the occasional need to make raw HTTP calls to the IO API.
The methods listed below aren't run through any naturalization by the library
aside from the response code checking.  These methods effectively route
directly into the requests session.  The responses will be Response objects from
the ``requests`` library.  In all cases, the path is appended to the base 
``url`` paramater that the ``TenableIO`` object was instantiated with.

Example:

.. code-block:: python

   resp = tio.get('scans')

.. py:module:: tenable.io
.. rst-class:: hide-signature
.. py:class:: TenableIO

    .. automethod:: get
    .. automethod:: post
    .. automethod:: put
    .. automethod:: delete
'''
import logging
from tenable.base import APISession
from .agent_config import AgentConfigAPI
from .agent_exclusions import AgentExclusionsAPI
from .agent_groups import AgentGroupsAPI
from .agents import AgentsAPI
from .assets import AssetsAPI
from .audit_log import AuditLogAPI
from .editor import EditorAPI
from .exclusions import ExclusionsAPI
from .exports import ExportsAPI
from .files import FileAPI
from .filters import FiltersAPI
from .folders import FoldersAPI
from .groups import GroupsAPI
from .permissions import PermissionsAPI
from .plugins import PluginsAPI
from .policies import PoliciesAPI
from .scanner_groups import ScannerGroupsAPI
from .scanners import ScannersAPI
from .scans import ScansAPI
from .server import ServerAPI
from .session import SessionAPI
from .tags import TagsAPI
from .target_groups import TargetGroupsAPI
from .users import UsersAPI
from .workbenches import WorkbenchesAPI


class TenableIO(APISession):
    '''
    The Tenable.io object is the primary interaction point for users to
    interface with Tenable.io via the pyTenable library.  All of the API
    endpoint classes that have been written will be grafted onto this class.

    Args:
        access_key (str):
            The user's API access key for Tenable.io
        secret_key (str):
            The user's API secret key for Tenable.io
        url (str, optional):
            The base URL that the paths will be appended onto.  The default
            is ``https://cloud.tenable.com`` 
        retries (int, optional):
            The number of retries to make before failing a request.  The
            default is ``3``.
        backoff (float, optional):
            If a 429 response is returned, how much do we want to backoff
            if the response didn't send a Retry-After header.  The default
            backoff is ``1`` second.
        ua_identity (str, optional):
            An application identifier to be added into the User-Agent string
            for the purposes of application identification.

    Examples:
        >>> from tenable.io import TenableIO
        >>> tio = TenableIO('ACCESS_KEY', 'SECRET_KEY')
    '''
    
    _tzcache = None
    _url = 'https://cloud.tenable.com'

    @property
    def agent_config(self):
        return AgentConfigAPI(self)

    @property
    def agent_groups(self):
        return AgentGroupsAPI(self)

    @property
    def agent_exclusions(self):
        return AgentExclusionsAPI(self)

    @property
    def agents(self):
        return AgentsAPI(self)

    @property
    def assets(self):
        return AssetsAPI(self)

    @property
    def audit_log(self):
        return AuditLogAPI(self)

    @property
    def editor(self):
        return EditorAPI(self)

    @property
    def exclusions(self):
        return ExclusionsAPI(self)

    @property
    def exports(self):
        return ExportsAPI(self)

    @property
    def files(self):
        return FileAPI(self)

    @property
    def filters(self):
        return FiltersAPI(self)

    @property
    def folders(self):
        return FoldersAPI(self)

    @property
    def groups(self):
        return GroupsAPI(self)

    @property
    def permissions(self):
        return PermissionsAPI(self)

    @property
    def plugins(self):
        return PluginsAPI(self)

    @property
    def policies(self):
        return PoliciesAPI(self)

    @property
    def scanner_groups(self):
        return ScannerGroupsAPI(self)

    @property
    def scanners(self):
        return ScannersAPI(self)

    @property
    def scans(self):
        return ScansAPI(self)

    @property
    def server(self):
        return ServerAPI(self)

    @property
    def session(self):
        return SessionAPI(self)
    
    @property
    def tags(self):
        return TagsAPI(self)

    @property
    def target_groups(self):
        return TargetGroupsAPI(self)

    @property
    def users(self):
        return UsersAPI(self)

    @property
    def workbenches(self):
        return WorkbenchesAPI(self)

    @property
    def _tz(self):
        '''
        As we will be using the timezone listing in a lot of parameter checking,
        we should probably cache the response as a private attribute to speed 
        up checking times.
        '''
        if not self._tzcache:
            self._tzcache = self.scans.timezones()
        return self._tzcache

    def __init__(self, access_key, secret_key, url=None, retries=None, 
                 backoff=None, ua_identity=None, session=None):
        self._access_key = access_key
        self._secret_key = secret_key
        APISession.__init__(self, url, retries, backoff, ua_identity, session)

    def _retry_request(self, response, retries, kwargs):
        '''
        If the call is retried, we will need to set some additional headers
        '''
        if 'headers' not in kwargs:
            kwargs['headers'] = dict()

        if 'X-Request-Uuid' in response.headers:
            # if the request uuid exists in the response, then we will sent the
            # uuid back so that there is solid requesty chain in any subsiquent
            # logs.
            kwargs['headers']['X-Tio-Last-Request-Uuid'] = response.headers['X-Request-Uuid']

        # We also need to return the number of times that we have attempted to
        # retry this call.
        kwargs['headers']['X-Tio-Retry-Count'] = str(retries)
        return kwargs


    def _build_session(self):
        '''
        Build the session and add the API Keys into the session
        '''
        APISession._build_session(self)
        self._session.headers.update({
            'X-APIKeys': 'accessKey={}; secretKey={};'.format(
                self._access_key, self._secret_key)
        })
