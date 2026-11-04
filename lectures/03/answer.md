# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
　素のLLMの回答は、入力した質問につながる単語をひたすら生成して、それっぽい答えを作るだけで、
　エージェントの回答は、回答するために必要な情報を探して、整理しながら回答している。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
前提：uv run python -m app.agent --trace "第2回の内容から確認問題を1問出して"　を実行した。

[tool call]   make_quiz({'lecture': 2})
[tool return] make_quiz -> {"question": "「過学習」の意味は？", "answer": "学習データにだけ過度に適合し、未知の入力に対する性能が落ちる状態。学習に使わない検証データで性能を測って気づく。"}…

- 1つの質問での LLM 呼び出し回数（`requests`）：2回
根拠：[usage] RunUsage(cost=Decimal('0.0004473'), details={'text_prompt_tokens': 966}, input_text_tokens=966, input_tokens=966, output_tokens=63, requests=2, tool_calls=1)

- 追加したツールと、docstring に書いた説明：
追加したツールは、make_quiz
docstring に書いた説明は、次のとおり。
    """指定した回の用語から1問を選んで、復習用の確認問題を作る。
    「第2回の確認問題を出して」「この回の問題を作って」のように、
    学習内容の振り返りや復習を求められたときに使うツール。
    その回で扱う用語が見つからない場合は、利用可能な回やエラー内容を返す。
    """
## 宿題

- 取り組んだレベル：実装

- やったこと：学習の記録を learning_log/ フォルダに保存するツール save_learning_log を作り、保存の前に利用者の確認を挟むように実装する。

実行コマンドは「uv run python -m app.agent --trace "第2回の内容から確認問題を1問出して質問と回答を保存して"」
コマンド起動後に、「このツールを実行してよいですか？ [y/N]」と表示されるので、「y」を入力してエンターキーを押す。
第2回の内容から確認問題を1問作成し、学習の記録として保存しました。

応答時間、トークン数は次のとおりで、LLMの実行回数は3回となりました。
　第2回
　[応答時間] 9.94秒
　[今回] 入力: 2103 tokens / 出力: 164 tokens / requests: 3
　[この実行の累計] 入力: 2103 tokens / 出力: 164 tokens / requests: 3
　[観測使用量] 直近1分: 3 requests, 2103 input tokens / 本日: 3 requests（この実行分のみ）
　[推定残り] RPM・TPM・RPDすべての上限を設定すると表示できます

traceの内容は次のとおりで、make_quiz及びsave_learning_logの2つのツールが呼び出されていることが確認できます。
--- trace ---
[tool call]   make_quiz({'lecture': 2})
[tool return] make_quiz -> {"question": "「Hugging Face Hub」の意味は？", "answer": "公開されたモデルやデータセットを共有・ダウンロードできるプラットフォーム。オープンウェイトのモデルを入手したり、LoRAアダプタを公開した…
[tool call]   save_learning_log({'topic': '第2回 確認問題と解答', 'note': '第2回の確認問題：\n問題：「Hugging Face Hub」の意味は？\n回答：公開されたモデルやデータセットを共有・ダウンロードできるプラットフォーム。オープンウェイトのモデルを入手したり、LoRAアダプタを公開したりするのに使われる。'})
[tool return] save_learning_log -> {"status": "saved", "path": "/workspaces/lecture-ai-engineering-2026/learning_log/20261104-045834_第2回 確認問題と解答.md","file…
[usage] RunUsage(cost=Decimal('0.0010409'), details={'text_prompt_tokens': 2103}, input_text_tokens=2103, input_tokens=2103, output_tokens=164, requests=3, tool_calls=2)

- 結果：保存処理を挟んだ分、LLMの起動回数が１回増えた。
　　　　また、LLMの入力トークン消費量も演習に比べて約２倍に増加した（保存処理なし966、保存処理あり2103）。

- 気づき・疑問：過去に同じ質問を投げたときに回答履歴（人間による確認済み）を参照するようにすれば、回答の生成速度の向上や、トークン消費量の節約につながるのではないかと思った。
