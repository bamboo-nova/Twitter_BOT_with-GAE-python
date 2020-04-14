# Twitter_BOT_with-GAE-python
GAE/pythonを使ってTwitterBOTを作って見たよ

### 動かし方
config.pyにあるTWITTER_CREDENTIALSにTwitter developer APIを登録した時に出てきたconsumer keyとconsumer secretを入力する。
また、RIOT_APIを使ってLeague of Legendsのサモナーネームから直近の試合で参加していたサモナーを表示させる処理を実装しているので、RIOT_APIのkeyも必要

これらを入力した上で、`dev_appserver.py`を実行すれば起動する。バッチ処理(ツイッターBOT)を試したい場合は、/registration処理を行なった上で/launcherに遷移すれば機能を確認できる。
