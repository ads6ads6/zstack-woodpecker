'''
@author: Quarkonics
'''
import os
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.operations.host_operations as host_ops
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.vm_operations as vm_ops

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()

def test():
    test_util.test_dsc('Test VM online change instance offering')

    image_name = os.environ.get('imageName_net')
    image_uuid = test_lib.lib_get_image_by_name(image_name).uuid
    l3_name = os.environ.get('l3VlanNetworkName1')
    l3_net_uuid = test_lib.lib_get_l3_by_name(l3_name).uuid
    l3_net_list = [l3_net_uuid]
    cpuNum = 2
    cpuSpeed = 222
    memorySize = 666 * 1024 * 1024
    new_offering = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            cpuSpeed = cpuSpeed, memorySize = memorySize)
    test_obj_dict.add_instance_offering(new_offering)
    new_offering_uuid = new_offering.uuid

    vm = test_stub.create_vm(l3_net_list, image_uuid, 'online_chg_offering_vm', instance_offering_uuid=new_offering_uuid, system_tags=['instanceOfferingOnlinechange::true'])
    test_obj_dict.add_vm(vm)

    cpuNum = 1
    memorySize = 222 * 1024 * 1024
    new_offering2 = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            cpuSpeed = cpuSpeed, memorySize = memorySize)
    test_obj_dict.add_instance_offering(new_offering2)
    new_offering_uuid2 = new_offering2.uuid

    vm.change_instance_offering(new_offering_uuid2)

    cpuNum = 1
    memorySize = 444 * 1024 * 1024
    new_offering3 = test_lib.lib_create_instance_offering(cpuNum = cpuNum,\
            cpuSpeed = cpuSpeed, memorySize = memorySize)
    test_obj_dict.add_instance_offering(new_offering3)
    new_offering_uuid3 = new_offering3.uuid
    vm.change_instance_offering(new_offering_uuid3)

    test_lib.lib_robot_cleanup(test_obj_dict)

    test_util.test_pass('VM online change instance offering Test Pass')

#Will be called only if exception happens in test().
def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)
