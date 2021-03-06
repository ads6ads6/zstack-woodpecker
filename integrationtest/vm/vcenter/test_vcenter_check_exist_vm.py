'''
test for checking if vm exist in newly add vcenter
@author: SyZhao
'''

import apibinding.inventory as inventory
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.vm_operations as vm_ops
import zstackwoodpecker.operations.vcenter_operations as vct_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstacklib.utils.ssh as ssh
import test_stub
import os

vcenter_uuid = None

def test():
    global vcenter_uuid

    vcenter1_name = os.environ['vcenter1_name']
    vcenter1_domain_name = os.environ['vcenter1_ip']
    vcenter1_username = os.environ['vcenter1_domain_name']
    vcenter1_password = os.environ['vcenter1_password']
    vm_name_pattern1 = os.environ['vcenter1_vm_pattern1']  
    vm_name_pattern2 = os.environ['vcenter1_vm_pattern2'] 


    #add vcenter senario1:
    zone_uuid = res_ops.get_resource(res_ops.ZONE)[0].uuid
    inv = vct_ops.add_vcenter(vcenter1_name, vcenter1_domain_name, vcenter1_username, vcenter1_password, True, zone_uuid)
    vcenter_uuid = inv.uuid

    if vcenter_uuid == None:
        test_util.test_fail("vcenter_uuid is None")

    #insert the basic operations for the newly join in vcenter resourse
    vm_list = []
    vm_names = res_ops.query_resource_fields(res_ops.VM_INSTANCE, [], None, fields=['name'])
    for vm_name in vm_names:
        vm_list.append(vm_name.name)

    test_util.test_logger( ", ".join( [ str(vm_name_tmp) for vm_name_tmp in vm_list ] ) )

    if vm_name_pattern1 not in vm_list:
        test_util.test_fail("newly joined vcenter missing fingerprint vm1, test failed")

    if vm_name_pattern2 not in vm_list:
        test_util.test_fail("newly joined vcenter missing fingerprint vm2, test failed")

    vct_ops.delete_vcenter(vcenter_uuid)
    test_util.test_pass("add && delete vcenter test passed.")



def error_cleanup():
    global vcenter_uuid
    if vcenter_uuid:
        vct_ops.delete_vcenter(vcenter_uuid)
