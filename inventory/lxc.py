#!/usr/bin/env python
#
# (c) 2015, Florian Haas, hastexo Professional Services GmbH
# <florian@hastexo.com>
# Based in part on:
# libvirt_lxc.py, (c) 2013, Michael Scherer <misc@zarb.org>
#
# This file is part of Ansible,
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
"""
Ansible inventory script for LXC containers. Requires Python
bindings for LXC API.

In LXC, containers can be grouped by setting the lxc.group option,
which may be found more than once in a container's
configuration. So, we enumerate all containers, fetch their list
of groups, and then build the dictionary in the way Ansible expects
it.
"""

from __future__ import print_function

# Horrible hack: we want this script to be called lxc.py, yet need to
# import a module named lxc. Absolute import (from __future__ import
# absolute_import) does not work here, because this is a script, not a
# package. The only way to tell Python that "import lxc" does *not*
# mean "import yourself" is to pop the first entry off of sys.path.
#
# Since inventory scripts are always invoked directly, and never
# imported, we should be able to get away with this.
import sys
sys.path.pop(0)
import lxc as _lxc

import json


def build_dict():
    """Returns a dictionary keyed to the defined LXC groups. All
    containers, including the ones not in any group, are included in the
    "all" group."""
    # Enumerate all containers, and list the groups they are in. Also,
    # implicitly add every container to the 'all' group.
    containers = dict([((_lxc.Container(c).get_ips()[0]),
                        ['all'] +
                        (_lxc.Container(c).get_config_item('lxc.group') or []))
                       for c in _lxc.list_containers()])

    # Extract the groups, flatten the list, and remove duplicates
    groups = set(sum([g for g in containers.values()], []))

    # Create a dictionary for each group (including the 'all' group
    return dict([(g, {'hosts': [k for k, v in containers.items() if g in v],
                      'vars': {'ansible_connection':'ssh'}}) for g in groups])

def main(argv):
    """Returns a JSON dictionary as expected by Ansible"""
    result = build_dict()
    if len(argv) == 2 and argv[1] == '--list':
        json.dump(result, sys.stdout)
    elif len(argv) == 3 and argv[1] == '--host':
        json.dump({'ansible_connection': 'ssh'}, sys.stdout)
    else:
        print("Need an argument, either --list or --host <host>", file=sys.stderr)

if __name__ == '__main__':
    main(sys.argv)


