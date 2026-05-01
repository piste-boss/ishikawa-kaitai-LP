# BASE テンプレート対応手順

静的なLP（HTML/CSS/JS の単純構成）を **BASE** の「HTML編集App」で動くテンプレートに変換する手順。
今回は `index.html` を `base-template.inline.html` に変換した実例ベース。

公式仕様: https://docs.thebase.in/template/

---

## TL;DR

```bash
# 1. base-template.html を編集（BASE用タグ＋必須変数を入れる）
# 2. ビルド
python3 build-base.py
# 3. 出力された base-template.inline.html の中身を BASE 管理画面に貼り付け
```

---

## 前提

| 項目 | 想定 |
|---|---|
| 元LP | 静的な `index.html` + 外部 CSS/JS + ローカル `assets/` 画像 |
| 公開先 | BASE ショップの「HTML編集App」 |
| Git ホスト | GitHub（jsDelivr 経由で画像CDN化） |
| BASE側の制約 | `<textarea>` 不可 / 必須変数タグあり / ファイルアップロード不可 |

---

## ステップ1: 必須テンプレートタグを入れる

### 1-1. ブロックタグで全体をラップ

```html
{block:NotLoadItemsPage}<!doctype html>
<html lang="ja">
<head>...</head>
<body>
{BackgroundTag}

{block:IndexPage}
  <!-- トップページの内容 -->
{/block:IndexPage}

{block:NotIndexPage}
  <main><div>{PageContents}</div></main>
{/block:NotIndexPage}

<footer>...</footer>
</body>
</html>{/block:NotLoadItemsPage}

{block:LoadItemsPage}
  {block:Items}
    <a href="{ItemPageURL}">...</a>
  {/block:Items}
{/block:LoadItemsPage}
```

### 1-2. `<head>` 必須変数

| タグ | 役割 | 配置 |
|---|---|---|
| `{PageTitle}` | ページタイトル | `<title>` 内 |
| `{FaviconTag}` | favicon link 自動生成 | `<head>` 直下 |
| `{GoogleAnalyticsTag}` | GA タグ自動挿入 | `<head>` 直下 |
| `{ItemAttentionTag}` | 商品ページ注意書き | `<head>` 直下 |

### 1-3. `<body>` 必須変数

| タグ | 役割 |
|---|---|
| `{BackgroundTag}` | 背景設定（管理画面で変更可能に） |
| `{LogoTag}` | ロゴ画像 / 店舗名 |
| `{BASEMenuTag}` | BASE標準ナビゲーション |
| `{ShopName}` | 店舗名 |
| `{IndexPageURL}` | トップページURL（ロゴリンク先） |
| `{ContactPageURL}` | お問い合わせ（フッター必須） |
| `{PrivacyPageURL}` | プライバシーポリシー（フッター必須） |
| `{LawPageURL}` | 特定商取引法（フッター必須） |
| `{IllegalReportTag}` | 違反通報リンク（フッター必須） |
| `{PageContents}` | 非IndexPageの本文（About/Privacy等で使用） |

### 1-4. カスタムデザインで使わない必須タグの隠し方

`{LogoTag}` や `{BASEMenuTag}` を出力したくないが必須なので、`{block:Hidden}` で囲む:

```html
{block:Hidden}{LogoTag}{BASEMenuTag}{/block:Hidden}
```

---

## ステップ2: 禁止要素を除去

### 2-1. `<textarea>` を `<input type="text">` に置換

BASEは `<textarea>` 自体を禁止。複数行入力が必要な場合は CSS で高さを稼ぐ:

```html
<input type="text" name="message" class="apply__message" placeholder="..." />
```

```css
.apply__form input.apply__message {
  padding: 28px 16px;  /* 上下を太くして見た目だけ複数行風に */
}
```

### 2-2. その他の制約（出たら追加）

- インラインJSの可否はテーマ審査次第。`<script>` ブロックは通常OKだが、外部 `<script src>` は不可なケースが多い
- `<iframe>` は基本NG
- フォームの `action` を独自URLにしてもBASE側ではPOSTされない（応募フォームは飾りで、実際は別経路を案内）

---

## ステップ3: 外部ファイルをインライン化

BASEはテンプレートHTML 1ファイルしか受け付けない。CSS/JS はすべてインライン化する。

### 3-1. CSS インライン化

```html
<!-- Before -->
<link rel="stylesheet" href="styles.css" />
<link rel="stylesheet" href="sections.css" />

<!-- After -->
<style>
/* styles.css の中身 */
/* sections.css の中身 */
</style>
```

### 3-2. JS インライン化

```html
<!-- Before -->
<script src="script.js"></script>

<!-- After -->
<script>
/* script.js の中身 */
</script>
```

---

## ステップ4: 画像を CDN URL に置換

ローカル `assets/...` のままだと BASE プレビューで `admin.thebase.com/shop_preview/assets/...` に解決されて 404 になる。

### 4-1. GitHub に push してから jsDelivr URL を生成

```
ローカル:  assets/ishikawa-hero-wide.jpg
       ↓
CDN URL: https://cdn.jsdelivr.net/gh/<user>/<repo>@main/assets/ishikawa-hero-wide.jpg
```

例:
```html
<img src="https://cdn.jsdelivr.net/gh/piste-boss/ishikawa-kaitai-LP@main/assets/ishikawa-hero-wide.jpg" />
```

### 4-2. CSS 内の `url(...)` も忘れず置換

