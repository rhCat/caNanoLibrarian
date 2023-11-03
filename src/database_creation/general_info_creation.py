import sql_utils as su
from tqdm.notebook import tqdm_notebook
import datetime


def create_general_info_tables(connection):

    general_info_string = "CREATE TABLE IF NOT EXISTS GeneralInfo " + \
            "(ID INT, sampleName VARCHAR(150), " + \
            "createdYear INT, createdMonth INT);"

    keyword_info_string = "CREATE TABLE IF NOT EXISTS " + \
        "SampleKeyWords (ID INT, sampleName VARCHAR(150), " + \
        "SampleKeyWord VARCHAR(150));"

    table_creation_querys = [
        general_info_string,
        keyword_info_string
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


def general_info_to_sql(
        contact_dt,
        connection
):

    total_ids = len(contact_dt)

    with tqdm_notebook(
        total=total_ids,
        desc='Processing',
        unit='ID'
    ) as progress_bar:

        # Create a cursor object
        cursor = connection.cursor()

        for ID in contact_dt:
            sample_info = contact_dt[ID]

            datetime_obj = datetime.datetime.fromtimestamp(
                sample_info['createdDate'] / 1000
                )

            year = datetime_obj.year
            month = datetime_obj.month

            # Write to NanoEntCom
            GeneralInfo_insert = (
                ID,
                sample_info['sampleName'],
                year,
                month
                )

            # Execute a SELECT statement to check
            # if the entry already exists
            search_query = "SELECT COUNT(*) " + \
                "FROM GeneralInfo WHERE " + \
                "ID = ? AND sampleName = ? " + \
                "AND createdYear = ? AND createdMonth = ?;"

            cursor.execute(search_query, GeneralInfo_insert)
            count = cursor.fetchone()[0]

            # Check the count to determine if the entry exists
            if count == 0:
                # Entry does not exist, proceed with insertion
                insert_query = "INSERT INTO GeneralInfo (" + \
                    "ID, " + \
                    "sampleName, " + \
                    "createdYear, " + \
                    "createdMonth) " + \
                    "VALUES (?, ?, ?, ?)"

                cursor.execute(
                    insert_query,
                    GeneralInfo_insert
                    )

                connection.commit()

            if sample_info['keywords'] and '<br />' in sample_info['keywords']:
                keyword_list = sample_info['keywords'].split("<br />")
            else:
                if sample_info['keywords']:
                    keyword_list = [sample_info['keywords']]
                else:
                    keyword_list = ["None"]

            for keyword in keyword_list:
                # Write to NanoEntCom
                keyword_insert = (
                    ID,
                    sample_info['sampleName'],
                    keyword
                    )

                # Execute a SELECT statement to check
                # if the entry already exists
                search_query = "SELECT COUNT(*) " + \
                    "FROM SampleKeyWords WHERE " + \
                    "ID = ? AND sampleName = ? " + \
                    "AND SampleKeyWord = ?;"

                cursor.execute(search_query, keyword_insert)
                count = cursor.fetchone()[0]

                # Check the count to determine if the entry exists
                if count == 0:
                    # Entry does not exist, proceed with insertion
                    insert_query = "INSERT INTO SampleKeyWords (" + \
                        "ID, " + \
                        "sampleName, " + \
                        "SampleKeyWord) " + \
                        "VALUES (?, ?, ?)"

                    cursor.execute(
                        insert_query,
                        keyword_insert
                        )

            progress_bar.update(1)
    cursor.close()
