import streamlit as st
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from pathlib import Path
import json
from contextlib import ExitStack
import asyncio

# 利用するモデルによって変更
from strands.models.ollama import OllamaModel

# gpt-ossを使う場合の例
DEFAULT_MODEL_HOST = "http://localhost:11434"
DEFAULT_MODEL_ID = "gpt-oss:20b"
DEFAULT_SYSTEM_PROMPT = "あなたは優秀なアシスタントです。"
MODEL = OllamaModel(
    host=DEFAULT_MODEL_HOST,
    model_id=DEFAULT_MODEL_ID,
    system_prompt=DEFAULT_SYSTEM_PROMPT,
)

MCP_CONFIG_PATH = "param/mcp.json"


async def process_stream_response(agent, prompt, message_placeholder, tool_status):
    """
    ストリーミングレスポンスを処理する関数

    Args:
        agent: エージェントオブジェクト
        prompt: ユーザーの入力プロンプト
        message_placeholder: メッセージ表示用プレースホルダー
        tool_status: ツールステータス表示用プレースホルダー

    Returns:
        str: 最終的な完全なレスポンス
    """
    full_response = ""
    current_tool_use = None

    async for event in agent.stream_async(prompt):
        # モデル出力データの処理
        if "data" in event and isinstance(event["data"], str):
            full_response += event["data"]
            message_placeholder.markdown(full_response + "▌")

        # ツール実行開始の処理
        elif (
            "current_tool_use" in event
            and event["current_tool_use"] != current_tool_use
        ):
            current_tool_use = event["current_tool_use"]
            if current_tool_use:
                tool_name = current_tool_use.get("name", "unknown")
                tool_status.info(f"ツール実行中: {tool_name}...")

        # ツール実行結果の処理
        elif "current_tool_result" in event and event["current_tool_result"]:
            if current_tool_use:
                tool_name = current_tool_use.get("name", "unknown")
                tool_status.success(f"ツール {tool_name} の実行が完了しました")
                current_tool_use = None

    # 最終的な応答を表示
    message_placeholder.markdown(full_response)
    tool_status.empty()
    return full_response


def reset_session():
    """セッション状態をリセットする"""
    for key in list(st.session_state.keys()):
        if key != "model":
            del st.session_state[key]
    st.rerun()


