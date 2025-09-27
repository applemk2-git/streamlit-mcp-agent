# Streamlit MCP Agent

> **注意事項**  
> 私の本業はネットワークエンジニアです。プログラミングは趣味として取り組んでおり、「動けばそれで良し」という精神で開発しています。  
> そのため、コードの品質や設計に稚拙な部分があるかもしれませんが、ご理解いただけますと幸いです。

Streamlit MCP Agentは、Model Context Protocol (MCP) を活用したAIエージェントとのチャットインターフェースを提供するStreamlitアプリケーションです。awsのstrands agentsフレームワークを利用しています。MCPクライアント経由でさまざまなツールを統合し、対話的なAIアシスタントを実現します。

## プロジェクトの概要

このアプリケーションは、以下の主要な機能を提供します：

- **MCP統合**: 複数のMCPクライアントをサポートし、AIエージェントが外部ツールを活用可能
- **ストリーミング応答**: リアルタイムでAIの応答をストリーミング表示
- **チャットインターフェース**: ユーザーフレンドリーなStreamlitベースのチャットUI
- **セッション管理**: チャット履歴の保持とセッション状態のリセット機能
- **ツール実行**: MCP経由でツールの実行と結果の表示

## 必要な環境・依存関係

### システム要件
- Python 3.13以上
- uv (Pythonパッケージマネージャー)

### 依存関係
- `ollama>=0.5.4`: Ollamaモデルとの連携（このままの設定でOllamaを使用する場合のみ必要）
- `strands-agents>=1.9.1`: AIエージェントフレームワーク
- `streamlit>=1.49.1`: WebアプリケーションUI

### 追加要件
- Ollamaサーバー: デフォルトで `http://localhost:11434` を使用
- MCP設定ファイル: `param/mcp.json` にMCPクライアントの設定を定義

## インストール・実行方法

### 1. リポジトリのクローン
```bash
git clone https://github.com/applemk2-git/streamlit-mcp-agent.git
cd streamlit-mcp-agent
```

### 2. 依存関係のインストール
```bash
uv sync
```

### 3. アプリケーションの実行
```bash
uv streamlit run agent.py
```

アプリケーションが起動したら、ブラウザで `http://localhost:8501` にアクセスしてください。

### 4. モデルサーバーのセットアップ（オプション）
このままの設定で実行する場合、Ollamaサーバーが必要です。実行されていない場合は起動してください：
```bash
ollama serve
```

デフォルトモデルとして `gpt-oss:20b` を使用します。必要に応じて `agent.py` 内の `DEFAULT_MODEL_ID` を変更してください。

## 使用例

### 基本的な使用方法
1. アプリケーション起動後、サイドバーから使用するMCPを選択
2. チャット入力欄にメッセージを入力
3. AIエージェントがMCPツールを活用して応答を生成

### サンプル対話
```
ユーザー: 現在の天気を教えてください
アシスタント: [MCPツールを使用して天気情報を取得し、結果を表示]
```

### MCP設定例
`param/mcp.json` では、以下の3種類のトランスポートタイプをサポートしています：

#### 1. stdio（標準入出力）
記載方法の例です。実際の利用するmcpに合わせて書き換えてください。
```json
{
  "aws-documentation-mcp": {
    "transport": "stdio",
    "command": "uvx",
    "args": ["awslabs.aws-documentation-mcp-server@latest"]
  }
}
```

#### 2. streamable-http（HTTPストリーミング）
記載方法の例です。実際の利用するmcpに合わせて書き換えてください。localhostではなくリモートホストでもOK。
```json
{
  "api-server": {
    "transport": "streamable-http",
    "url": "http://localhost:3000/mcp"
  }
}
```

#### 3. sse（Server-Sent Events）
記載方法の例です。実際の利用するmcpに合わせて書き換えてください。localhostではなくリモートホストでもOK。
```json
{
  "sse-server": {
    "transport": "sse",
    "url": "http://localhost:3000/sse-mcp"
  }
}
```

カンマ区切りで複数のmcpサーバを定義可能です。

### デフォルトのMCP設定について
`param/mcp.json` には、以下の設定がデフォルトで含まれています：

- **aws-documentation-mcp**: AWSが提供する公式のMCPサーバー（実際に動作します）
  - AWSドキュメント検索機能を提供

**注意**: streamable-httpとsseの設定例は書き方の参考として記載していますが、実際には動作しないダミー設定です。実際のMCPサーバーを使用する際は、適切なURLやコマンドに変更してください。

## 機能詳細

### MCPクライアントのサポート
- **stdio**: 標準入出力ベースのMCPクライアント
- **streamable-http**: HTTPストリーミングベースのMCPクライアント
- **sse**: Server-Sent EventsベースのMCPクライアント

### エラーハンドリング
- MCPクライアントの初期化失敗時の警告表示
- ツール実行エラーの適切な処理
- セッション状態の安全な管理

### カスタマイズ
- システムプロンプトの変更（`DEFAULT_SYSTEM_PROMPT`）
- モデル設定の変更（`DEFAULT_MODEL_HOST`, `DEFAULT_MODEL_ID`）
- MCP設定ファイルのパス変更（`MCP_CONFIG_PATH`）

## ライセンス

このプロジェクトはApache License 2.0の下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルをご参照ください。

## 注意事項

- 初回実行時はMCPクライアントの初期化に時間がかかる場合があります
- 外部APIを使用するMCPツールの場合、適切な認証情報が必要です
- 開発環境ではOllamaサーバーが実行されていることを確認してください

## モデル設定について

このプロジェクトではOllamaを使用した例を示していますが、これはあくまで一例です。利用可能なモデルや、それぞれのモデルの使い方については、[Strands AgentsドキュメントのModel Providersセクション](https://strandsagents.com/latest/documentation/docs/)を参照して、各々で適切な設定を行ってください。

`agent.py` 内の以下の部分を変更することで、異なるモデルプロバイダーを使用できます：

### 設定定数の変更
- `DEFAULT_MODEL_HOST`: モデルサーバーのホストURL
- `DEFAULT_MODEL_ID`: 使用するモデルID
- `DEFAULT_SYSTEM_PROMPT`: システムプロンプト
- `MODEL`: モデル


### モデルオブジェクトの変更
上記の定数を変更しただけでは不十分です。`create_agent` 関数内のモデルオブジェクトも適切なモデルプロバイダーに変更する必要があります：

```python
# 現在のOllamaModelの例
model=OllamaModel(
    host=DEFAULT_MODEL_HOST,
    model_id=DEFAULT_MODEL_ID,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)
```

他のモデルプロバイダー（例: OpenAI, Anthropicなど）を使用する場合は、対応するモデルクラスに変更し、必要なパラメータを設定してください。詳細な設定方法はStrands Agentsドキュメントを参照してください。
