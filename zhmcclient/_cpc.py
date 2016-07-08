#!/usr/bin/env python

"""
A **Central Processor Complex (CPC)** is a physical z Systems computer.
A particular HMC can manage multiple CPCs.

The HMC can manage a range of old and new CPC generations. Some older CPC
generations are not capable of supporting the HMC Web Services API; these older
CPCs can be managed using the GUI of the HMC, but not through its Web Services
API. Therefore, such older CPCs will not show up at the HMC Web Services API,
and thus will not show up in the API of this Python package.

TODO: List earliest CPC generation that supports the HMC Web Services API.
"""

from __future__ import absolute_import

from ._manager import BaseManager
from ._resource import BaseResource
from ._lpar import LparManager

__all__ = ['CpcManager', 'Cpc']

class CpcManager(BaseManager):
    """
    Manager object for CPCs. This manager object is scoped to the HMC Web
    Services API capable CPCs managed by the HMC that is associated with a
    particular client.

    Derived from :class:`~zhmcclient.BaseManager`; see there for common methods.
    """

    def __init__(self, client):
        """
        Parameters:

          client (:class:`~zhmcclient.Client`):
            Client object for the HMC to be used.
        """
        super(CpcManager, self).__init__()
        self._session = client.session

    def list(self):
        """
        List the CPCs in scope of this manager object.

        Returns:

          : A list of :class:`~zhmcclient.Cpc` objects.
        """
        cpcs_res = self.session.get('/api/cpcs')
        cpc_list = []
        if cpcs_res:
            cpc_items = cpcs_res['cpcs']
            for cpc_attrs in cpc_items:
                cpc_list.append(Cpc(self, cpc_attrs))
        return cpc_list


class Cpc(BaseResource):
    """
    Representation of a CPC.
    """

    def __init__(self, manager, attrs):
        """
        Parameters:

          manager (:class:`~zhmcclient.CpcManager`):
            Manager object for this CPC.

          attrs (dict):
            Attributes to be attached to this object.
        """
        assert isinstance(manager, CpcManager)
        super(Cpc, self).__init__(manager, attrs)
        self._lpars = LparManager(self)

    @property
    def lpars(self):
        """
        :class:`~zhmcclient.LparManager`: Manager object for the LPARs in this
        CPC.
        """
        return self._lpars

