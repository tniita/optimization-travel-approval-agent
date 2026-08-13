# 基本的なホステッドエージェント（Responses プロトコル）

**Responses プロトコル**を使って Microsoft Foundry 上でホストされる、最小構成の [Agent Framework](https://github.com/microsoft/agent-framework) エージェントです。基本的なリクエスト/レスポンスのやりとりと、マルチターン会話をデモします。

## 仕組み

このエージェントは Agent Framework の `FoundryChatClient` を使用し、`ResponsesHostServer` 経由で提供されます。`ResponsesHostServer` は OpenAI Responses プロトコル互換の REST API を公開します。実装は [main.py](main.py) を参照してください。

## 方法 1: Azure Developer CLI (`azd`)

### 前提条件

1. **Azure Developer CLI (`azd`)** — [azd をインストールする](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd)
2. AI エージェント拡張機能をインストール:
   ```bash
   azd ext install azure.ai.agents
   ```
3. 認証:
   ```bash
   azd auth login
   ```

### エージェントプロジェクトを初期化する

クローンは不要です。新しいフォルダーを作成し、マニフェストから初期化します:

```bash
mkdir my-basic-agent && cd my-basic-agent

azd ai agent init -m https://github.com/microsoft-foundry/foundry-samples/blob/main/samples/python/hosted-agents/agent-framework/responses/01-basic/agent.manifest.yaml
```

プロンプトに従って Foundry プロジェクトとモデルデプロイを設定します。既存の Foundry プロジェクトがない場合でも、`azd ai agent init` が作成手順を案内してくれます。

### Azure リソースをプロビジョニングする（必要な場合）

Foundry プロジェクトとモデルデプロイがまだない場合:

```bash
azd provision
```

### ローカルでエージェントを実行する

```bash
azd ai agent run
```

エージェントホストが `http://localhost:8088` で起動します。

### ローカルエージェントを呼び出す

別のターミナルで、プロジェクトディレクトリから実行します:

```bash
azd ai agent invoke --local "Hi"
```

### Foundry にデプロイする

ローカルでの動作確認ができたら、Microsoft Foundry にデプロイします:

```bash
azd deploy
```

デプロイの完全なガイドは [ホステッドエージェントをデプロイする](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent) を参照してください。

### デプロイ済みエージェントを呼び出す

```bash
azd ai agent invoke "Hi"
```

## 方法 2: VS Code（Foundry Toolkit）

### 前提条件

1. **[Foundry Toolkit](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.azure-ai-foundry)** 拡張機能をインストールした **VS Code**。
2. VS Code で Azure にサインインしておくこと。

### プロジェクトを作成する

1. コマンドパレット (`Ctrl+Shift+P`) を開き、**Foundry Toolkit: Create Hosted Agent** を実行します。
2. ギャラリーからこのサンプルを選択します。拡張機能が新しいワークスペースにプロジェクトをスキャフォールドし、`agent.yaml`、`.env`、`.vscode/tasks.json` + `launch.json` を自動生成します。
3. **Foundry Project Setup** を完了して、サブスクリプションと Foundry プロジェクトを選択します（新規作成も可）。

### エージェントを実行・デバッグする

**F5** を押すとデバッグモードでエージェントが起動します。エージェントホストは `http://localhost:8088` で起動します。

### Agent Inspector でテストする

1. コマンドパレット (`Ctrl+Shift+P`) を開き、**Foundry Toolkit: Open Agent Inspector** を実行します。
2. Inspector が実行中のエージェントに接続します。メッセージを送信して、ストリーミングされる応答を確認できます。

### Foundry にデプロイする

1. コマンドパレット (`Ctrl+Shift+P`) を開き、**Foundry Toolkit: Deploy Hosted Agent** を実行します。拡張機能が **Deploy Hosted Agent** ウィザードを開き、`agent.yaml` を読んで設定を自動入力します。
2. 求められたら **Foundry Project Setup** を完了し、サブスクリプションとプロジェクトを選択します。
3. **Basics** タブでデプロイ方式（**Code** または **Container**）を選び、エージェント名を確認します。
4. **Review + Deploy** でランタイムの詳細を確認し、**CPU and Memory** サイズを選んで **Deploy** をクリックします。
5. デプロイ後は Agent Playground でエージェントを呼び出し、**Logs** タブからライブログをストリーミングできます。

## 次のステップ

- [クイックスタート: ホステッドエージェントを作成する](https://learn.microsoft.com/en-us/azure/foundry/agents/quickstarts/quickstart-hosted-agent) — `azd` を使ったエンドツーエンドの解説
- [ツールカタログ](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog) — エージェントを拡張するツール一覧（Bing Search、Azure AI Search、ファイル検索、コードインタープリターなど）
- [ホステッドエージェントを管理する](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/manage-hosted-agent) — デプロイ済みエージェントの監視と管理
- [エージェントにツールを追加する](../02-tools/) — ローカルツール関数のサンプル
- [MCP サーバーに接続する](../03-mcp/) — リモート MCP ツールプロバイダーを使うサンプル
- [Foundry Toolbox を使う](../04-foundry-toolbox/) — Azure Foundry Toolbox 連携のサンプル
