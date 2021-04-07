# dc_states.py

import logging

from Utils.ssh_util import SshUtil


logger = logging.getLogger('framework')

PYTEST_STATES_DIR = "/tmp/pytest_states"
DC_STATES = {
    'removed'     : 0,
    'uploaded'    : 1,
    'extracted'   : 2,
    'installed'   : 3,
    'joined'      : 4,
    'leaved'      : 5,
    'uninstalled' : 6
}
DC_STATE_FILE = "dc_state"


###### DC states related functions ######

def set_dc_state(state, ssh):
    sudo = sudo_or_not(ssh)
    ssh.send_command(f"{sudo}mkdir -p {PYTEST_STATES_DIR} && {sudo}chmod 755 {PYTEST_STATES_DIR}")
    rc, result, error = ssh.send_command(f"echo {state} | {sudo}tee {PYTEST_STATES_DIR}/{DC_STATE_FILE} && "
                                         f"{sudo}chmod 644 {PYTEST_STATES_DIR}/{DC_STATE_FILE}")
    if rc != 0:
        raise Exception("Cannot set DC state")


def get_dc_state(ssh):
    rc, result, error = ssh.send_command(f"cat {PYTEST_STATES_DIR}/{DC_STATE_FILE}")
    if rc != 0:
        return 0
    state = int(ssh.cleanup(result))
    return state


def run_dc_state(state, mode, packages, command, func,
                 env, machine, bundle, ssh, run_next):
    if run_next:
        state += 1
        if state > DC_STATES['uninstalled']:
            state = DC_STATES['removed']
    logger.debug(f"Running state {state}")
    if state == DC_STATES['removed']: # removed state must be zero
        auto_remove_dc(bundle, ssh)
    elif state == DC_STATES['uploaded']:
        auto_upload_dc(machine, bundle, ssh)
    elif state == DC_STATES['extracted']:
        auto_extract_dc(bundle, ssh)
    elif state == DC_STATES['installed']:
        auto_install_dc(mode, packages, env, bundle, ssh)
    elif state == DC_STATES['joined']:
        auto_join_domain(command, func, env, bundle, ssh)
    elif state == DC_STATES['leaved']:
        auto_leave_domain(env, bundle, ssh)
    elif state == DC_STATES['uninstalled']:
        auto_uninstall_dc(bundle, ssh)
    return state


def sync_current_dc_state(bundle, ssh):
    record = get_dc_state(ssh)
    current = record
    if is_joined(bundle, ssh):
        current = DC_STATES['joined']
    elif is_installed(bundle, ssh):
        if current != DC_STATES['installed'] and current != DC_STATES['leaved']:
            current = DC_STATES['installed']
    elif is_extracted(bundle, ssh):
        if current != DC_STATES['extracted'] and current != DC_STATES['uninstalled']:
            current = DC_STATES['extracted']
    elif is_uploaded(bundle, ssh):
        current = DC_STATES['uploaded']
    else:
        current = DC_STATES['removed']
    if current != record:
        set_dc_state(current, ssh)
    logger.debug(f"Current state is {current}")
    return current


def go_dc_state(state, mode, packages, command, func,
                env, machine, bundle, ssh):
    current = sync_current_dc_state(bundle, ssh)
    # Rollback if anything changed
    if current >= DC_STATES['installed'] and \
      rollback_if_install_changed(mode, packages, env, bundle, ssh):
        current = DC_STATES['installed'] - 1
    elif current >= DC_STATES['joined'] and \
      rollback_if_join_changed(command, env, bundle, ssh):
        current = DC_STATES['joined'] - 1
    if current > state:
        logger.debug("Going back to state 0")
        # Go back to the state zero
        #
        # Short cut to avoid adjoin, move to joined state
        # and we can start tearing down to state zero
        if current < DC_STATES['joined']:
            current = DC_STATES['joined']
        while current != DC_STATES['removed']: # removed state must be zero
            # Short cut to avoid uninstalling package files and install again
            if current == DC_STATES['leaved'] and \
              state >= DC_STATES['installed']:
                current = DC_STATES['installed']
                set_dc_state(current, ssh)
                break
            # Short cut to avoid removing package files and upload again
            if current == DC_STATES['uninstalled'] and \
              state >= DC_STATES['extracted']:
                current = DC_STATES['extracted']
                set_dc_state(current, ssh)
                break
            current = run_dc_state(current, mode, packages, command, func,
                                   env, machine, bundle, ssh, True)
    while current < state:
        current = run_dc_state(current, mode, packages, command, func,
                               env, machine, bundle, ssh, True)


# Import here to avoid circular imports
from Shared.dc_functions import *
