import pandas as pd
import sqlite3


def show_table_columns(connection, table):

    query = f"PRAGMA table_info({table});"
    table_columns = simple_querry(
        connection,
        query
    )

    for item in table_columns:
        print(f"Column: {item[1]}, Type: {item[2]}")


def construct_db(
        db_name,
        overview_dict
        ):

    # Create a SQLite database connection
    conn = sqlite3.connect(db_name)

    for key in overview_dict:
        overview_dict[key].to_sql(
            key,
            conn,
            if_exists='replace',
            index=False)

    # Close the database connection
    conn.close()

    return "Done"


def submit_querry(
        query,
        connection
        ):

    try:
        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(query)

        # Fetch the column names
        column_names = [description[0] for description in cursor.description]

        # Fetch all the results
        results = cursor.fetchall()

        # Combine the column names with the query result
        # header = ','.join(column_names)

        # Close the cursor and the connection
        cursor.close()

        # Create a DataFrame from the results
        df = pd.DataFrame(results, columns=column_names)

        # Return the DataFrame
        return df

    except Exception as e:
        # Return the error message if an exception occurs
        error_message = str(e)
        df = pd.DataFrame({'Error': [error_message]})
        return df


def sql_prompt(question, stucture):
    header = "select appropriate table(s), write me a sql query to:\n"
    tail = " return sql query only."

    prompt = header + \
        question + " " + \
        "\n\n(context: the table structure is: " + \
        stucture + ")" + \
        tail

    return prompt


def simple_querry(connection, querry):
    cursor = connection.cursor()

    # Execute the SQL query
    cursor.execute(querry)

    # Fetch all the results
    results = cursor.fetchall()

    return results


def show_tables(connection):
    show_tables = "SELECT name\nFROM sqlite_master\nWHERE type = 'table'"
    tables = simple_querry(connection, show_tables)
    print(tables)
