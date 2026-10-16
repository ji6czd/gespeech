# gespeech

A command-line tool for generating speech using Google Gemini text-to-speech.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run gespeech -t "こんにちは、世界！" -p
```

## Voices

```bash
uv run gespeech-voices -l ja-JP
```

Each line is `ID | DISPLAY_NAME (...)`. Use the ID as `voice_id`. See `-h` for
filters.

## Script files

`-i` reads a text file with optional TOML front matter between `+++` lines
(see `samples/hello.txt`). Accepted keys are `model_id`, `voice_id` and `style`.

### Dialogue (multiple speakers)

If the front matter has a `[speakers]` table (at most two speakers), the script
is sent as multi-speaker speech. Each body line is `name: text`; a line without
a label continues the previous line. `voice_id` cannot be combined with
`[speakers]`.

```text
+++
model_id = "gemini-3.8-flash-lite-tts"
style = "Cheerful and friendly"

[speakers]
tutor2 = "ja-jp-tutor-2"
tutor3 = "ja-jp-tutor-3"
+++
tutor2: こんにちは。
tutor3: <laugh> こんにちは。
```

## Inline tags

Inline tags allow you to add expressive sounds and actions directly within your text. Use the supported tags listed below by enclosing them in angle brackets, e.g., `<laugh>`.

### Supported tags

- argh — 痛みや怒りを表すうめき声
- breath — 息を吸う音
- cackle — 高笑い、けたけた笑う声
- cheer — 歓声、応援する声
- chuckle — くすくす笑う
- chuckles — くすくす笑い
- cough — せき
- cry — 泣く、泣き声
- exhales — 息を吐く
- gasp — はっと息をのむ音
- giggle — くすくす笑う、含み笑い
- groan — 苦しそうなうめき声
- growl — うなる声
- grr — 怒りや不満を表すうなり声
- grunt — うなるような短い声
- heavy breath — 荒い息、深い呼吸
- hiss — シューッという音、歯の間から出す声
- laugh — 笑う
- laughter — 笑い声
- long pause — 長い間
- moan — 悲しみや苦痛を表すうめき声
- pant — 息を切らす
- pff — あきれたり不満を示したりする鼻息
- phew — 安堵や疲れを表す「ふう」という息
- scream — 悲鳴を上げる
- short pause — 短い間
- shout — 大声で叫ぶ
- shriek — 甲高い悲鳴を上げる
- sigh — ため息をつく
- sighs — ため息
- sneeze — くしゃみ
- snicker — こっそり笑う、忍び笑い
- snort — 鼻を鳴らす、鼻で笑う
- sob — すすり泣く
- throat-clearing — せき払い
- tsk — 舌打ち
- whimper — 弱々しく泣く、すすり上げる
- whispering — ささやく
- whispers — ささやき声
- yawn — あくび
