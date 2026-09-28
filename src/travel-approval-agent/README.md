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
| [requirements.in](requirements.in) | 直接依存の固定バージョン。依存更新時の編集元 |
| [requirements.txt](requirements.txt) | 直接依存・間接依存を固定した生成ファイル。リモートビルド・Docker・ローカルで共通利用 |
| [.agent_configs/baseline/metadata.yaml](.agent_configs/baseline/metadata.yaml) | モデルと構成ファイルの参照先 |
| [.agent_configs/baseline/instructions.md](.agent_configs/baseline/instructions.md) | 最適化前のシステムプロンプト |
| [.agent_configs/baseline/skills/policy-reviewer/SKILL.md](.agent_configs/baseline/skills/policy-reviewer/SKILL.md) | 出張申請レビューのスキル |
| [.agent_configs/baseline/tools.json](.agent_configs/baseline/tools.json) | 最適化対象となるツールの説明とパラメーター定義 |
| [../../azure.yaml](../../azure.yaml) | このサンプルのデプロイ定義、モデルデプロイ、エージェントの環境変数 |

現行の手順では、エージェント定義はルートの `azure.yaml` を使います。このフォルダーに残る `agent.yaml` や `Dockerfile` を編集する必要はありません。直接コードデプロイを使うため、ローカルの Docker / ACR の準備も不要です。

構成の適用方法やロールバックは、ルート README の [Step 4 — 勝者を適用してデプロイする](../../README.md#6-step-4--勝者を適用してデプロイする) を参照してください。

## 依存パッケージの固定と更新

`requirements.in` の直接依存と、生成された `requirements.txt` の間接依存は、すべて `==` でバージョン固定しています。2026-09-25 の検証時のローカル環境を基準にし、Python 3.13（Foundry）と Python 3.14（既存の Dockerfile / ローカル）で利用する構成です。`pywin32` などの OS 固有パッケージには条件を付けているため、Windows の環境をそのまま `pip freeze` して Linux に持ち込む形ではありません。

通常のデプロイでは生成コマンドを実行する必要はありません。ローカル開発時も、仮想環境に同じファイルからインストールします。

```bash
# リポジトリルートから、使用する仮想環境を有効にした状態で実行
python -m pip install -r src/travel-approval-agent/requirements.txt
python -m pip check
```

依存を更新する場合だけ、次の手順を実施します。

1. `requirements.in` の対象バージョンを更新します。プレビュー版も `==` で明示します。
2. 更新作業用の仮想環境で、以下を実行します。`uv` は生成用であり、エージェントの実行には不要です。

```bash
python -m pip install uv==0.12.17
cd src/travel-approval-agent
uv pip compile requirements.in --universal --python-version 3.13 --no-annotate --output-file requirements.txt
```

3. 差分を確認し、空の仮想環境に `requirements.txt` をインストールして `python -m pip check` とエージェントの起動・ツール動作を確認します。デプロイ前には対象ランタイムでも確認してください。
4. `requirements.in` と `requirements.txt` を一緒にコミットします。

再生成時は既存の固定バージョンが優先されます。間接依存も意図的に更新するときだけ生成コマンドに `--upgrade` を追加し、同様に確認してください。Renovate は `pip-compile` マネージャーで編集元と生成ファイルをまとめて更新する設定です。自動生成された PR も、確認せずにマージしないでください。

この固定の対象は Python パッケージのバージョンです。Python 本体、Docker ベースイメージ、azd、Azure 上のモデルやサービスまで固定するものではありません。また、固定後もセキュリティ修正などの更新は定期的に取り込む必要があります。
