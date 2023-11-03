import data_utils as du
import nanomaterial_entity_creation as nec
import functionalizing_entity_creation as fec
import chemical_association_creation as cac
import general_info_creation as gic
import publication_info_creation as pic
import characterization_info_creation as cic
import sqlite3


def SQLdb_creation(
    db_name,
    sample_search_df,
    overview_data_path,
    sample_list,
    connection,
    re_parse=False
):
    """
    Please note that this portion of the script is to
    show how the database was created from the existing pulic
    data download from caNanoLab and for the community
    to inspect of any misconfiguration in the setup
    of the backing database for the caNanoLibrarian App.
    This is not intended to encourage public to ramp
    downloading request to caNanoLab, please use the database
    responsibly. Thank you.
    """
    table_names = []
    table_schemas = []
    resulting_schema_dict = {}

    if re_parse:
        overview_dict, table_structure = du.parse_overview_raw_data(
            sample_search_df,
            overview_data_path,
            re_parse_overview=False
            )

        composition_dt = {}
        characterization_dt = {}
        publication_dt = {}
        contact_dt = {}
        for sample in sample_list:
            sampleID = str(sample['sampleID'])
            composition_dt[sampleID] = sample['composition']
            characterization_dt[sampleID] = sample['characterization']
            publication_dt[sampleID] = sample['publication']
            contact_dt[sampleID] = sample['contact']

        connection = sqlite3.connect(db_name)

        print("Writing GeneralInfo...")
        gic.create_general_info_tables(connection)
        gic.general_info_to_sql(contact_dt, connection)

        print("Writing NanoMaterialEntity...")
        nec.create_nanomaterial_entity_tables(connection)
        nec.nanomaterialentity_to_sql(composition_dt, connection)

        print("Writing FunctionalizingEntity...")
        fec.create_functionalizing_entity_tables(connection)
        fec.functionalizingentity_to_sql(composition_dt, connection)

        print("Writing ChemicalAssociation...")
        cac.create_ChemAsso_tables(connection)
        cac.chemicalassociation_to_sql(composition_dt, connection)

        print("Writing Characteriztion...")
        cic.create_characterization_dt_tables(connection)
        cic.characterization_to_sql(characterization_dt, connection)

        print("Writing Publication...")
        pic.create_Publication_Info_tables(connection)
        pic.publication_info_to_sql(publication_dt, connection)

        print("Done!")
    else:
        cursor = connection.cursor()
        # Get the list of tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # Print the schema of each table
        for table in tables:
            table_name = table[0]
            table_names.append(table_name)
            # print(f"Table: {table_name}")
            # print("Schema:")
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()
            current_schema = []
            for column in schema:
                current_schema.append(f"{column[1]}: {column[2]}")
            table_schemas.append(current_schema)
            resulting_schema_dict[table_name] = current_schema

        # Close the cursor and the database connection
        cursor.close()

    return resulting_schema_dict
