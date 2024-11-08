import psycopg2
import main_sql
from typing import List
from icecream import ic

def sql_main(input_list):

    con = psycopg2.connect('dbname = printers user = postgres password = postgres')
    cur = con.cursor()
            
    cur.execute("""SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE  table_name = 'printers'
                );""")
    table_exists: bool = cur.fetchone()

    if table_exists[0] == True:
        cur.execute('''DROP TABLE printers;''')
        print('Table existed. Dropped to recreate.')

    try:
        cur.execute("""CREATE TABLE printers(
                    id integer PRIMARY KEY UNIQUE,
                    serial_number text,
                    make text,
                    model varchar(30),
                    customer_number varchar(8),
                    street_address varchar(60),
                    city varchar(15),
                    state char(2),
                    zip integer DEFAULT 00000,
                    location varchar(600),
                    ip_address varchar(20),
                    mac_address varchar(17)
                    );""")
        print('Table created!')
    except Exception as e:
        ic(e)
  
    for item in input_list:
        try:
            cur.execute("""INSERT INTO printers (
                        id, 
                        serial_number, 
                        make, 
                        model, 
                        customer_number, 
                        street_address,
                        city,
                        state,
                        zip,
                        location,
                        ip_address,
                        mac_address) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", 
                        (item.equipment_number,
                        item.serial_number,
                        item.make,
                        item.model,
                        item.customer_number,
                        item.address,
                        item.city,
                        item.state,
                        item.zip,
                        item.location,
                        item.ip_address,
                        item.mac_address,
                        ))
        except Exception as e:
            ic(e)
            ic(item)
        
    cur.close()
    con.commit()

    print('Table populated!')
    return