import csv
import sql_utils as su
from tqdm.notebook import tqdm_notebook


def create_characterization_dt_tables(connection):

    CharacterizationInfo_str = "CREATE TABLE IF NOT EXISTS " + \
        "CharacterizationInfo " + \
        "(ID INT, CharType VARCHAR(150), CharName VARCHAR(150), " + \
        "AssayType VARCHAR(150), Protocol TEXT, " + \
        "DesignDescription TEXT, AnalysisAndConclusion TEXT);"

    CharExpConfig_str = "CREATE TABLE IF NOT EXISTS " + \
        "CharExpConfig " + \
        "(ID INT, CharType VARCHAR(150), CharName VARCHAR(150), " + \
        "AssayType VARCHAR(150), ExpConfigTechnique TEXT, " + \
        "ExpConfigInstruments TEXT, ExpConfigDescription TEXT);"

    CharResultDescriptions_str = "CREATE TABLE IF NOT EXISTS " + \
        "CharResultDescriptions " + \
        "(ID INT, CharType VARCHAR(150), CharName VARCHAR(150), " + \
        "AssayType VARCHAR(150), CharResultDescription TEXT);"

    CharResultKeywords_str = "CREATE TABLE IF NOT EXISTS " + \
        "CharResultKeywords " + \
        "(ID INT, CharType VARCHAR(150), CharName VARCHAR(150), " + \
        "AssayType VARCHAR(150), CharResultKeyword VARCHAR(150)); "

    CharResultTables_str = "CREATE TABLE IF NOT EXISTS " + \
        "CharResultTables " + \
        "(ID INT, CharType VARCHAR(150), CharName VARCHAR(150), " + \
        "AssayType VARCHAR(150), CharTable TEXT); "

    table_creation_querys = [
        CharacterizationInfo_str,
        CharExpConfig_str,
        CharResultDescriptions_str,
        CharResultKeywords_str,
        CharResultTables_str
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


def characterization_to_sql(
        characterization_dt,
        connection
):

    total_ids = len(characterization_dt)
    no_sample_list = []
    with tqdm_notebook(
        total=total_ids,
        desc='Processing',
        unit='ID'
    ) as progress_bar:
        cursor = connection.cursor()

        for ID in characterization_dt:
            sample_info = characterization_dt[ID]

            for CharType_info in sample_info:
                if 'type' not in CharType_info:
                    print('There is no characterization with your sample.')
                    no_sample_list.append([ID, CharType_info])
                    continue
                CharType = CharType_info['type']
                CharType_Info_Assay = CharType_info['charsByAssayType']
                for CharName in CharType_Info_Assay:
                    CharName_infos = CharType_Info_Assay[CharName]
                    for charname_info in CharName_infos:
                        displayableItems = charname_info['displayableItems']
                        # Create a cursor object
                        for item in displayableItems:
                            if item['name'] == 'Assay Type':
                                AssayType = item['value']

                            if item['name'] == 'Protocol':
                                Protocol = item['value']

                            if item['name'] == 'Design Description':
                                DesignDescription = item['value']

                            if item['name'] == 'Experiment Configurations':
                                exp_config_list = item['value']

                            if item['name'] == 'Characterization Results':
                                char_results = item['value']

                            if item['name'] == 'Analysis and Conclusion':
                                AnalysisAndConclusion = item['value']

                        n_row = len(exp_config_list[0]['Technique'])
                        for i in range(n_row):
                            ExpConfigTechnique = exp_config_list[
                                0
                            ]['Technique'][i]

                            ExpConfigInstruments = exp_config_list[
                                1
                            ]['Instruments'][i]

                            ExpConfigDescription = exp_config_list[
                                2
                            ]['Description'][i]

                            # Write to NanoEntDes
                            CharExpConfig_insert = (
                                ID,
                                CharType,
                                CharName,
                                AssayType,
                                ExpConfigTechnique,
                                ExpConfigInstruments,
                                ExpConfigDescription
                                )

                            # Execute a SELECT statement to check
                            # if the entry already exists

                            search_query = "SELECT COUNT(*) FROM " + \
                                "CharExpConfig" + \
                                " WHERE ID = ?" + \
                                " AND CharType = ?" + \
                                " AND CharName = ?" + \
                                " AND AssayType = ?" + \
                                " AND ExpConfigTechnique = ?" + \
                                " AND ExpConfigInstruments = ?;"

                            cursor.execute(
                                search_query,
                                CharExpConfig_insert[:6]
                            )
                            count = cursor.fetchone()[0]

                            # Check the count to determine
                            # if the entry exists
                            if count == 0:
                                # Entry does not exist, proceed
                                # with insertion
                                insert_query = "INSERT INTO " + \
                                    "CharExpConfig " + \
                                    "(ID, " + \
                                    "CharType, " + \
                                    "CharName, " + \
                                    "AssayType, " + \
                                    "ExpConfigTechnique, " + \
                                    "ExpConfigInstruments, " + \
                                    "ExpConfigDescription) " + \
                                    "VALUES (?, ?, ?, ?, ?, ?, ?)"
                                cursor.execute(
                                    insert_query,
                                    CharExpConfig_insert
                                )
                                connection.commit()

                        for char_result in char_results:
                            if 'Data and Conditions' in char_result:
                                table_list = char_result[
                                    'Data and Conditions'
                                ]
                                CharTable = ""
                                for item in table_list:
                                    tsc = ",".join(
                                        item[
                                            'value'
                                        ]
                                    )
                                    CharTable += tsc
                                    CharTable += ";"
                                    # Write to NanoEntDes
                                    CRTables_insert = (
                                        ID,
                                        CharType,
                                        CharName,
                                        AssayType,
                                        CharTable
                                        )

                                    # Execute a SELECT
                                    # statement to check
                                    # if the entry already exists

                                    search_query = "SELECT " + \
                                        "COUNT(*) FROM " + \
                                        "CharResultTables" + \
                                        " WHERE ID = ?" + \
                                        " AND CharType = ?" + \
                                        " AND CharName = ?" + \
                                        " AND AssayType = ?;"

                                    cursor.execute(
                                        search_query,
                                        CRTables_insert[:4]
                                    )
                                    count = cursor.fetchone()[0]

                                    # Check the count to determine
                                    # if the entry exists
                                    if count == 0:
                                        # Entry does not exist, proceed
                                        # with insertion
                                        insert_query = "INSERT " + \
                                            "INTO " + \
                                            "CharResultTables " + \
                                            "(ID, " + \
                                            "CharType, " + \
                                            "CharName, " + \
                                            "AssayType, " + \
                                            "CharTable) " + \
                                            "VALUES (?, ?, ?, ?, ?)"
                                        cursor.execute(
                                            insert_query,
                                            CRTables_insert
                                        )
                                        connection.commit()
                            if 'Files' in char_result:
                                file_list = char_result[
                                    'Files'
                                ]

                                for char_file in file_list:
                                    if 'description' in char_file:
                                        CRDes = char_file[
                                            'description'
                                        ]
                                    else:
                                        CRDes = "None"

                                    if 'keywordsString' in char_file:
                                        CRKWstr_ls = char_file[
                                            'keywordsString'
                                        ].split(",")
                                    else:
                                        CRKWstr_ls = list("None")

                                    CRDes_insert = (
                                        ID,
                                        CharType,
                                        CharName,
                                        AssayType,
                                        CRDes
                                        )

                                    # Execute a SELECT
                                    # statement to check
                                    # if the entry already exists

                                    search_query = "SELECT " + \
                                        "COUNT(*) FROM " + \
                                        "CharResultDescriptions" + \
                                        " WHERE ID = ?" + \
                                        " AND CharType = ?" + \
                                        " AND CharName = ?" + \
                                        " AND AssayType = ?;"

                                    cursor.execute(
                                        search_query,
                                        CRDes_insert[:4]
                                    )
                                    count = cursor.fetchone()[0]

                                    # Check the count to determine
                                    # if the entry exists
                                    if count == 0:
                                        # Entry does not exist, proceed
                                        # with insertion
                                        insert_query = "INSERT " + \
                                            "INTO " + \
                                            "CharResultDescriptions" +\
                                            " (ID, " + \
                                            "CharType, " + \
                                            "CharName, " + \
                                            "AssayType, " + \
                                            "CharResultDescription" + \
                                            ") " + \
                                            "VALUES (?, ?, ?, ?, ?)"

                                        cursor.execute(
                                            insert_query,
                                            CRDes_insert
                                        )
                                        connection.commit()

                                    for CRKW in CRKWstr_ls:
                                        CRKW_insert = (
                                            ID,
                                            CharType,
                                            CharName,
                                            AssayType,
                                            CRKW
                                        )

                                        # Execute a SELECT
                                        # statement to check
                                        # if the entry already exists

                                        search_query = "SELECT " + \
                                            "COUNT(*) FROM " + \
                                            "CharResultKeywords" + \
                                            " WHERE ID = ?" + \
                                            " AND CharType = ?" + \
                                            " AND CharName = ?" + \
                                            " AND AssayType = ?" + \
                                            " AND " + \
                                            "CharResultKeyword = ?;"

                                        cursor.execute(
                                            search_query,
                                            CRKW_insert
                                        )
                                        count = cursor.fetchone()[0]

                                        # Check the count to determine
                                        # if the entry exists
                                        if count == 0:
                                            # Entry does not exist,
                                            # proceed
                                            # with insertion
                                            insert_query = "INSERT " +\
                                                "INTO " + \
                                                "CharResultKeywords" +\
                                                " (ID, " + \
                                                "CharType, " + \
                                                "CharName, " + \
                                                "AssayType, " + \
                                                "CharResultKeyword" + \
                                                ") " + \
                                                "VALUES (?, ?, " + \
                                                "?, ?, ?)"

                                            cursor.execute(
                                                insert_query,
                                                CRKW_insert
                                            )
                                            connection.commit()

                        # Write to NanoEntDes
                        CharacterizationInfo_insert = (
                            ID,
                            CharType,
                            CharName,
                            AssayType,
                            Protocol,
                            DesignDescription,
                            AnalysisAndConclusion
                            )

                        # Execute a SELECT statement to check
                        # if the entry already exists

                        search_query = "SELECT COUNT(*) FROM " + \
                            "CharacterizationInfo" + \
                            " WHERE ID = ?" + \
                            " AND CharType = ?" + \
                            " AND CharName = ?" + \
                            " AND AssayType = ?" + \
                            " AND Protocol = ?;"

                        cursor.execute(
                            search_query,
                            CharacterizationInfo_insert[:5]
                        )
                        count = cursor.fetchone()[0]

                        # Check the count to determine if the entry exists
                        if count == 0:
                            # Entry does not exist, proceed with insertion
                            insert_query = "INSERT INTO " + \
                                "CharacterizationInfo " + \
                                "(ID, " + \
                                "CharType, " + \
                                "CharName, " + \
                                "AssayType, " + \
                                "Protocol, " + \
                                "DesignDescription, " + \
                                "AnalysisAndConclusion) " + \
                                "VALUES (?, ?, ?, ?, ?, ?, ?)"
                            cursor.execute(
                                insert_query,
                                CharacterizationInfo_insert
                            )
                            connection.commit()
            progress_bar.update(1)
    cursor.close()
    no_sample_csv = 'no_characterization.csv'
    # Specify the filename for the CSV file

    with open(no_sample_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(no_sample_list)

    print(f"CSV file '{no_sample_csv}' has been created.")
