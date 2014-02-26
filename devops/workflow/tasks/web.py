"""
The web module offers classes that deal with traversing and getting data from the web.

The HttpDataRetrieval class makes use of the requests module (http://requests.readthedocs.org/en/latest/) to do a GET on static data from some web address.
"""

from ..workflow import DevOpsTask
import requests


class HttpDataRetrieval(DevOpsTask):

    """
    The HttpDataRetrieval class makes use of the requests module (http://requests.readthedocs.org/en/latest/) to do a GET on static data from some web address.
    """

    def __init__(self, url, destination):

        """
        self.url => The url to GET data from.
        self.destination = The target save location on the local machine.
        """

        super().__init__()
        self.url = url
        self.destination = destination

    def execute(self, step_name=''):

        """
        Uses requests to GET data from self.url.
        """

        super().execute(step_name)
        self._w_print('Attempting to retrieve data from {}'.format(self.url))
        r = requests.get(self.url)
        self._w_print('Saving data to: {}'.format(self.destination))
        with open(self.destination, 'wb') as dest:
            dest.write(r.content)