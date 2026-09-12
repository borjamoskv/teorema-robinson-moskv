#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/sysctl.h>
#include <mach/mach.h>
#include <mach/vm_statistics.h>

int main() {
    size_t alloc_size = 1024 * 1024 * 10;
    void *immune_memory = malloc(alloc_size);
    int mlock_res = mlock(immune_memory, alloc_size);
    
    mach_msg_type_number_t count = HOST_VM_INFO64_COUNT;
    vm_statistics64_data_t vm_stat;
    mach_port_t host_port = mach_host_self();
    kern_return_t kr = host_statistics64(host_port, HOST_VM_INFO64, (host_info64_t)&vm_stat, &count);
    
    int thermal_level = -1;
    size_t size = sizeof(thermal_level);
    sysctlbyname("machdep.xcpm.cpu_thermal_level", &thermal_level, &size, NULL, 0);

    int logical_cpus = 0;
    size = sizeof(logical_cpus);
    sysctlbyname("hw.logicalcpu", &logical_cpus, &size, NULL, 0);

    printf("{\n");
    printf("  \"panopticon_status\": \"ACTIVE\",\n");
    printf("  \"mlock_status\": %d,\n", mlock_res);
    printf("  \"mlock_bytes_locked\": %zu,\n", alloc_size);
    if (kr == KERN_SUCCESS) {
        printf("  \"mach_free_pages\": %llu,\n", vm_stat.free_count);
        printf("  \"mach_active_pages\": %llu,\n", vm_stat.active_count);
    }
    printf("  \"thermal_level\": %d,\n", thermal_level);
    printf("  \"logical_cpus\": %d\n", logical_cpus);
    printf("}\n");

    munlock(immune_memory, alloc_size);
    free(immune_memory);
    return 0;
}
