'''
@author: FangSun
'''
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import hot_plug_common
import zstackwoodpecker.operations.vm_operations as vm_ops
import time

_config_ = {
        'timeout': 1000,
        'noparallel' : False
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():
    vm = hot_plug_common.create_onlinechange_vm(test_stub, test_obj_dict)
    (total_cpu_before, total_mem_before, vm_outer_cpu_before, vm_outer_mem_before,
     vm_interal_cpu_before, vm_interal_mem_before) =hot_plug_common.check_cpu_mem(vm)

    vm_instance_offering = test_lib.lib_get_instance_offering_by_uuid(vm.get_vm().instanceOfferingUuid)
    vm_ops.update_vm(vm.get_vm().uuid, None, vm_instance_offering.memorySize + 1024*1024*1024)
    vm.update()
    time.sleep(10)

    (total_cpu_after, total_mem_after, vm_outer_cpu_after, vm_outer_mem_after,
     vm_interal_cpu_after, vm_internal_mem_after) = hot_plug_common.check_cpu_mem(vm)

    assert total_cpu_before == total_cpu_after
    assert total_mem_before == total_mem_after - 1024*1024*1024
    assert vm_outer_cpu_before == vm_outer_cpu_after
    assert vm_outer_mem_before == vm_outer_mem_after - 1
    assert vm_interal_cpu_before == vm_interal_cpu_after
    assert vm_interal_mem_before == vm_internal_mem_after - 1024


def error_cleanup():
    test_lib.lib_error_cleanup(test_obj_dict)