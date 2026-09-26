# 出張承認エージェント — 最適化サイクル用サンプル

架空の会社 **Contoso Ltd.** の出張申請をレビューする、Microsoft Foundry のホステッドエージェントです。[Agent Framework](https://github.com/microsoft/agent-framework) と Responses プロトコルを使用し、評価・最適化の前後で応答の品質を比較するためのサンプルになっています。

## 初めて動かす場合

**セットアップ・デプロイ・評価・最適化の手順は、[リポジトリルートの README](../../README.md) にまとめています。**

| 状況 | 進む場所 |
|---|---|
| まだ環境を準備していない | [前提条件・リポジトリの取得](../../README.md#2-前提条件) |
| ツールとリポジトリは準備済み | [デプロイ手順（新規／既存プロジェクトを選択）](../../README.md#エージェントをホステッドエージェントとしてデプロイする) |
| このサンプルをデプロイ・動作確認済みで、azd 環境も設定済み | [Step 1 — 評価スイートを生成する](../../README.md#3-step-1--評価スイートを生成する) |

コマンドは、このフォルダーではなく **`azure.yaml` があるリポジトリルート**から実行します。別のサンプルを `azd ai agent init` で初期化する必要はありません。Azure 上で動かすため、モデル推論とホステッドエージェントの実行に利用料金が発生します。

## エージェントが行うこと

たとえば「3 日間の東京出張で、航空券とホテルが合計 2,800 ドル。承認できるか」という申請に対して、旅費規程・部門予算・代替案を確認して応答します。不足情報があれば、判断の前に追加情報を求めることもあります。

| ツール | 返す情報 |
|---|---|
| `lookup_travel_policy` | 金額ごとの承認レベル、宿泊費の上限、航空券の条件、事前予約日数 |
| `check_department_budget` | Engineering 部門の予算総額と残額 |
| `get_flight_alternatives` | 日程変更や近隣空港の利用による節約案 |

**これらのツールは固定のサンプルデータを返すだけです。** 外部の予約サービスや実際の社内システムには接続せず、出張の承認記録・航空券の予約・予算更新も行いません。本番業務の承認システムではなく、応答の評価・改善を学ぶための実装です。

## 仕組み

[main.py](main.py) は `load_config()` で最適化用の構成を読み込み、指示・スキル・ツールの説明・モデルをエージェントに反映します。通常は `.agent_configs/baseline/` を使い、候補の適用後は `OPTIMIZATION_CANDIDATE_ID` で指定した構成を使います。

モデル呼び出しには `FoundryChatClient`、API の公開には OpenAI Responses プロトコル互換の `ResponsesHostServer` を使用します。

| ファイル | 役割 |
|---|---|
| [main.py](main.py) | エージェントの起動、ツールの実装、最適化構成の読み込み |
| [requirements.txt](requirements.txt) | Python の依存関係。直接コードデプロイ時にリモートビルドでインストール |
| [.agent_configs/baseline/metadata.yaml](.agent_configs/baseline/metadata.yaml) | モデルと構成ファイルの参照先 |
| [.agent_configs/baseline/instructions.md](.agent_configs/baseline/instructions.md) | 最適化前のシステムプロンプト |
| [.agent_configs/baseline/skills/policy-reviewer/SKILL.md](.agent_configs/baseline/skills/policy-reviewer/SKILL.md) | 出張申請レビューのスキル |
| [.agent_configs/baseline/tools.json](.agent_configs/baseline/tools.json) | 最適化対象となるツールの説明とパラメーター定義 |
| [../../azure.yaml](../../azure.yaml) | このサンプルのデプロイ定義、モデルデプロイ、エージェントの環境変数 |

現行の手順では、エージェント定義はルートの `azure.yaml` を使います。このフォルダーに残る `agent.yaml` や `Dockerfile` を編集する必要はありません。直接コードデプロイを使うため、ローカルの Docker / ACR の準備も不要です。

構成の適用方法やロールバックは、ルート README の [Step 4 — 勝者を適用してデプロイする](../../README.md#6-step-4--勝者を適用してデプロイする) を参照してください。
