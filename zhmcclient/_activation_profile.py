# Copyright 2016 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
**Activation Profiles** control the activation of CPCs and LPARs. They are used
to tailor the operation of a CPC and are stored in the Support Element
associated with the CPC.

Activation Profile resources are contained in CPC resources.

Activation Profile resources only exist in CPCs that are not in DPM mode.

TODO: If Reset Activation Profiles are used to determine the CPC mode,
      should they not exist in all CPC modes?

There are three types of Activation Profiles:

1. Reset:
   The Reset Activation Profile defines for a CPC the mode in which the CPC
   licensed internal code will be loaded (e.g. DPM mode or classic mode) and
   how much central storage and expanded storage will be used.

2. Image:
   For CPCs in classic mode, each LPAR can have an Image Activation Profile.
   The Image Activation Profile determines the number of CPs that the LPAR will
   use and whether these CPs will be dedicated to the LPAR or shared. It also
   allows assigning the amount of central storage and expanded storage that
   will be used by each LPAR.

3. Load:
   For CPCs in classic mode, each LPAR can have a Load Activation Profile.
   The Load Activation Profile defines the channel address of the device that
   the operating system for that LPAR will be loaded (booted) from.
"""

from __future__ import absolute_import

from ._manager import BaseManager
from ._resource import BaseResource
from ._logging import _log_call


__all__ = ['ActivationProfileManager', 'ActivationProfile']


class ActivationProfileManager(BaseManager):
    """
    Manager providing access to the Activation Profiles of a particular type in
    a particular CPC.

    Derived from :class:`~zhmcclient.BaseManager`; see there for common methods
    and attributes.
    """

    def __init__(self, cpc, profile_type):
        """
        Parameters:

          cpc (:class:`~zhmcclient.Cpc`):
            CPC defining the scope for this manager.

          profile_type (string):
            Type of Activation Profiles:

            * `reset`: Reset Activation Profiles
            * `image`: Image Activation Profiles
            * `load`: Load Activation Profiles
        """
        super(ActivationProfileManager, self).__init__(cpc)
        self._profile_type = profile_type

    @property
    def cpc(self):
        """
        :class:`~zhmcclient.Cpc`: CPC defining the scope for this manager.
        """
        return self._parent

    @property
    def profile_type(self):
        """
        Return the type of the Activation Profiles managed by this object:

        * `reset`: Reset Activation Profiles
        * `image`: Image Activation Profiles
        * `load`: Load Activation Profiles
        """
        return self._profile_type

    @_log_call
    def list(self, full_properties=False):
        """
        List the Activation Profiles of the type managed by this object and in
        this CPC.

        Parameters:

          full_properties (bool):
            Controls whether the full set of resource properties should be
            retrieved, vs. only the short set as returned by the list
            operation.

        Returns:

          : A list of :class:`~zhmcclient.ActivationProfile` objects.

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        cpc_uri = self.cpc.get_property('object-uri')
        activation_profile = self._profile_type + '-activation-profiles'
        profiles_res = self.session.get(cpc_uri + '/' + activation_profile)
        profile_list = []
        if profiles_res:
            profile_items = profiles_res[self._profile_type +
                                         '-activation-profiles']
            for profile_props in profile_items:
                profile = ActivationProfile(self, profile_props['element-uri'],
                                            profile_props)
                if full_properties:
                    profile.pull_full_properties()
                profile_list.append(profile)
        return profile_list


class ActivationProfile(BaseResource):
    """
    Representation of an Activation Profile of a particular type.

    Derived from :class:`~zhmcclient.BaseResource`; see there for common
    methods and attributes.
    """

    def __init__(self, manager, uri, properties):
        """
        Parameters:

          manager (:class:`~zhmcclient.ActivationProfileManager`):
            Manager for this Activation Profile.

          uri (string):
            Canonical URI path of this Activation Profile.

          properties (dict):
            Properties to be set for this Activation Profile.
            See initialization of :class:`~zhmcclient.BaseResource` for
            details.
        """
        assert isinstance(manager, ActivationProfileManager)
        super(ActivationProfile, self).__init__(manager, uri, properties)

    def update_properties(self, properties):
        """
        Update writeable properties of this Activation Profile.

        Parameters:

          properties (dict): New values for the properties to be updated.
            Properties not to be updated are omitted.
            Allowable properties are the properties with qualifier (w) in
            section 'Data model' in section
            '<profile_type> activation profile' in the :term:`HMC API` book,
            where <profile_type> is the profile type of this object
            (e.g. Reset, Load, Image).

        Raises:

          :exc:`~zhmcclient.HTTPError`
          :exc:`~zhmcclient.ParseError`
          :exc:`~zhmcclient.AuthError`
          :exc:`~zhmcclient.ConnectionError`
        """
        profile_uri = self.get_property('element-uri')
        self.manager.session.post(profile_uri, body=properties)
