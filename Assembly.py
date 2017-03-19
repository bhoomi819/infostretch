from pymongo import MongoClient
from bson.objectid import ObjectId
import click
import re

client = MongoClient()
db = client['assembly_db']
collection_name = "assembly_collection"
collection = None


def take_action():
    new_choice = click.prompt('\nPlease enter your choice', type=int)
    # If the choice is to exit, then don't do anything and exit, else for any other choice,
    # first take the action, and then make a recursive call to take_action to repeat
    global collection
    if new_choice == 10:
        print("Exiting....")
    else:
        if new_choice == 1:
            load_assembly()
        elif collection is not None:  # We need that load assembly has happened or collection variable is initialized for actions 2, 3, 4 to succeed
            if new_choice == 2:
                entry_name = click.prompt('\tPlease enter entry name', type=str)
                description = click.prompt('\tPlease enter entry description', type=str)
                version = click.prompt('\tPlease enter entry version', type=int)
                add_entry(entry_name, description, version)

            elif new_choice == 3:
                entry_name = click.prompt('\tPlease enter entry name to remove: ', type=str)
                remove_entry(entry_name)

            elif new_choice == 4:
                print("Here is the list of all existing entries")
                list_entries()

            elif new_choice == 5:
                entry_name = click.prompt('\t Please enter entry name to update: ',type=str)
                update_entry(entry_name)

            elif new_choice == 6:
                list = get_entry_name_list()
                list.sort()
                print_list(list)

            elif new_choice==7:
                keyword=click.prompt('\t Please enter keyword to search: ',type=str)
                search(keyword)

        else:
            print("Choose 1. to load assembly before trying other actions")

    take_action()


# Load assembly, if mongo collection doesn't exist, create it, otherwise return the existing one
def load_assembly():
    global collection
    already_exists = collection_name in db.collection_names()
    if not already_exists:
        print("Created and Loaded assembly")
        collection = db.create_collection(collection_name)
    else:
        print("Loaded existing assembly")
        collection = db.get_collection(collection_name)

def search(keyword):
    Entries=list(collection.find())
    for entry in Entries:
        entry_name=entry['name']
        description=entry['description']
        name_match = re.search(keyword, entry_name)
        desc_match = re.search(keyword, description)
        if name_match or desc_match:
            print(entry)

# Given the entry_name, description and version,
# create a json document and call function "insert_one" to insert that document
def add_entry(entry_name, description, version):
    entry = {"name": entry_name, "description": description, "version": version}
    collection.insert_one(entry)
    print("Successfully added an entry")


# collection.update_one({'_id': UUID}, {'$set': {'name': new_entry_name}})

def update_entry(entry_name):
    documents = collection.find({'name' : entry_name})
    list_of_entries = list(documents)
    print(list_of_entries)
    uuid = None

    if len(list_of_entries) == 0:
        print("Entry " + entry_name + " does not exist")
        return
    elif len(list_of_entries) > 1:
        print("\n Multiple entries for "+entry_name+ "found. Please enter Object Id to specify unique entry to update")
        for entry in list_of_entries:
            print(entry['_id'])
        uuid = click.prompt('\n Object ID here:')

    print(list_of_entries)
    field_to_update = click.prompt('\n Enter variable to update- "i)entry_name OR  ii)description OR  iii)version: ')
    if field_to_update == 'entry_name':
        new_entry_name = click.prompt('\tPlease enter new entry name', type=str)
        if uuid is not None:
            #print(uuid + " is present")
            collection.update_one({'_id': ObjectId(uuid)}, {'$set': {'name': new_entry_name}})
            return
        else:
            collection.update_one({'name': entry_name}, {'$set': {'name': new_entry_name}})
            return

    elif field_to_update == 'description':
        new_description = click.prompt('\tPlease enter new description', type=str)
        if uuid is not None:
            #print(uuid+ " is present")
            collection.update_one({'_id':ObjectId(uuid)},{'$set':{'description':new_description}})
            return
        else:
            collection.update_one({'name':entry_name},{'$set':{'description':new_description}})
            return
    elif field_to_update == 'version':
        new_version = click.prompt('\tPlease enter new version', type=int)

        if uuid is not None:
            #print(uuid+ " is present")
            collection.update_one({'_id':ObjectId(uuid)},{'$set':{'version':new_version}})
            return
        else:
            collection.update_one({'name':entry_name},{'$set':{'version':new_version}})
            return
    else:
        print("\n Enter input only from given options in proper case: i)entry_name  ii) description iii)version ")


# Remove the entry called "entry_name"
def remove_entry(entry_name):
    write_result = collection.remove({"name" : entry_name})
    if write_result['n'] != 0:
        print("Entry" +entry_name+ " is removed")
    else:
        print("Entry " +entry_name+ " does not exist")

# This function queries mongo to get a list of entry names
def get_entry_name_list():
    documents = collection.find()
    list_of_entries = list(documents)
    print(list_of_entries)
    list_of_entry_names = list()
    for entry in list_of_entries:
        entry_name = entry['name']
        list_of_entry_names.append(entry_name)
    return list_of_entry_names

def print_list(entry_names):
    for entry in entry_names:
        print("\t" + entry)

def print_entries(entries):
    for entry in entries:
        print(entry['_id'])

# List all entries
def list_entries():
    entry_names = get_entry_name_list()
    print_list(entry_names)

if __name__ == '__main__':
   print("1. Load assembly")
   print("2. Add entry")
   print("3. Remove entry")
   print("4. List all entries")
   print("5. Update an entry")
   print("6. Sort all entries")
   print("7. Search an entry")
   print("10. Exit")
   take_action()

