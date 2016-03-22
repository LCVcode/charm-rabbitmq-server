# Copyright 2016 Canonical Limited.
#
# This file is part of charm-helpers.
#
# charm-helpers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3 as
# published by the Free Software Foundation.
#
# charm-helpers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with charm-helpers.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import subprocess


from charmhelpers.core.hookenv import (
    log,
    INFO,
)
from charmhelpers.contrib.hardening.audits.file import (
    FilePermissionAudit,
    DirectoryPermissionAudit,
    NoReadWriteForOther,
    TemplatedFile,
)
from charmhelpers.contrib.hardening.audits.apache import DisabledModuleAudit
from charmhelpers.contrib.hardening.apache import TEMPLATES_DIR
from charmhelpers.contrib.hardening import utils


def get_audits():
    """Get Apache hardening config audits.

    :returns:  dictionary of audits
    """
    if subprocess.call(['which', 'apache2'], stdout=subprocess.PIPE) != 0:
        log("Apache server does not appear to be installed on this node - "
            "skipping apache hardening", level=INFO)
        return []

    context = ApacheConfContext()
    settings = utils.get_settings('apache')
    audits = [
        FilePermissionAudit(paths='/etc/apache2/apache2.conf', user='root',
                            group='root', mode=0o0640),

        TemplatedFile(os.path.join(settings['common']['apache_dir'],
                                   'mods-available/alias.conf'),
                      context,
                      TEMPLATES_DIR,
                      mode=0o0755,
                      user='root',
                      service_actions=[{'service': 'apache2',
                                        'actions': ['restart']}]),

        TemplatedFile(os.path.join(settings['common']['apache_dir'],
                                   'conf-enabled/hardening.conf'),
                      context,
                      TEMPLATES_DIR,
                      mode=0o0640,
                      user='root',
                      service_actions=[{'service': 'apache2',
                                        'actions': ['restart']}]),

        DirectoryPermissionAudit(settings['common']['apache_dir'],
                                 user='root',
                                 group='root',
                                 mode=0o640),

        DisabledModuleAudit(settings['hardening']['modules_to_disable']),

        NoReadWriteForOther(settings['common']['apache_dir']),
    ]

    return audits


class ApacheConfContext(object):
    """Defines the set of key/value pairs to set in a apache config file.

    This context, when called, will return a dictionary containing the
    key/value pairs of setting to specify in the
    /etc/apache/conf-enabled/hardening.conf file.
    """
    def __call__(self):
        settings = utils.get_settings('apache')
        ctxt = settings['hardening']

        out = subprocess.check_output(['apache2', '-v'])
        ctxt['apache_version'] = re.search(r'.+version: Apache/(.+?)\s.+',
                                           out).group(1)
        ctxt['apache_icondir'] = '/usr/share/apache2/icons/'
        ctxt['traceenable'] = settings['hardening']['traceenable']
        return ctxt