```css
/* Before */
background: url('assets/brush-red.png');
/* After */
background: url('https://cdn.jsdelivr.net/gh/piste-boss/ishikawa-kaitai-LP@main/assets/brush-red.png');
```

### 4-3. キャッシュ注意

- jsDelivr は最大12時間キャッシュ
- 即時反映が必要なら `@main` をコミットSHA固定に: `@17c53c6`

---

## ステップ5: ビルドスクリプトで自動化

毎回手作業でやらないために `build-base.py` を置く。

`build-base.py`:
```python
"""Inline CSS / JS / images into base-template.html for BASE upload."""
import re
from pathlib import Path

ROOT = Path(__file__).parent
CDN_BASE = "https://cdn.jsdelivr.net/gh/piste-boss/ishikawa-kaitai-LP@main/assets"

html = (ROOT / "base-template.html").read_text(encoding="utf-8")
styles = (ROOT / "styles.css").read_text(encoding="utf-8")
sections = (ROOT / "sections.css").read_text(encoding="utf-8")
script = (ROOT / "script.js").read_text(encoding="utf-8")

# CSS 内の assets/ も書き換え
styles = styles.replace("url('assets/", f"url('{CDN_BASE}/")
styles = styles.replace('url("assets/', f'url("{CDN_BASE}/')

# CSS 結合 → <style> ブロック
combined_css = styles + "\n\n/* === sections.css === */\n\n" + sections
style_block = f"<style>\n{combined_css}\n</style>"

# <link> タグを <style> に置換
html = re.sub(
    r'\s*<link rel="stylesheet" href="styles\.css"[^>]*>\s*<link rel="stylesheet" href="sections\.css"[^>]*>',
    "\n  " + style_block,
    html,
)

# <script src> を <script> インラインに置換
html = html.replace(
    '<script src="script.js"></script>',
    f"<script>\n{script}\n</script>",
)

# 画像 src / og:image を CDN URL に
html = re.sub(r'src="assets/', f'src="{CDN_BASE}/', html)
html = re.sub(r'content="assets/', f'content="{CDN_BASE}/', html)

(ROOT / "base-template.inline.html").write_text(html, encoding="utf-8")
print("Wrote base-template.inline.html — size:", len(html), "bytes")
```

実行:
```bash
python3 build-base.py
```

---

## ステップ6: BASEに貼り付け

1. BASE管理画面 → デザイン → HTML編集App をインストール / 開く
2. `base-template.inline.html` の中身を全選択コピーして貼り付け
3. 保存 → プレビュー
4. 必須タグ不足エラーが出たら **このドキュメントの「ステップ1」に戻って追加**

---

## バリデーションエラー早見表

| エラー | 対処 |
|---|---|
| `必須変数の{XxxTag}が見つかりませんでした` | ステップ1-2 / 1-3 の表を見て該当タグを追加 |
| `<textarea>は使用できません` | `<input type="text">` に置換（ステップ2-1） |
| プレビューで `404 (Not Found)` 大量発生 | 外部ファイル参照が残ってる。ステップ3 / 4 を実施 |
| プレビューでスタイルが当たらない | `<style>` インライン化忘れ |
| 画像だけ表示されない | jsDelivr URL タイポ / push 忘れ / キャッシュ未反映 |

---

## チェックリスト

提出前に必ず確認:

- [ ] `<head>` 内: `{PageTitle}` `{FaviconTag}` `{GoogleAnalyticsTag}` `{ItemAttentionTag}`
- [ ] `<body>` 直後: `{BackgroundTag}`
- [ ] フッター: `{ContactPageURL}` `{PrivacyPageURL}` `{LawPageURL}` `{IllegalReportTag}`
- [ ] どこかに: `{LogoTag}` `{BASEMenuTag}`（不要なら `{block:Hidden}` で囲む）
- [ ] `{block:NotLoadItemsPage}` ... `{/block:NotLoadItemsPage}` で全体ラップ
- [ ] `{block:LoadItemsPage}` の AJAX用ループあり
- [ ] `{block:IndexPage}` で LP 内容ラップ
- [ ] `{block:NotIndexPage}` 内に `{PageContents}` あり
- [ ] `<textarea>` ゼロ
- [ ] `<link rel="stylesheet" href="...">` ゼロ
- [ ] `<script src="...">` ゼロ
- [ ] `src="assets/` `url('assets/` `url("assets/` ゼロ（grep で確認）

```bash
# 一括チェック用
grep -E "<textarea|<link rel=\"stylesheet|<script src=|src=\"assets/|url\\(['\"]?assets/" base-template.inline.html
# → 何も出なければOK
```

---

## ファイル構成（参考）

```
.
├── index.html              # オリジナル（Netlify静的配信用）
├── styles.css              # 共通スタイル
├── sections.css            # セクションスタイル
├── script.js               # vanilla JS
├── assets/                 # 画像（GitHub経由でCDN配信）
├── base-template.html      # BASE用テンプレート（手で編集する元ファイル）
├── base-template.inline.html  # ビルド成果物（BASEに貼り付ける）
└── build-base.py           # インライン化スクリプト
```

---

## 既知の制約 / TODO

- BASE標準のフォーム送信機能はないので、応募フォームは「飾り」止まり。実運用は Instagram DM / 電話 / 別フォームサービスへ誘導
- jsDelivr は無料・無認証だが商用利用での冗長性は別途検討（必要ならCloudflare R2 等へ）
- BASE 商品（`{block:Items}`）を使う場合は max 24件 / ループ
