import data_utils as du
import sql_utils as su
from tqdm.notebook import tqdm_notebook


def create_functionalizing_entity_tables(connection):

    FuncEntDes_str = "CREATE TABLE IF NOT EXISTS FuncEntDes " + \
        "(ID INT, FunctionEntity VARCHAR(255), FunctionEntityType " + \
        "VARCHAR(150), Description TEXT, ActivationMethod TEXT," + \
        " pubChemID VARCHAR(50), MolarMass VARCHAR(100)," + \
        " MolarMassUnit VARCHAR(100));"

    FuncEntFunction_str = "CREATE TABLE IF NOT EXISTS FuncEntFunction " + \
        "(ID INT, FunctionEntity VARCHAR(255), Function VARCHAR(255), " + \
        "FunctionDescription TEXT);"

    table_creation_querys = [
        FuncEntDes_str,
        FuncEntFunction_str
    ]

    for query in table_creation_querys:
        results = su.simple_querry(
            connection,
            query
            )
        if len(results) == 0:
            print("Table Exists")
        else:
            print(results)
    su.show_tables(connection)


def functionalizingentity_to_sql(
        composition_dt,
        connection
):

    functionalizingentity_dt = {}

    du.parse_dictionary(
        composition_dt,
        "functionalizingentity",
        functionalizingentity_dt
        )

    total_ids = len(functionalizingentity_dt)

    with tqdm_notebook(
        total=total_ids,
        desc='Processing',
        unit='ID'
    ) as progress_bar:

        for ID in functionalizingentity_dt:
            sample_info = functionalizingentity_dt[ID]
            for FuncEntity in sample_info:
                FuncEntity_info = sample_info[FuncEntity]
                for Entry in FuncEntity_info:
                    # Create a cursor object
                    cursor = connection.cursor()

                    # Write to NanoEntDes
                    FuncEntDes_insert = (
                        ID,
                        Entry['Name'],
                        FuncEntity,
                        Entry['description'],
                        Entry['ActivationMethod'],
                        Entry['pubChemID'],
                        Entry['value'],
                        Entry['valueUnit']
                        )

                    # Execute a SELECT statement to check
                    # if the entry already exists

                    search_query = "SELECT COUNT(*) FROM FuncEntDes" + \
                        " WHERE ID = ? AND FunctionEntity = ?" + \
                        " AND FunctionEntityType = ?" + \
                        " AND Description = ?" + \
                        " AND ActivationMethod = ?" + \
                        " AND pubChemID = ?" + \
                        " AND MolarMass = ?" + \
                        " AND MolarMassUnit = ?;"

                    cursor.execute(search_query, FuncEntDes_insert)
                    count = cursor.fetchone()[0]

                    # Check the count to determine if the entry exists
                    if count == 0:
                        # Entry does not exist, proceed with insertion
                        insert_query = "INSERT INTO FuncEntDes " + \
                                        "(ID, FunctionEntity, " + \
                                        "FunctionEntityType, " + \
                                        "Description, " + \
                                        "ActivationMethod, pubChemID, " + \
                                        "MolarMass, MolarMassUnit) " + \
                                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                        cursor.execute(insert_query, FuncEntDes_insert)
                        connection.commit()
                    # else:
                    #     # Entry already exists, skip
                    #     print("Entry already exists, skipping...")

                    # Commit the changes
                    connection.commit()

                    for function in Entry['Functions']:

                        # Write to NanoEntCom
                        FuncEntFunction_insert = (
                            ID,
                            Entry['Name'],
                            function['Type'],
                            function['FunctionDescription']
                            )

                        # Execute a SELECT statement to check
                        # if the entry already exists
                        search_query = "SELECT COUNT(*) " + \
                            "FROM FuncEntFunction WHERE " + \
                            "ID = ? AND FunctionEntity = ? " + \
                            "AND Function = ? " + \
                            "AND FunctionDescription = ?;"

                        cursor.execute(search_query, FuncEntFunction_insert)
                        count = cursor.fetchone()[0]

                        # Check the count to determine if the entry exists
                        if count == 0:
                            # Entry does not exist, proceed with insertion
                            insert_query = "INSERT INTO FuncEntFunction " + \
                                            "(ID, FunctionEntity, " + \
                                            "Function, " + \
                                            "FunctionDescription) " + \
                                            "VALUES (?, ?, ?, ?)"
                            cursor.execute(insert_query,
                                           FuncEntFunction_insert)
                            connection.commit()
                        # else:
                        #     # Entry already exists, skip
                        #     print("Entry already exists, skipping...")
            progress_bar.update(1)
    cursor.close()
