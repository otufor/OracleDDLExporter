
# Oracle DDL Exporter

このPythonスクリプトは、Oracleデータベースに接続し、テーブル、ビュー、パッケージなどのデータベースオブジェクトのDDL（データ定義言語）スクリプトをエクスポートするために設計されています。スクリプトは設定をTOMLファイルから読み込み、Oracleデータベースに接続して指定されたオブジェクトのDDLを取得し、スキーマとオブジェクトタイプ別に整理されたSQLファイルに書き込みます。

## 必要条件

- Python 3.x
- Oracle Instant Client

## 仮想環境での作業 (Windows)

### 仮想環境のセットアップ

1. プロジェクトディレクトリで、以下のコマンドを実行してPythonの仮想環境を作成します：

   ```cmd
   py -m venv .venv
   ```

2. 作成した仮想環境をアクティベートします：

   ```cmd
   .\.venv\Scripts\activate
   ```

### 依存関係のインストール

仮想環境がアクティベートされた状態で、以下のコマンドを実行してプロジェクトの依存関係をインストールします：

- **Poetryを使用する場合**:
  ```cmd
  poetry install
  ```

- **Pipを使用する場合**:
  ```cmd
  pip install .
  ```

### スクリプトの実行

仮想環境内で、以下のコマンドで `ddl_export.py` スクリプトを実行します：

```cmd
py ddl_export.py
```

## 設定

スクリプトを実行する前に、以下の構造で `config.toml` ファイルを設定する必要があります：

```toml
[client]
instant_client_path = "インスタントクライアントへのパス"

[database]
host = "データベースホスト"
port = "ポート"
service_name = "サービス名"
user = "ユーザー名"
password = "パスワード"

[extraction]
schema = "対象のスキーマ"
object_types = ["TABLE", "VIEW", "PACKAGE", "PACKAGE BODY", ...]
```

## 出力

出力は、スキーマ名の下でオブジェクトタイプ別に整理されたディレクトリ内のSQLファイルです。例えば：

```
schema_name/
│
├── TABLE/
│   └── table_name.sql
├── VIEW/
│   └── view_name.sql
...
```

各 `.sql` ファイルには、対応するデータベースオブジェクトのDDLスクリプトが含まれます。