def load_mcp_config():
    """
    MCP設定ファイルを読み込む

    Returns:
        dict: MCP設定データ

    Raises:
        FileNotFoundError: 設定ファイルが存在しない場合
        json.JSONDecodeError: JSON形式が不正の場合
        ValueError: 設定ファイルの形式が不正の場合
    """
    config_path = Path(__file__).parent / MCP_CONFIG_PATH

    if not config_path.exists():
        raise FileNotFoundError(f"MCP設定ファイルが見つかりません: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    if not isinstance(config, dict):
        raise ValueError("MCP設定ファイルの形式が正しくありません")

    return config


def create_mcp_client(mcp_name, mcp_config):
    """
    MCPクライアントを作成する

    Args:
        mcp_name: MCPの名前
        mcp_config: MCP設定データ

    Returns:
        MCPClient: 作成されたMCPクライアント
    """
    transport = mcp_config["transport"]

    if transport == "streamable-http":
        url = mcp_config["url"]
        return MCPClient(lambda u=url: streamablehttp_client(u))
    elif transport == "sse":
        url = mcp_config["url"]
        return MCPClient(lambda u=url: sse_client(u))
    elif transport == "stdio":
        command = mcp_config["command"]
        args = mcp_config["args"]
        return MCPClient(
            lambda c=command, a=args: stdio_client(
                StdioServerParameters(command=c, args=a)
            )
        )
    else:
        raise ValueError(f"未対応のトランスポートタイプです: {transport}")


def initialize_mcp_clients(selected_mcps, mcp_config):
    """
    MCPクライアントを初期化する

    Args:
        selected_mcps: 選択されたMCPリスト
        mcp_config: MCP設定データ

    Returns:
        dict: 初期化されたMCPクライアントの辞書
    """
    clients = {}
    for mcp_name in selected_mcps:
        try:
            clients[mcp_name] = create_mcp_client(mcp_name, mcp_config[mcp_name])
        except Exception as e:
            st.error(f"MCPクライアント {mcp_name} の初期化に失敗しました: {e}")
            continue
    return clients


def create_agent(mcp_clients):
    """
    エージェントを作成する

    Args:
        mcp_clients: MCPクライアントの辞書

    Returns:
        Agent: 作成されたエージェント
    """
    # ツールの収集
    tools = []
    for client in mcp_clients.values():
        try:
            tools.extend(client.list_tools_sync())
        except Exception as e:
            st.warning(f"ツール一覧の取得に失敗しました: {e}")
            continue

    return Agent(
        model=MODEL,
        tools=tools,
    )


def handle_mcp_selection(mcp_config):
    """
    MCP選択を処理する

    Args:
        mcp_config: MCP設定データ

    Returns:
        list: 選択されたMCPのリスト
    """
    if "persistent_selected_mcps" not in st.session_state:
        st.session_state["persistent_selected_mcps"] = []

    selected = st.sidebar.multiselect(
        "Select MCPs",
        mcp_config.keys(),
        default=st.session_state["persistent_selected_mcps"],
        key="mcp_selection",
    )

    if set(selected) != set(st.session_state["persistent_selected_mcps"]):
        st.session_state["persistent_selected_mcps"] = selected.copy()
        # 依存するセッション状態をクリア
        for key in ["agent", "messages", "mcp_clients"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    return selected


def render_header():
    """ヘッダー部分を表示する"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            "<h1 style='text-align: center;'>MCP Agent</h1>", unsafe_allow_html=True
        )
        if st.button("リセット", use_container_width=True):
            reset_session()


def render_chat_history():
    """チャット履歴を表示する"""
    if "messages" not in st.session_state:
        return

    for chat in st.session_state["messages"]:
        role = chat["role"]
        with st.chat_message(role):
            content = (
                chat["content"].replace("\n", "<br>")
                if role == "user"
                else chat["content"]
            )
            st.markdown(content, unsafe_allow_html=True)


def handle_chat_input():
    """チャット入力を処理する"""
    if "agent" not in st.session_state:
        st.error("エージェントが初期化されていません")
        return

    user_msg = st.chat_input("メッセージを入力してください...")
    if not user_msg:
        return

    # ユーザーメッセージを表示
    with st.chat_message("user"):
        st.markdown(user_msg.replace("\n", "<br>"), unsafe_allow_html=True)

    # セッション状態に追加
    st.session_state["messages"].append({"role": "user", "content": user_msg})

    # アシスタントの応答を処理
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        tool_status = st.empty()

        try:
            final_response = asyncio.run(
                process_stream_response(
                    agent=st.session_state["agent"],
                    prompt=user_msg,
                    message_placeholder=message_placeholder,
                    tool_status=tool_status,
                )
            )
            st.session_state["messages"].append(
                {"role": "assistant", "content": final_response}
            )
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")


def main():
    """メインアプリケーション"""
    # MCP設定の読み込み
    try:
        mcp_config = load_mcp_config()
        st.session_state["mcp_config"] = mcp_config
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        st.error(f"MCP設定エラー: {e}")
        st.error("param/mcp.json ファイルを確認してください。")
        st.stop()
    except Exception as e:
        st.error(f"予期しないエラー: {e}")
        st.stop()

    # サイドバー設定
    st.sidebar.title("MCP Settings")
    selected_mcps = handle_mcp_selection(mcp_config)

    # ヘッダー表示
    render_header()

    # MCPクライアント初期化
    if "mcp_clients" not in st.session_state:
        st.session_state["mcp_clients"] = initialize_mcp_clients(
            selected_mcps, mcp_config
        )

    # メッセージ履歴初期化
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # チャット履歴表示
    render_chat_history()

    # MCPクライアント接続
    with ExitStack() as stack:
        for key, client in st.session_state["mcp_clients"].items():
            try:
                stack.enter_context(client)
                print(f"{key} connected!")
            except Exception as e:
                print(f"{key} connect failed: {e}")

        # エージェント初期化
        if "agent" not in st.session_state:
            st.session_state["agent"] = create_agent(st.session_state["mcp_clients"])

        # チャット入力処理
        handle_chat_input()


if __name__ == "__main__":
    main()
