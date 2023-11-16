import os
import toml
import oracledb
from tqdm import tqdm
from typing import Any, Dict, Optional

def load_config(path: str) -> Dict[str, Any]:
    """TOML設定ファイルを読み込み、内容を辞書で返す。

    Args:
        path (str): 設定ファイルのパス。

    Returns:
        Dict[str, Any]: 設定ファイルの内容を含む辞書。
    """
    return toml.load(path)

def make_directory(path: str) -> None:
    """指定されたパスにディレクトリが存在しない場合、ディレクトリを作成する。

    Args:
        path (str): 作成するディレクトリのパス。
    """
    if not os.path.exists(path):
        os.makedirs(path)

def get_ddl(connection: oracledb.Connection, object_type: str, name: str, schema: str) -> Optional[str]:
    """指定されたオブジェクトタイプ、名前、スキーマに基づいてDDLを取得する。

    Args:
        connection (oracledb.Connection): Oracleデータベースへの接続。
        object_type (str): オブジェクトのタイプ（例: TABLE, VIEW）。
        name (str): オブジェクトの名前。
        schema (str): オブジェクトが存在するスキーマ。

    Returns:
        Optional[str]: DDL文字列、またはDDLが存在しない場合はNone。

    Raises:
        oracledb.Error: DDLの取得中にOracleデータベースエラーが発生した場合。
    """
    with connection.cursor() as cursor:
        ddl_query = """
            SELECT DBMS_METADATA.GET_DDL(:1, :2, :3) FROM DUAL
        """
        try:
            cursor.execute(ddl_query, [object_type, name, schema])
            ddl_result = cursor.fetchone()
        except oracledb.Error as e:
            print(f"Error getting DDL for {object_type} {name}: {e}")
        if not ddl_result:
            return None
        # LOBはread()でstrに変換
        if isinstance(ddl_result[0], oracledb.LOB):
            return ddl_result[0].read().strip() 
        else:
            return ddl_result[0].strip()

def write_to_file(directory: str, filename: str, ddl: str) -> None:
    """指定されたディレクトリに、指定されたファイル名でDDLを書き込む。

    Args:
        directory (str): DDLを書き込むディレクトリ。
        filename (str): 作成するファイルの名前。
        ddl (str): 書き込むDDL文字列。
    """
    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(ddl)
        print(f"Written: {file_path}")

def fetch_and_write_ddls(connection: oracledb.Connection, schema: str, object_types: list[str], output_directory: str) -> None:
    """指定されたスキーマとオブジェクトタイプに基づいてDDLをフェッチし、ファイルに書き込む。

    Args:
        connection (oracledb.Connection): Oracleデータベースへの接続。
        schema (str): 対象のスキーマ名。
        object_types (list[str]): 対象のオブジェクトタイプのリスト。
    """
    placeholder = ', '.join([f':object_types_{i+1}' for i in range(len(object_types))])
    query = f"""
        SELECT object_name, object_type
        FROM all_objects
        WHERE owner = :schema AND object_type IN ({placeholder}) AND status = 'VALID'
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [schema, *object_types])
        objects = list(cursor)

    for object_name, object_type in tqdm(objects, desc="Extracting", unit="file"):
        ddl_type = "PACKAGE_BODY" if object_type == "PACKAGE BODY" else object_type
        ddl = get_ddl(connection, ddl_type, object_name, schema)
        if ddl:
            directory = os.path.join(output_directory, schema, ddl_type)
            make_directory(directory)
            filename = f"{object_name}.sql"
            write_to_file(directory, filename, ddl)

def main() -> None:
    """メイン実行関数。設定を読み込み、データベース接続を行い、DDLを抽出してファイルに書き込む。"""
    config = load_config('config.toml')
    oracledb.init_oracle_client(lib_dir=config['client']['instant_client_path'])

    db_config = config['database']
    dsn = oracledb.makedsn(db_config['host'], db_config['port'], service_name=db_config['service_name'])
    extraction_config = config['extraction']
    
    db_user = db_config['user']
    db_password = db_config['password']
    db_encoding = "UTF-8"
    object_types = extraction_config['object_types']
    schema = extraction_config['schema']

    output_directory = config['output']['directory']
    
    with oracledb.connect(user=db_user, password=db_password, dsn=dsn, encoding=db_encoding) as connection:
        fetch_and_write_ddls(connection, schema, object_types, output_directory)

if __name__ == "__main__":
    main()
