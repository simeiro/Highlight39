# Highlight39

## 概要
  Highlight39は https://vocadb.net/api/ を利用して現在のハイライトボカロ曲を自動送信してくれるDiscordのBotです。
  直近の全ての人気ボカロ曲が自動送信することは保証しません。
  
  デプロイはrailwayにて行いました。

## 使用方法

### １招待

以下のリンクから招待することができます

https://discord.com/api/oauth2/authorize?client_id=700404770548088933&permissions=76800&scope=bot


### 2招待後

招待後は**39!set**で自動送信登録を行うことができます。

登録が完了するとハイライト曲を自動で送信してくれるようになります。

送信を中止したい場合、**39!delete**で登録を削除することができます。

再設定する場合は**39!delete**→**39!set**の順で実行してください。



## コマンド

以下はコマンドの紹介です。接頭辞の39!は省略しています。（）はこのコマンドでも同じ内容が実行されることを意味しています。

**help**

コマンドの説明、リンクが送信されます。

**set**

実行するとサーバー、チャンネルの情報が登録され自動送信が開始されます。送信チャンネルを変更したい場合は一度**delete**を実行してから再度**set**してください。

**delete**

実行すると**set**で登録された情報が削除されます。つまり、自動送信がされなくなります。

**song (s)**

現在のハイライト曲を表示します。**song**後に数字を指定することで数字分の曲を表示します。(例.39!s 10) 数字の範囲は1~20です。数字指定がない場合は5曲分表示されます。APIのリクエスト過多を避けるため、1つのサーバーにつき**random**を含め1日5件までに制限しています。

**rand (r)**

ランダムにボカロ曲の情報を取得します。APIのリクエスト過多を避けるため、1つのサーバーにつき**song**を含め1日5件までに制限しています。
送信時のハイライトになっている曲idをランダムの数の上限にしています。


## 参考
以下の記事を参考にして制作しました。

discord.py - MongoDBをdiscord.pyで使う　https://zenn.dev/mnonamer/articles/f00eb4915d9c0a

RailwayでDiscord Botをホストしてみた　https://zenn.dev/mnonamer/articles/f73386390399f6


