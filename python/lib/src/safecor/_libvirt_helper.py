""" \author Tristan Israël """

import libvirt

class LibvirtHelper():

    @staticmethod
    def get_domains() -> dict:
        """ @brief Returns the list of Domains declared on the system and their status """

        domains = {}

        conn = LibvirtHelper.__open_readonly()
        if conn is False:
            return domains

        conn.getAllDomainStats()

        conn.close()

        return domains

    @staticmethod
    def get_vcpu_information() -> dict:
        """ @brief Returns information about vcpus of all domains """
        vcpus = {}

        conn = LibvirtHelper.__open_readonly()
        if conn is False:
            return vcpus
        
        conn.close()

        return vcpus 

    @staticmethod
    def get_cpu_count() -> int:
        """ @brief Returns the number of CPU in the system 
        
            In case of error the function returns 0.
        """
        
        conn = LibvirtHelper.__open_readonly()
        if conn is False:
            return 0
        
        info = conn.getInfo()
        if info is None:
            print("ERROR: Could not get information about the host")
            conn.close()
            return 0

        count =  info[2]
        conn.close()

        return count

    @staticmethod
    def reboot_domain(domain_name:str) -> bool:
        """ @brief Reboots a domain.
         
            Returns True if the reboot has been acknowledged by the hypervisor 
        """

        result = False
        conn = LibvirtHelper.__open_readwrite()

        try:
            dom = conn.lookupByName(domain_name)
            dom.reboot()
            # Can we get more information?
        except libvirt.libvirtError:
            print(f"ERROR: Could not access domain {domain_name}")
            conn.close()
            return False

        conn.close()
        return result

    @staticmethod
    def __open_readonly() -> libvirt.virConnect|bool:
        try:
            conn = libvirt.openReadOnly("xen:///")
            return conn
        except libvirt.libvirtError:
            print("ERROR: Could not open connection (RO) to libvirt")            
            return False

    @staticmethod
    def __open_readwrite() -> libvirt.virConnect|bool:
        try:
            conn = libvirt.open("xen:///")
            return conn
        except libvirt.libvirtError:
            print("ERROR: Could not open connection (RW) to libvirt")
            return False
        
    