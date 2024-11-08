
'''Trying to use Pydantic to validate pieces of equipment read from a CSV'''

import pydantic
from pydantic_core import PydanticCustomError
from pydantic_extra_types.mac_address import MacAddress
from pydantic import ValidationError, ConfigDict, Field as PydanticField, AliasChoices, IPvAnyAddress
from typing import Optional, List, Generator, Dict, Any, Annotated
from icecream import ic
from easygui import *
import csv
import sql_stuff

class Copier:
    copiers: List = []
    
class ValidationResults:
    passed: List = []
    failed: List = []

class Equipment(pydantic.BaseModel):
    model_config  = ConfigDict(protected_namespaces=(),
                            from_attributes=True,
                            populate_by_name=True,
                            str_strip_whitespace=True)
    
    equipment_number: Annotated[int, PydanticField(validation_alias=AliasChoices("Equipment number"))]
    serial_number: Annotated[str, PydanticField(validation_alias=AliasChoices("Serial number"))]
    item_desc: Annotated[str, PydanticField(validation_alias=AliasChoices("Item desc."))]
    customer_name: Annotated[str, PydanticField(validation_alias=AliasChoices("Customer name"))]
    customer_number: Annotated[str, PydanticField(validation_alias=AliasChoices("Customer number"))]
    make: Annotated[str, PydanticField(validation_alias=AliasChoices("Make"))]
    model: Annotated[str, PydanticField(validation_alias=AliasChoices("Model"))]
    address: Annotated[str, PydanticField(validation_alias=AliasChoices("Address"))]
    city: Annotated[str, PydanticField(validation_alias=AliasChoices("City"))]
    state: Annotated[str, PydanticField(validation_alias=AliasChoices("State"))]
    zip: Annotated[Optional[int], PydanticField(validation_alias=AliasChoices("Zip"))]
    location: Annotated[str, PydanticField(validation_alias=AliasChoices("Location"))]
    cost_center: Annotated[Optional[str], None] = None
    ip_address: Annotated[Optional[str], PydanticField(validation_alias=AliasChoices("IP address"))]
    mac_address: Annotated[Optional[MacAddress], PydanticField(validation_alias=AliasChoices("MAC address"))] 
    install_date: Annotated[str, PydanticField(validation_alias=AliasChoices("Install date"))]

def equipment_row_generator() -> Generator:
    input_csv: str = fileopenbox(msg = 'Select the input file. Must be a .csv', default='*.csv', filetypes = ['*.csv'])
    if not input_csv:
        print('No input file selected.')
        exit()    
    with open(input_csv, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row

def attempt_fix_machines(list) -> None:
    _corrected_amount: int = 0
    for machine in list:
        try:
            if not machine['IP address'] or machine['IP address'] == '':
                machine['IP address'] = '0.0.0.0'
            if not machine['MAC address'] or machine['MAC address'] == '':
                machine['MAC address'] = '00:00:00:00:00:00'
            if not machine['Zip'] or machine['Zip'] == '' :
                machine['Zip'] = 00000
            Copier.copiers.append(Equipment(**machine))
            _corrected_amount += 1
        except ValidationError as e:
            ic(e)
            ic(machine['Equipment number'])
    print(f'Corrected {_corrected_amount} machines!')

def main() -> None:
    '''Main Function'''
    equip_gen = equipment_row_generator()
   
    for item in equip_gen:    #iterate through the generator that is fed from the input CSV. Machines get added to a 'Pass' list or a 'Fail' list.
        try:
            Copier.copiers.append(Equipment(**item))
            ValidationResults.passed.append(item)
        except ValidationError as e:
            #ic(item['Equipment number'])
            ValidationResults.failed.append(item)
    
    #try to fix machines that failed validation with this function so they can be added to the invoice
    if len(ValidationResults.failed) > 0:
        attempt_fix_machines((ValidationResults.failed))

    for copier in Copier.copiers:
        split_locaton = copier.location.split()
        try:
            cost_center_index = split_locaton.index('CC:')
            copier.cost_center = split_locaton[cost_center_index + 1]
        except:
            copier.cost_center = 'UNKNOWN'
            
    print('Finished prepping machines for SQL!')

    sql_stuff.sql_main(Copier.copiers)
    return

if __name__ == '__main__':
    main()