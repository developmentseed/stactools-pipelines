import logging
import time


def run_query(
    client, output_location: str, database_name: str, query: str, s3_output: str
) -> None:
    """Generic function to run athena query and ensures it is successfully completed

    Parameters
    ----------
    query : str
        formatted string containing athena sql query
    s3_output : str
        query output path
    """
    start_response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": database_name},
        ResultConfiguration={
            "OutputLocation": output_location,
        },
    )
    query_id = start_response["QueryExecutionId"]

    while True:
        state = client.get_query_execution(QueryExecutionId=query_id)["QueryExecution"][
            "Status"
        ]["State"]
        if state == "RUNNING" or state == "QUEUED":
            time.sleep(10)
        else:
            break

    assert state == "SUCCEEDED", f"query state is {state}"
    logging.info(f"Query {query_id} complete")


def build_create_table_query(inventory_location: str):
    query = f"""
        CREATE EXTERNAL TABLE inventory(
             bucket string,
             key string,
             version_id string,
             is_latest boolean,
             is_delete_marker boolean,
             size string,
             last_modified_date string,
             e_tag string,
             storage_class string,
             is_multipart_uploaded boolean,
             replication_status string,
             encryption_status string,
             object_lock_retain_until_date string,
             object_lock_mode string,
             object_lock_legal_hold_status string,
             intelligent_tiering_access_tier string,
             bucket_key_status string,
             checksum_algorithm string
        )
        ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
        STORED AS INPUTFORMAT 'org.apache.hadoop.hive.ql.io.SymlinkTextInputFormat'
        OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat'
        LOCATION '{inventory_location}'
        """
    return query
