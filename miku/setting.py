import os
# from dotenv import load_dotenv
from motor import motor_asyncio as motor

# load_dotenv()
TOKEN = os.environ["TOKEN"]
OWNER_ID = os.environ["OWNER_ID"]
dbclient = motor.AsyncIOMotorClient(os.environ["DB_CLIENT"])
db = dbclient["39-bot"]
guilds_collection = db["guilds"]
songs_collection = db["songs"]

description = """__コマンド一覧__

**39!set**
送信するチャンネルを設定します。

**39!delete**
設定した情報を削除します。

**39!song**
39!sでも可。現在のハイライト曲を送信します。39!s 10 のように数字を指定するとその曲数分表示されます。

**39!rand**
39!rでも可。ランダムで曲情報を送信します。

__リンク__

[**vocaDB**](https://vocadb.net)
[**コード、詳しい仕様解説**](https://github.com/simeiro/HighlightMIKU)
[**僕**](https://twitter.com/simeir0)
"""
invite_msg = """Botの追加ありがとうございます\n
            私は <https://vocadb.net/api/> を使用し、ボカロハイライト曲を自動送信します
            39!set から自動送信の登録を行うことができます
            わからないことがあれば 39!help を使用してください
            また、こちらのサイトも是非活用してより良いボカロライフを送ってください
            https://vocadb.net/"""
