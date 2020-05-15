#SCRIPT FOR SHAREPOINT DATABASE BACKUP WITH NETBACKUP
import errno, os, winreg
from string import Template

aKey = r"SOFTWARE\Microsoft\MSSQLServer\Client"
database_list = "db_list.txt"

# (STEP 1) - Reading Registry Key

#Read HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\MSSQLServer\Client (64 bit key)
key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, aKey, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) 

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
#print(registry_key_value)


# (STEP 2) - Reading file
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

#[print(i,v) for i,v in db_alias_dictionary.items()]


# (STEP 3) - Prepare backup script
#DB_NAME required  
#HOSTNAME required
#ISTANCE_NAME required

template_env_file = open("template_env_script", "r")
file_string = template_env_file.read()
template_file_string = Template(file_string)

final_script = ""
for obj in db_alias_dictionary:
      
      db_name = obj.upper()
      hostname = db_alias_dictionary[obj].split('\\')[0].upper()
      instance_name = db_alias_dictionary[obj].split('\\')[1].upper()
      
      final_script += template_file_string.substitute(DB_NAME=db_name, HOSTNAME=hostname, ISTANCE_NAME=instance_name) + "\n\n"


# f = open("netbackup_script.bch", "a") #Create script file in local directory
# f.write("Now the file has more content!")
# f.close()

