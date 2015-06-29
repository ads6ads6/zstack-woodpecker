import os
import subprocess
import time

import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.zstack_test.zstack_test_vm as zstack_vm_header

def create_vlan_vm(image_name, l3_name=None, disk_offering_uuids=None):
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    if not l3_name:
        l3_name = os.environ.get('l3VlanNetworkName1')

    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    return create_vm([l3_net_uuid], image_uuid, 'zs_install_%s' % image_name, \
            disk_offering_uuids)

def create_vm(l3_uuid_list, image_uuid, vm_name = None, \
        disk_offering_uuids = None, default_l3_uuid = None):
    vm_creation_option = test_util.VmOption()
    conditions = res_ops.gen_query_conditions('type', '=', 'UserVm')
    instance_offering_uuid = res_ops.query_resource(res_ops.INSTANCE_OFFERING, conditions)[0].uuid
    vm_creation_option.set_instance_offering_uuid(instance_offering_uuid)
    vm_creation_option.set_l3_uuids(l3_uuid_list)
    vm_creation_option.set_image_uuid(image_uuid)
    vm_creation_option.set_name(vm_name)
    vm_creation_option.set_data_disk_uuids(disk_offering_uuids)
    vm_creation_option.set_default_l3_uuid(default_l3_uuid)
    vm = zstack_vm_header.ZstackTestVm()
    vm.set_creation_option(vm_creation_option)
    vm.create()
    return vm

def check_str(string):
    if string == None:
        return ""
    return string

def execute_shell_in_process(cmd, tmp_file):
    logfd = open(tmp_file, 'w', 0)
    process = subprocess.Popen(cmd, executable='/bin/sh', shell=True, stdout=logfd, stderr=logfd, universal_newlines=True)

    timeout = 3600
    start_time = time.time()
    while process.poll() is None:
        curr_time = time.time()
        test_time = curr_time - start_time
        if test_time > timeout:
            process.terminate()
            logfd.close()
            logfd = open(tmp_file, 'r')
            test_util.test_logger('[shell:] %s [timeout logs:] %s' % (cmd, '\n'.join(logfd.readlines())))
            logfd.close()
            os.system('rm -f %s' % tmp_file)
            test_util.test_fail('[shell:] %s timeout, after %d seconds' % (cmd, timeout))
        print('Installation: %d' % int(test_time))
        time.sleep(1)
    logfd.close()
    logfd = open(tmp_file, 'r')
    test_util.test_logger('[shell:] %s [logs]: %s' % (cmd, '\n'.join(logfd.readlines())))
    logfd.close()
    return process.returncode

def prepare_test_env(vm_inv, aio_target):
    zstack_install_script = os.environ['zstackInstallScript']
    target_file = '/root/zstack_installer.sh'
    test_lib.lib_scp_file_to_vm(vm_inv, zstack_install_script, target_file)

    all_in_one_pkg = os.environ['zstackPkg']
    test_lib.lib_scp_file_to_vm(vm_inv, all_in_one_pkg, aio_target)

    vm_ip = vm_inv.vmNics[0].ip
    ssh.make_ssh_no_password(vm_ip, test_lib.lib_get_vm_username(vm_inv), \
            test_lib.lib_get_vm_password(vm_inv))

def execute_install(ssh_cmd, target_file, tmp_file):
    env_var = "ZSTACK_ALL_IN_ONE='%s' WEBSITE='%s'" % \
            (target_file, 'localhost')

    cmd = '%s "%s bash /root/zstack_installer.sh -d -a"' % (ssh_cmd, env_var)

    process_result = execute_shell_in_process(cmd, tmp_file)

    if process_result != 0:
        cmd = '%s "cat /tmp/zstack_installation.log"' % ssh_cmd
        execute_shell_in_process(cmd, tmp_file)
        test_util.test_fail('zstack installation failed')

def check_installation(ssh_cmd, tmp_file):
    cmd = '%s "/usr/bin/zstack-cli LogInByAccount accountName=admin password=password"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-cli login failed')

    cmd = '%s "/usr/bin/zstack-cli CreateZone name=zone1 description=zone1"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-cli create zone failed')

    cmd = '%s "/usr/bin/zstack-cli QueryZone name=zone1 description=zone1"' % ssh_cmd
    process_result = execute_shell_in_process(cmd, tmp_file)
    if process_result != 0:
        test_util.test_fail('zstack-cli Query zone failed')