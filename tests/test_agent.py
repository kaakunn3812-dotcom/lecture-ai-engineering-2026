"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import RateLimits, agent, print_usage_summary, run_chat
from pydantic_ai.usage import RunUsage

BASE_TOOLS = {"search_glossary", "get_lecture_summary"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    assert len(_parts(result, ToolReturnPart)) == len(_parts(result, ToolCallPart))
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"


def test_chat_passes_previous_turns_as_message_history(monkeypatch, capsys):
    prompts = iter(["最初の質問", "続きの質問", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))

    run_sync = agent.run_sync
    histories = []

    def record_history(*args, **kwargs):
        histories.append(kwargs["message_history"])
        return run_sync(*args, **kwargs)

    monkeypatch.setattr(agent, "run_sync", record_history)
    run_chat(agent, TestModel(call_tools=[]))

    assert len(histories) == 2
    assert histories[0] == []
    assert "最初の質問" in str(histories[1])
    assert capsys.readouterr().out.count("[応答時間] ") == 2


def test_usage_summary_estimates_remaining_chats_from_tightest_limit(capsys):
    print_usage_summary(
        RunUsage(requests=2, input_tokens=100, output_tokens=40),
        [],
        RateLimits(rpm=10, tpm=1000, rpd=100),
    )

    output = capsys.readouterr().out
    assert "入力: 100 tokens" in output
    assert "出力: 40 tokens" in output
    assert "[推定残り] 約4チャット" in output
