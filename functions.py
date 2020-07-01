import errno, os, winreg, sys
from string import Template
def readRegKey(local_machine_regedit_key):

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, local_machine_regedit_key, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) 
    subkey_connect_to_name = winreg.EnumKey(key, 0) # get name of first sub_key ('ConnectTo')
    subkey_connect_to = winreg.OpenKey(key, subkey_connect_to_name) # Read 'ConnectTo' key.

    # Filling Dictionary with Registry Key Values 
    registry_key_value = {}
    for i in range(0, winreg.QueryInfoKey(subkey_connect_to)[1]):
        registry_value = winreg.EnumValue(subkey_connect_to, i)
        
        if(registry_value[1] != 0 and registry_value[1] != '' ):
            key = registry_value[0].lower()
            value = registry_value[1].split(',')[1]

            if(not key in registry_key_value.values() ): #if value isn't yet in dictionary.
                registry_key_value[key] = value

    #Key-Value Registry Dictionary
    number_of_items_machine_registry = len(registry_key_value.items())
    return registry_key_value;

def readDBFileAndReplace(database_list,registry_key_value):

    print("\n(STEP 2) ------- Reading local SQL Database file ------")
    print(str(database_list) + " opened")

    shp_exp_file = open(database_list, "r")
    i=0

    db_alias_dictionary = {}
    for line in shp_exp_file:
        if(i != 0): #Skip first line
            kv = line.split(',') #Create key-value array
            db_name = kv[0].strip().replace("\"","")
            alias = kv[1].strip().replace("\"","")
            solved_alias = ""
            try:
                index = list(registry_key_value.keys()).index(alias) 
                solved_alias = list(registry_key_value.values())[index]
            except:
                solved_alias = alias
                pass

            db_alias_dictionary[db_name] = solved_alias
        i+=1
    shp_exp_file.close()

    return db_alias_dictionary;

def createScript(template_netbackup_script,db_alias_dictionary,final_netbackup_script):
    print("\n(STEP 3) ------- Prepare backup script ------")

    template_env_file = open(template_netbackup_script, "r")
    file_string = template_env_file.read()
    template_file_string = Template(file_string)

    #Count number of entry for istance name
    hostname_instance_counter = {}
    for item in set(db_alias_dictionary.values()):
        hostname_instance_counter[item.upper()] = sum(value == item for value in db_alias_dictionary.values())
        #print(sum(value == item for value in db_alias_dictionary.values()))
    #[print(i + "---->"+ str(v)) for i,v in hostname_instance_counter.items()]

    #Change alias with registry key instance name
    final_script_dict = {}
    for key,value in db_alias_dictionary.items():
        
        db_name = key
        source_machine_instance = value.upper()
        
        #print(source_machine_instance)
        hostname = source_machine_instance.split('\\')[0]
        instance_name = source_machine_instance.split('\\')[1]
        
        if source_machine_instance in final_script_dict:
            final_script_dict[source_machine_instance] += template_file_string.substitute(DB_NAME=db_name, HOSTNAME=hostname, ISTANCE_NAME=instance_name) + "\n\n"
        else:
            final_script_dict[source_machine_instance] = template_file_string.substitute(DB_NAME=db_name, HOSTNAME=hostname, ISTANCE_NAME=instance_name) + "\n\n"
    
    for key,value in final_script_dict.items():
        key_for_file_name = final_netbackup_script + "-" + key.replace("\\","-").lower() + ".bch"
        f = open(key_for_file_name, "w") # Create script file in local directory
        f.write("GROUPSIZE " + str(hostname_instance_counter[key]) + "\n") #INSERT FIRST LINE OF SCRIPT WITH NUMBER OF OPERATIONS
        f.write(final_script_dict[key])
        f.close()
        print("Script: " + str(key_for_file_name) + " written")
