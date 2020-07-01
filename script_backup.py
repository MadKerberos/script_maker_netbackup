#SCRIPT FOR SHAREPOINT DATABASE BACKUP WITH NETBACKUP
import errno, os, sys
import functions
from string import Template

local_machine_regedit_key = r"SOFTWARE\Microsoft\MSSQLServer\Client"
database_list = "source_informations\\database_list.txt"
template_netbackup_script = "source_informations\\template_netbackup_script.txt"
netbackup_shp_script = "output_script\\netbackup_sharepoint_script"

# (STEP 1) - Reading Registry Key
dic_registry_key = functions.readRegKey(local_machine_regedit_key)
number_of_items_machine_registry = len(dic_registry_key)
print(str(number_of_items_machine_registry) + " items detected\n")    
[print(i + "---->"+v) for i,v in dic_registry_key.items()]

# (STEP 2) - Reading file and replace alias
db_alias_dictionary = functions.readDBFileAndReplace(database_list,dic_registry_key)
number_of_items_sql_entry = len(db_alias_dictionary.items())
print(str(number_of_items_sql_entry) + " items detected\n")
#[print(i + "---->"+v) for i,v in db_alias_dictionary.items()]

#(STEP 3) - Prepare backup script
if number_of_items_sql_entry > 0 :
    functions.createScript(template_netbackup_script,db_alias_dictionary,netbackup_shp_script)
else:
    print("\n0 elements founded in database_list")
    sys.exit()
