import data_utils as du
import sql_utils as su
from tqdm.notebook import tqdm_notebook


def create_nanomaterial_entity_tables(connection):

    NanoEntDes_str = "CREATE TABLE IF NOT EXISTS `NanoEntDes` " + \
        "(`ID` INT, `NanoEntity` VARCHAR(255), `Description` TEXT);"

    NanoEntCom_str = "CREATE TABLE IF NOT EXISTS NanoEntCom " + \
        "(ID INT, NanoEntity VARCHAR(255), Composition VARCHAR(100), " + \
        "CompositionType VARCHAR(100), MolecularWeight VARCHAR(150), " + \
        "PubChemID VARCHAR(255));"

    table_creation_querys = [
        NanoEntDes_str,
        NanoEntCom_str
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


def nanomaterialentity_to_sql(
        composition_dt,
        connection
):

    nanomaterialentity_dt = {}

    du.parse_dictionary(
        composition_dt,
        "nanomaterialentity",
        nanomaterialentity_dt
        )

    total_ids = len(nanomaterialentity_dt)

    with tqdm_notebook(
        total=total_ids,
        desc='Processing',
        unit='ID'
    ) as progress_bar:

        for ID in nanomaterialentity_dt:
            sample_info = nanomaterialentity_dt[ID]
            for NanoEntity in sample_info:
                NanoEntity_info = sample_info[NanoEntity]
                for Entry in NanoEntity_info:
                    # Create a cursor object
                    cursor = connection.cursor()

                    # Write to NanoEntDes
                    NanoEntDes_insert = (ID, NanoEntity, Entry['Description'])

                    # Execute a SELECT statement to check
                    # if the entry already exists

                    search_query = "SELECT COUNT(*) FROM NanoEntDes" + \
                        " WHERE ID = ? AND NanoEntity = ?" + \
                        " AND Description = ?"

                    cursor.execute(search_query, NanoEntDes_insert)
                    count = cursor.fetchone()[0]

                    # Check the count to determine if the entry exists
                    if count == 0:
                        # Entry does not exist, proceed with insertion
                        insert_query = "INSERT INTO NanoEntDes " + \
                                        "(ID, NanoEntity, Description) " + \
                                        "VALUES (?, ?, ?)"
                        cursor.execute(insert_query, NanoEntDes_insert)
                        connection.commit()
                    # else:
                    #     # Entry already exists, skip
                    #     print("Entry already exists, skipping...")

                    # Commit the changes
                    connection.commit()

                    for composition in Entry['ComposingElements']:
                        if 'DisplayName' in composition and not composition[
                            'DisplayName'
                        ]:

                            composition_type = "NULL"
                            composition_name = "NULL"
                            composition_MolecularWeight = "NULL"

                        else:
                            # Extract composition_type
                            displayname = composition['DisplayName']
                            index_open = displayname.find("(")
                            composition_type = displayname[
                                :index_open
                                ].strip() if index_open != -1 else "NULL"

                            # Extract composition_name and composition_quantity
                            index_name = displayname.find(
                                "name: "
                            ) + len("name: ")
                            index_amount = displayname.find(", amount: ")

                            if index_name != -1:
                                if index_amount != -1:
                                    composition_name = displayname[
                                        index_name:index_amount
                                        ].strip()
                                    composition_MolecularWeight = displayname[
                                        index_amount + len(", amount: "):-1
                                        ].strip()
                                else:
                                    composition_name = displayname[
                                        index_name:-1
                                        ].strip()
                                    composition_MolecularWeight = "NULL"
                            else:
                                composition_name = "NULL"
                                composition_MolecularWeight = "NULL"

                        if 'PubChemId' in composition and not composition[
                            'PubChemId'
                        ]:
                            PubChemID = "Null"
                        else:
                            PubChemID = composition['PubChemId']

                    # Write to NanoEntCom
                        NanoEntCom_insert = (
                            ID,
                            NanoEntity,
                            composition_name,
                            composition_type,
                            composition_MolecularWeight,
                            PubChemID
                            )

                        # Execute a SELECT statement to check
                        # if the entry already exists
                        search_query = "SELECT COUNT(*) " + \
                            "FROM NanoEntCom WHERE " + \
                            "ID = ? AND NanoEntity = ? " + \
                            "AND Composition = ? " + \
                            "AND CompositionType = ? " + \
                            "AND MolecularWeight = ? " + \
                            "AND PubChemID = ?"

                        cursor.execute(search_query, NanoEntCom_insert)
                        count = cursor.fetchone()[0]

                        # Check the count to determine if the entry exists
                        if count == 0:
                            # Entry does not exist, proceed with insertion
                            insert_query = "INSERT INTO NanoEntCom " + \
                                            "(ID, NanoEntity, " + \
                                            "Composition, " + \
                                            "CompositionType, " + \
                                            "MolecularWeight, PubChemID) " + \
                                            "VALUES (?, ?, ?, ?, ?, ?)"
                            cursor.execute(insert_query, NanoEntCom_insert)
                            connection.commit()
                        # else:
                        #     # Entry already exists, skip
                        #     print("Entry already exists, skipping...")
            progress_bar.update(1)
    cursor.close()
