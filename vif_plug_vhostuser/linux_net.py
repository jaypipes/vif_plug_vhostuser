#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Implements vlans, bridges, and iptables rules using linux utilities."""


from oslo_log import log as logging

from vif_plug_vhostuser.i18n import _LE
from vif_plug_vhostuser import processutils

LOG = logging.getLogger(__name__)


def _ovs_vsctl(args, timeout=30):
    full_args = ['ovs-vsctl', '--timeout=%s' % timeout] + args
    try:
        return processutils.execute(*full_args, run_as_root=True)
    except Exception as e:
        LOG.error(_LE("Unable to execute %(cmd)s. Exception: %(exception)s"),
                  {'cmd': full_args, 'exception': e})
        raise e.AgentError(method=full_args)


def create_ovs_vif_port(bridge, dev, iface_id, mac, instance_id,
                        timeout=30, type=None):
    cmd = ['--', '--if-exists', 'del-port', dev, '--',
           'add-port', bridge, dev,
           '--', 'set', 'Interface', dev,
           'external-ids:iface-id=%s' % iface_id,
           'external-ids:iface-status=active',
           'external-ids:attached-mac=%s' % mac,
           'external-ids:vm-uuid=%s' % instance_id]
    if type:
        cmd += ['type=%s' % type]

    _ovs_vsctl(cmd, timeout=timeout)


def delete_ovs_vif_port(bridge, dev, timeout=30):
    _ovs_vsctl(['--', '--if-exists', 'del-port', bridge, dev],
               timeout=timeout)
