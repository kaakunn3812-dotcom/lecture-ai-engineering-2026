# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

### STEP 1：ツールの名前

- **`app.agent`（2個）**
  - `search_materials`
  - `make_quiz`
- **`app.mcp_agent`（8個）**
  - `glossary_search_glossary`
  - `glossary_make_quiz`
  - `fetch_fetch`
  - `aws_aws___read_documentation`
  - `aws_aws___search_documentation`
  - `aws_aws___list_regions`
  - `aws_aws___get_regional_availability`
  - `aws_aws___retrieve_skill`

### STEP 2：`tool call`

```text
[tool call]   glossary_search_glossary({'query': '3レベル'})
[tool return] glossary_search_glossary -> [{"term": "宿題の3レベル", "lecture": 1, "definition": "AIE2026の宿題の構成。「基礎（講義内容の確認）」「実装（自分でコードを書く）」「発展（調査や試行）」の3段階があり、どれか1つに取り組…
```

### STEP 3：`tool call`

```text
[tool call]   glossary_search_glossary({'query': 'MCP'})
[tool return] glossary_search_glossary -> [{"term": "MCP（Model Context Protocol）", "lecture": 3, "definition": "AIアプリと外部のツールやデータソースをつなぐためのオープンな標準プロトコル。MCPサーバーとして公…
```

### STEP 4：`tool call`

```text
[tool call]   aws_aws___search_documentation({'topics': ['general'], 'search_phrase': 'Amazon S3 バージョニング 概要'})
[tool return] aws_aws___search_documentation -> {'content': {'result': [{'rank_order': 1, 'title': 'querying-aws-s3', 'skill_description': 'Queries S3 object metadata, …
[tool call]   aws_aws___search_documentation({'search_phrase': 'What is versioning in Amazon S3', 'topics': ['general']})
[tool return] aws_aws___search_documentation -> {'content': {'result': [{'rank_order': 1, 'title': 'Amazon S3 FAQs', 'context': '#### What is Versioning?\n\nVersioning …
```

### 気づき・疑問

- **気づき：** STEP 2・3 は内部知識（講義用語集）を検索し、STEP 4 は外部知識（AWS公式ドキュメント）を検索している。
- **疑問：** LLM はどのタイミングで内部知識と外部知識を使い分けているのか。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

### 取り組んだ内容

- **取り組んだレベル：** 実装
- **やったこと：** MCP サーバーに、第3回で作ったツール（`make_quiz`）を追加した。ツールの引数が範囲外のときに分かりやすいメッセージを返すようにし、そのメッセージがモデルにどう伝わるかを確かめた。
- **結果：** ツールが追加されたことは、演習 STEP 1 の `glossary_make_quiz` に示したとおり。

### 実行結果

用語が用意されている回はクイズが作成され、用意されていない回は、MCP 経由で利用できないことと利用可能な回が案内された。

#### 用語がある回：第6回

```bash
$ uv run --env-file .env python -m app.mcp_agent --trace "第6回のクイズを作って"
```

```text
[tool call]   glossary_make_quiz({'lecture': 6})
[tool return] glossary_make_quiz -> {"question": "ツールの名前空間の意味は？", "answer": "複数のMCPサーバーを使うとき、同じ名前のツールを区別するために「サーバー名_ツール名」のように接頭辞を付けること。本講座の app/mcp_agent.py…
[usage] 入力 5,535 tokens / 出力 138 tokens / モデル応答 2 回
```

#### 用語がない回：第5回

```bash
$ uv run --env-file .env python -m app.mcp_agent --trace "第5回のクイズを作って"
```

```text
[tool call]   glossary_make_quiz({'lecture': 5})
[tool return] glossary_make_quiz -> {"error": "第5回の用語は用意されていません。利用できる回: 第1回、第2回、第3回、第4回、第6回。"}…
[usage] 入力 5,457 tokens / 出力 88 tokens / モデル応答 2 回
```

### 気づき・疑問

- 接続している MCP サーバー（`glossary`、`fetch`、`aws`）のツール定義が毎回すべてシステムプロンプトとしてモデルに渡される。そのため、質問文が数文字違うだけでも、ベースとなる入力トークン数（約5,400〜5,500 tokens）はほぼ変わらない。
- 2回目はツールが例外（クラッシュ）を起こすのではなく、`{"error": "..."}` という JSON 文字列を返している。エージェント（LLM）は「データが存在しない」という事実を文脈として理解し、「第1〜4回、第6回なら作成できる」とフォローアップの回答を組み立てている。
