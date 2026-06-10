# Gemini Enterprise app カスタムエージェント登録体験

## 始めましょう

AI エージェントを Gemini Enterprise app に登録し、利用するまでの流れを体験していきましょう。

**[開始]** ボタンをクリックして次のステップに進みます。

<walkthrough-tutorial-duration duration="30"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="1"></walkthrough-tutorial-difficulty>

## 1. プロジェクトの設定

ハンズオン実施対象のプロジェクトを選択してください。

<walkthrough-project-setup></walkthrough-project-setup>

## 2. CLI 初期設定 & API 有効化

選択した環境変数と、ハンズオンで利用するリージョンを環境変数として設定しておきます。

```bash
export GOOGLE_CLOUD_PROJECT=<walkthrough-project-id/>
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

[gcloud（Google Cloud の CLI ツール)](https://cloud.google.com/sdk/gcloud?hl=ja) のデフォルト プロジェクトを設定します。

```bash
gcloud config set project "${GOOGLE_CLOUD_PROJECT}"
```

[Vertex AI](https://cloud.google.com/vertex-ai?hl=ja) など、関連サービスを有効化し、利用できる状態にしましょう。

<walkthrough-enable-apis apis=
 "generativelanguage.googleapis.com,
  aiplatform.googleapis.com,
  iamcredentials.googleapis.com,
  cloudresourcemanager.googleapis.com">
</walkthrough-enable-apis>

## 3. 認証

みなさんの権限でアプリケーションを動作させられるよう、[デフォルト認証情報（ADC）](https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=ja) を作成します。表示される URL をブラウザの別タブで開き、認証コードをコピー、ターミナルにもどってきてそれを貼り付け、Enter を押してください。

```bash
gcloud auth application-default login --quiet
```

## 4. AI エージェントの確認

EC サイト AI エージェントです。[FakeStore API](https://fakestoreapi.com) を利用して、商品・カート・ユーザー情報を検索・照会します。

API を呼び出す関数ツールは <walkthrough-editor-select-line filePath="cloudshell_open/gemini-enterprise-handson/store/agent.py" startLine="20" endLine="20" startCharacterOffset="4" endCharacterOffset="100">agent.py の tools 行</walkthrough-editor-select-line> で設定していますが

呼ばれる <walkthrough-editor-open-file filePath="cloudshell_open/gemini-enterprise-handson/store/tools/store.py">関数そのもの</walkthrough-editor-open-file> は `requests` ライブラリで外部 API を呼び出すシンプルな実装です。

ADK は関数の引数やコメント情報を整理して LLM に渡し、どの関数をいつ、どんな引数で呼ぶかを考える手助けをしています。ADK は関数の返り値として **辞書型** を[推奨しています](https://adk.dev/tools-custom/function-tools/#return-type)が、例えば<walkthrough-editor-select-line filePath="cloudshell_open/gemini-enterprise-handson/store/tools/store.py" startLine="19" endLine="19" startCharacterOffset="8" endCharacterOffset="100">ここ</walkthrough-editor-select-line>では API 呼び出しが失敗したときに `{"status": "error"}` を返し、LLM に処理が失敗したことを伝えています。

## 5. ローカルでの AI エージェント起動

Python の仮想環境を作り

```bash
cd ~/cloudshell_open/gemini-enterprise-handson
uv venv && source .venv/bin/activate && uv sync
```

起動してみましょう。

```bash
adk web --allow_origins "*"
```

ターミナルに表示される `INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)` のリンクをクリックし、Web UI にアクセスしてください。

左上のコンボボックスで `store` を選択し、試しに以下のような質問をしてみましょう。

```txt
どんな商品カテゴリーがありますか？
```

カテゴリー一覧が返ってきましたか？続いて商品も検索してみましょう。

```txt
electronics カテゴリーの商品を 3 件教えてください
```

確認ができたらターミナルにもどり、`Ctrl + C` コマンドで起動中の Web サービスを停止しましょう。

## 6. AI エージェントのテスト

ADK では AI エージェントの評価を Trajectory（軌跡）と最終的な出力で行います。それぞれの閾値をテストの設定として <walkthrough-editor-open-file filePath="cloudshell_open/gemini-enterprise-handson/store/eval/data/test_config.json">このように</walkthrough-editor-open-file> 定義してみました。

- `tool_trajectory_avg_score`: どの関数をどの順序で、どんな引数で呼ぶのかがどれくらい期待と一致しているか
- `response_match_score`: 応答がどれくらい期待と一致しているか

テストを実行してみましょう。

```bash
adk eval store store/eval/data/eval_data1.evalset.json --config_file_path store/eval/data/test_config.json
```

うまくいけば `Tests passed: 2` となります。fail するようであれば `--print_detailed_results` オプションを有効にして再実行すると

```text
Eval Set Id: store_agent_accuracy
Eval Id: get_product_detail
Overall Eval Status: PASSED
---------------------------------------------------------------------
Metric: tool_trajectory_avg_score, Status: PASSED, Score: 1.0, Threshold: 1.0
---------------------------------------------------------------------
Metric: response_match_score, Status: PASSED, Score: 1.0, Threshold: 0.7
---------------------------------------------------------------------
```

など具体的な状況が確認できます。

## 7. Agent Runtime へのデプロイ

追加で必要となる環境変数を設定し、

```text
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_CLOUD_STORAGE_BUCKET=ai-agents-$(whoami)-$(date -u '+%Y%m%d%H%M%S')
```

一連のファイルをアップロードするためのオブジェクト ストレージを作成し

```bash
gcloud storage buckets create "gs://${GOOGLE_CLOUD_STORAGE_BUCKET}" --default-storage-class STANDARD --location "${GOOGLE_CLOUD_LOCATION}" --uniform-bucket-level-access
```

必要なサービスアカウントと権限を設定します。

```bash
gcloud beta services identity create --service "aiplatform.googleapis.com"
gcloud storage buckets add-iam-policy-binding "gs://${GOOGLE_CLOUD_STORAGE_BUCKET}" --member "serviceAccount:service-$( gcloud projects describe ${GOOGLE_CLOUD_PROJECT} --format 'get(projectNumber)' )@gcp-sa-aiplatform.iam.gserviceaccount.com" --role "roles/storage.objectViewer"
```

その上で、このアプリケーションを [Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime?hl=ja) へデプロイしてみましょう。

```bash
uv run -m deployment.deploy --create --location "${GOOGLE_CLOUD_LOCATION}"
```

5 分ほどかかります。デプロイがうまくいくと、最後のように以下のような出力があるはずです。

`Created remote agent: projects/123456789012/locations/us-central1/reasoningEngines/1234567890123456789`


## 8. Agent Runtime 上のエージェントへアクセス

ユーザーの ID と合わせて、環境変数に設定しましょう。

```bash
api_host="https://${GOOGLE_CLOUD_LOCATION}-aiplatform.googleapis.com"
api_endpoint="${api_host}/v1/projects/${GOOGLE_CLOUD_PROJECT}/locations/${GOOGLE_CLOUD_LOCATION}/reasoningEngines"
export AGENT_ENGINE_ID=$( curl -sX GET "${api_endpoint}" -H "Authorization: Bearer $(gcloud auth print-access-token)" | jq -r '.reasoningEngines[] | select(.displayName | contains("store_agent")) | .name' )
export USER_ID=test-user
```

以下のコマンドでデプロイしたアプリケーションに対話形式で接続してみましょう。

```bash
uv run -m deployment.test_deployment --resource_id "${AGENT_ENGINE_ID}" --user_id "${USER_ID}"
```

対話形式に入ったら、先ほどの質問をプロンプトとして渡してみましょう。

```text
electronics カテゴリーの商品を 3 件教えてください
```

終了するには `quit` と入力してください。セッションが削除され、会話が終了します。

```text
quit
```


## 9. API でのアクセス

ライブラリを使わず、直接 API でも接続してましょう。

セッションを作成し

```text
session=$( curl -sX POST "${api_endpoint}/"${AGENT_ENGINE_ID##*/}":query" -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-Type: application/json" -d '{"class_method": "async_create_session", "input": {"user_id": "test_user"}}' )
session_id=$( echo "${session}" | jq -r ".output.id")
echo "${session}" | jq .
```

それを利用して、エージェントにメッセージを送信し、結果を jq で取り出してみます。

```text
message_base='{"class_method": "async_stream_query", "input": {"user_id": "test_user", "message": "商品 ID が 1 の商品を教えてください"'
response=$( curl -sX POST "${api_endpoint}/"${AGENT_ENGINE_ID##*/}":streamQuery?alt=sse" -H "Authorization: Bearer $(gcloud auth print-access-token)" -H "Content-Type: application/json" -d "${message_base}, \"session_id\": \"${session_id}\"}}" )
echo "${response}" | jq -s ".[-1].content.parts"
```

結果が返ってきましたか？

Agent Runtime にデプロイされた ADK ベースのエージェントは API で会話できるため、どんなプログラミング言語でもこのエージェントに仕事を依頼するアプリケーションが作れます。

## 10. Gemini Enterprise app へ登録（その 1）

作ったエージェントは Gemini Enterprise app へ登録し、同僚たちに使ってもらいましょう。一時フォルダを作り、一般の方が作ってくれたツールをダウンロードします。

```bash
mkdir -p tmp && cd $_
git clone https://github.com/VeerMuchandi/agent_registration_tool.git
cd agent_registration_tool
```

[クラウドの管理コンソール](https://console.cloud.google.com/gen-app-builder/engines)で該当の Gemini Enterprise アプリを開き、URL から Gemini Enterprise の ID とロケーションを確認します。

例えば `https://console.cloud.google.com/gemini-enterprise/locations/<location>/engines/<gemini-enterprise-id>/overview/..` といった URL の中の

`<gemini-enterprise-id>` がその ID であり

```bash
gemini_enterprise_id=
```

`<location>` がロケーションです。

```bash
gemini_enterprise_location="global"
```

## 11. Gemini Enterprise app へ登録（その 2）

設定ファイルを `config.json` として用意して

```text
cat << EOF > config.json
{
    "project_id": "${GOOGLE_CLOUD_PROJECT}",
    "location": "${GOOGLE_CLOUD_LOCATION}",
    "re_resource_name": "${AGENT_ENGINE_ID}",
    "re_resource_id": "${AGENT_ENGINE_ID##*/}",
    "re_display_name": "store_agent",
    "app_id": "${gemini_enterprise_id}",
    "agent_id": "store-agent",
    "ars_display_name": "store_agent",
    "description": "EC サイトの商品・カート・ユーザー情報を検索・照会するエージェント",
    "tool_description": "This is an EC site agent that can search products, browse carts, and look up user information via the FakeStore API. Use the appropriate tool for each query rather than answering from intuition.",
    "adk_deployment_id": "${AGENT_ENGINE_ID##*/}",
    "auth_id": "",
    "icon_uri": "",
    "api_location": "${gemini_enterprise_location}",
    "re_location": "${GOOGLE_CLOUD_LOCATION}"
}
EOF
```

作られたファイルを <walkthrough-editor-open-file filePath="cloudshell_open/gemini-enterprise-handson/tmp/agent_registration_tool/config.json">エディタで開いて</walkthrough-editor-open-file> 確認してください。

`auth_id` と `icon_uri` 以外に  
空欄のフィールドはないでしょうか？  
**もし何かかけていたら、どこかの手順が抜けています。**

問題なさそうであれば、以下のコマンドで登録します。

```bash
python3 as_registry_client.py register_agent
```

## 12. Gemini Enterprise app での利用

初期セットアップで準備した Gemini Enterprise アプリケーションにユーザとしてアクセスします。

左のサイドメニューから `エージェント` 画面に行くと、いま登録したエージェントが表示されているはずです！実際に対話してみてください。

## これで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

これで `カスタムエージェントの体験` ハンズオンは終了です。

お疲れさまでした！
