import data_utils as du
import sql_utils as su
from tqdm.notebook import tqdm_notebook


def create_ChemAsso_tables(connection):

    table_String_ChemAssoName = "CREATE TABLE IF NOT EXISTS ChemAsso (" + \
        "ID INT, " + \
        "AssociationType VARCHAR(150), " + \
        "BondType VARCHAR(150), " + \
        "Description TEXT, " + \
        "dataId INT, " + \
        "ComposingElementNameA VARCHAR(150), " + \
        "ComposingElementNameB VARCHAR(150), " + \
        "CompositiontypeB VARCHAR(150), " + \
        "CompositiontypeA VARCHAR(150), " + \
        "DomainElementNameB VARCHAR(150), " + \
        "DomainElementNameA VARCHAR(150), " + \
        "DomainAssociationId INT, " + \
        "ComposingElemetIdB INT, " + \
        "ComposingElemetIdA INT, " + \
        "ComposingElementTypeA VARCHAR(150), " + \
        "EntityDisplayNameB VARCHAR(150), " + \
        "ComposingElementTypeB VARCHAR(150), " + \
        "EntityDisplayNameA VARCHAR(150), " + \
        "AttachmentId INT);"

    table_creation_querys = [
        table_String_ChemAssoName
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


def chemicalassociation_to_sql(
        composition_dt,
        connection
):

    chemicalassociation_dt = {}

    du.parse_dictionary(
        composition_dt,
        "chemicalassociation",
        chemicalassociation_dt
        )

    total_ids = len(chemicalassociation_dt)

    with tqdm_notebook(
        total=total_ids,
        desc='Processing',
        unit='ID'
    ) as progress_bar:

        # Create a cursor object
        cursor = connection.cursor()

        for ID in chemicalassociation_dt:
            sample_info = chemicalassociation_dt[ID]
            for AssociationType in sample_info:
                AssociationType_info = sample_info[AssociationType]
                for Entry in AssociationType_info:
                    # Create a cursor object
                    elements = Entry['AssocitedElements']

                    # Write to NanoEntCom
                    ChemAsso_insert = (
                        ID,
                        AssociationType,
                        Entry['BondType'],
                        Entry['Description'],
                        Entry['dataId'],
                        elements['ComposingElementNameA'],
                        elements['ComposingElementNameB'],
                        elements['CompositiontypeB'],
                        elements['CompositiontypeA'],
                        elements['DomainElementNameB'],
                        elements['DomainElementNameA'],
                        elements['DomainAssociationId'],
                        elements['ComposingElemetIdB'],
                        elements['ComposingElemetIdA'],
                        elements['ComposingElementTypeA'],
                        elements['EntityDisplayNameB'],
                        elements['ComposingElementTypeB'],
                        elements['EntityDisplayNameA'],
                        Entry['AttachmentId']
                        )

                    # Execute a SELECT statement to check
                    # if the entry already exists
                    search_query = "SELECT COUNT(*) " + \
                        "FROM ChemAsso WHERE " + \
                        "ID = ? AND AssociationType = ? " + \
                        "AND BondType = ? " + \
                        "AND Description = ? " + \
                        "AND dataId = ?;"

                    cursor.execute(search_query, ChemAsso_insert[:5])
                    count = cursor.fetchone()[0]

                    # Check the count to determine if the entry exists
                    if count == 0:
                        # Entry does not exist, proceed with insertion
                        insert_query = "INSERT INTO ChemAsso (" + \
                            "ID, " + \
                            "AssociationType, " + \
                            "BondType, " + \
                            "Description, " + \
                            "dataId, " + \
                            "ComposingElementNameA, " + \
                            "ComposingElementNameB, " + \
                            "CompositiontypeB, " + \
                            "CompositiontypeA, " + \
                            "DomainElementNameB, " + \
                            "DomainElementNameA, " + \
                            "DomainAssociationId, " + \
                            "ComposingElemetIdB, " + \
                            "ComposingElemetIdA, " + \
                            "ComposingElementTypeA, " + \
                            "EntityDisplayNameB, " + \
                            "ComposingElementTypeB, " + \
                            "EntityDisplayNameA, " + \
                            "AttachmentId) " + \
                            "VALUES (?, ?, ?, ?, " + \
                            "?, ?, ?, ?, ?, ?, ?, ?, " + \
                            "?, ?, ?, ?, ?, ? , ?)"

                        cursor.execute(
                            insert_query,
                            ChemAsso_insert
                            )

                        connection.commit()
                    # else:
                    #     # Entry already exists, skip
                    #     print("Entry already exists, skipping...")
            progress_bar.update(1)
    cursor.close()
