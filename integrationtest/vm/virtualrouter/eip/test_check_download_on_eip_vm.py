'''

Test create EIP for a VM. 

Test step:
    1. Create a VM
    2. Create a EIP with VM's nic
    3. Check the EIP connectibility
    4. Destroy VM

@author: Glody
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import os

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Create test vm with EIP and check.')
    vm = test_stub.create_vlan_vm(os.environ.get('l3VlanNetworkName1'))
    test_obj_dict.add_vm(vm)
    
    l3_name = os.environ.get('l3VlanNetworkName1')
    vr1_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr1_l3_uuid)
    temp_vm1 = None
    if not vrs:
        #create temp_vm1 for getting vlan1's vr for test pf_vm portforwarding
        temp_vm1 = test_stub.create_vlan_vm()
        test_obj_dict.add_vm(temp_vm1)
        vr1 = test_lib.lib_find_vr_by_vm(temp_vm1.vm)[0]
    else:
        vr1 = vrs[0]

    l3_name = os.environ.get('l3NoVlanNetworkName1')
    vr2_l3_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    vrs = test_lib.lib_find_vr_by_l3_uuid(vr2_l3_uuid)
    temp_vm2 = None
    if not vrs:
        #create temp_vm2 for getting novlan's vr for test pf_vm portforwarding
        temp_vm2 = test_stub.create_user_vlan_vm()
        test_obj_dict.add_vm(temp_vm2)
        vr2 = test_lib.lib_find_vr_by_vm(temp_vm2.vm)[0]
    else:
        vr2 = vrs[0]

    #we do not need temp_vm1 and temp_vm2, since we just use their VRs.
    if temp_vm1:
        temp_vm1.destroy()
        test_obj_dict.rm_vm(temp_vm1)
    if temp_vm2:
        temp_vm2.destroy()
        test_obj_dict.rm_vm(temp_vm2)

    vm_nic = vm.vm.vmNics[0]
    vm_nic_uuid = vm_nic.uuid
    pri_l3_uuid = vm_nic.l3NetworkUuid
    vr = test_lib.lib_find_vr_by_l3_uuid(pri_l3_uuid)[0]
    vr_pub_nic = test_lib.lib_find_vr_pub_nic(vr)
    l3_uuid = vr_pub_nic.l3NetworkUuid
    vip = test_stub.create_vip('create_eip_test', l3_uuid)
    test_obj_dict.add_vip(vip)
    eip = test_stub.create_eip('create eip test', vip_uuid=vip.get_vip().uuid, vnic_uuid=vm_nic_uuid, vm_obj=vm)
    
    vip.attach_eip(eip)
   
    vm_ip = vm_nic.ip
    user_name = 'root'
    user_password = 'password'
 
    vm.check()
    vip.check()

    cmd = "ping -c 4 172.20.0.1"
    rsp_ping = os.system("sshpass -p '%s' ssh %s@%s '%s'"%(user_password, user_name, vm_ip, cmd)) 

    #Try to download webpage from Jenkins server
    cmd = "curl http://172.20.198.250"
    rsp_curl = os.system("sshpass -p '%s' ssh %s@%s '%s'"%(user_password, user_name, vm_ip, cmd))
    if rsp_ping != 0:
        test_util.test_fail('Attach EIP but cannot ping from VM')
    if rsp_ping == 0 and rsp_curl != 0:
        test_util.test_fail('Attach EIP and can ping from the VM, but cannot download anything in VM')

    vm.destroy()
    test_obj_dict.rm_vm(vm)
    vip.check()
    eip.delete()
    vip.delete()
    test_obj_dict.rm_vip(vip)
    test_util.test_pass('Attached EIP and download webpage in VM Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
