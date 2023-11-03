import sql_utils as su
from tqdm.notebook import tqdm_notebook
import re


def create_Publication_Info_tables(connection):

    general_info_string = "CREATE TABLE IF NOT EXISTS PublicationInfo " + \
            "(ID INT, PMID INT, year INT, " + \
            "title TEXT, author TEXT, journal TEXT, " + \
            "publicationCategories TEXT, description TEXT);"

    keyword_info_string = "CREATE TABLE IF NOT EXISTS " + \
        "PublicationKeyWords (ID INT, PublicationKeyWord VARCHAR(150));"

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


def publication_info_to_sql(
        publication_dt,
        connection
):

    total_ids = len(publication_dt)

    def extract_information(string):
        pattern = r"(.*?)\.\s*(\d{4});.*?PMID:\s*(\d+)"
        match = re.search(pattern, string)

        if match:
            publication = match.group(1).strip()
            year = match.group(2).strip()
            pmid = match.group(3)

            pub_list = publication.split(".")
            if len(pub_list) <= 2:
                if "," not in pub_list[0]:
                    year_match = re.search(r'\b(\d{4})\b', string)
                    year = year_match.group(1)

                    # Extracting the journal name
                    journal_match = re.search(r'\. (.+?)\.', string)
                    journal = journal_match.group(1)

                    # Extracting the PMID
                    pmid_match = re.search(r'PMID: (\d+)', string)
                    pmid = pmid_match.group(1)

                    title_match = re.search(r'^([^\.]+)\.', string)
                    title = title_match.group(1).strip()

                    return {
                        'journal': journal,
                        'pmid': pmid,
                        'year': year,
                        'title': title,
                        'author': "None"
                    }
                else:
                    print(pub_list)
            else:
                return {
                    'journal': pub_list[2].strip(),
                    'pmid': pmid,
                    'year': year,
                    'title': pub_list[1].strip(),
                    'author': pub_list[0].strip()
                    }

        return {
            'journal': "None",
            'pmid': "None",
            'year': "None",
            'title': "None",
            'author': "None"
            }

    with tqdm_notebook(
        total=total_ids,
        desc='Processing',
        unit='ID'
    ) as progress_bar:

        # Create a cursor object
        cursor = connection.cursor()

        for ID in publication_dt:
            sample_info = publication_dt[ID]

            for category in sample_info['category2Publications']:
                info_dict = sample_info['category2Publications'][category]
                for info in info_dict:

                    citation_string = info['displayName']

                    article_info = extract_information(citation_string)

                    # Write to NanoEntCom
                    publication_insert = (
                        ID,
                        article_info['pmid'],
                        article_info['year'],
                        article_info['title'],
                        article_info['author'],
                        article_info['journal'],
                        category,
                        info['description']
                        )

                    # Execute a SELECT statement to check
                    # if the entry already exists
                    search_query = "SELECT COUNT(*) " + \
                        "FROM PublicationInfo  WHERE " + \
                        "ID = ? AND PMID  = ? AND year  = ? AND " + \
                        "title  = ? AND author  = ? AND journal  = ? AND " + \
                        "publicationCategories  = ? AND description  = ?;"

                    cursor.execute(search_query, publication_insert)
                    count = cursor.fetchone()[0]

                    # Check the count to determine if the entry exists
                    if count == 0:
                        # Entry does not exist, proceed with insertion
                        insert_query = "INSERT INTO PublicationInfo (" + \
                            "ID, " + \
                            "PMID, " + \
                            "year, " + \
                            "title, " + \
                            "author, " + \
                            "journal, " + \
                            "publicationCategories, " + \
                            "description) " + \
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

                        cursor.execute(
                            insert_query,
                            publication_insert
                            )

                        connection.commit()

                    if info[
                            'keywordsDisplayName'
                        ] and '<br />' in info[
                            'keywordsDisplayName'
                    ]:
                        keyword_list = info[
                            'keywordsDisplayName'
                            ].split("<br />")
                    else:
                        if info['keywordsDisplayName']:
                            keyword_list = [info['keywordsDisplayName']]
                        else:
                            keyword_list = ["None"]

                    for keyword in keyword_list:
                        # Write to NanoEntCom
                        keyword_insert = (
                            ID,
                            keyword
                            )

                        # Execute a SELECT statement to check
                        # if the entry already exists
                        search_query = "SELECT COUNT(*) " + \
                            "FROM PublicationKeyWords WHERE " + \
                            "ID = ? AND PublicationKeyWord  = ?;"

                        cursor.execute(search_query, keyword_insert)
                        count = cursor.fetchone()[0]

                        # Check the count to determine if the entry exists
                        if count == 0:
                            # Entry does not exist, proceed with insertion
                            insert_query = "INSERT INTO " + \
                                "PublicationKeyWords (" + \
                                "ID, " + \
                                "PublicationKeyWord ) " + \
                                "VALUES (?, ?)"

                            cursor.execute(
                                insert_query,
                                keyword_insert
                                )

            progress_bar.update(1)
    cursor.close()
