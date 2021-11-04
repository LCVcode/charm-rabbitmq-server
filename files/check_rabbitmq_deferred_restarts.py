#!/usr/bin/python3
"""
Checks for RabbitMQ deferred service restarts.

This Nagios check will parse /var/lib/policy-rd.d/
to find any restarts that are currently deferred.
Will do nothing if config `enable-auto-restarts`
is True.
"""

import glob
import sys
import yaml


def get_service_name(file_name):
    """Read a deferred event file and return the deferred service name.

    :param file_name: Name of file to read.
    :type file_name: str
    :returns: Name of services with deferred restart.
    :rtype: str
    """
    with open(file_name, 'r') as f:
        service = yaml.safe_load(f)['service']
    return service


if __name__ == "__main__":

    deferred_restart_files = glob.glob("/var/lib/policy-rc.d/*.deferred")
    deferred_restarts = [get_service_name(f) for f in deferred_restart_files]

    if not len(deferred_restarts):
        print("OK: No deferred service restarts.")
        sys.exit(0)
    else:
        print(
            "CRITICAL: Restarts are deferred for services: {}.".format(
                ", ".join(deferred_restarts)
            )
        )
        sys.exit(2)
