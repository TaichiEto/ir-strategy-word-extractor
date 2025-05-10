# 戦略ワード抽出アプリケーション（？）


## 概要
本プロジェクトは、企業のIR（Investor Relations）情報から戦略ワードを自動抽出するPythonアプリケーションです。N-gramと共通語コーパスを用いたノイズ除去、独立性・重要度指標によるスコアリングを行い、企業独自の戦略的キーワードを抽出します。

## 参考論文
本アプリケーションは、以下の論文の手法を参考に実装しています：

- 峯田誠也, 岡田公治, 「企業のIR情報からの戦略ワードの抽出法の提案」, 経営情報学会 全国研究発表大会要旨集, 2016年秋季全国研究発表大会, セッションID: G1-9  
  [J-STAGE 論文ページ](https://www.jstage.jst.go.jp/article/jasmin/2016f/0/2016f_75/_article/-char/ja/)
- 機能、数式の再現実装が未熟です。あくまで動作を再現したまでです。


## ディレクトリ構成
```
project/
├── ir_texts/              # IR文書（テキストファイル複数、テスト用サンプルも格納）
├── common_corpus.txt      # 共通語コーパス
├── extract_strategy_words.py  # メインスクリプト
├── strategy_words.csv     # 抽出結果（実行後に生成）
├── README.md              # このファイル
```

## テスト用IRテキストについて
`ir_texts/` ディレクトリには、動作確認用のサンプルIR文書（日本語テキスト）が格納されています。すぐに実行・検証が可能です。

## 必要な環境
- Python 3.8以降
- MeCab（本体・辞書）
- mecab-python3, numpy, scipy

### M1/M2/M3 Macの場合
HomebrewでMeCabをインストールし、`/opt/homebrew/etc/mecabrc` を参照するようにスクリプトが設定されています。

```
brew install mecab mecab-ipadic
pip install mecab-python3 numpy scipy
```

## 使い方
1. 必要なライブラリ・MeCab本体をインストール
2. `ir_texts/` にIR文書（テキストファイル）を追加（サンプルあり）
3. `common_corpus.txt` に共通語コーパスを用意（サンプルあり）
4. スクリプトを実行
   ```bash
   python extract_strategy_words.py
   ```
5. `strategy_words.csv` にスコア付き戦略ワードリストが出力されます

## カスタマイズ
- N-gramのn値やしきい値はスクリプト内で調整可能です。
- IR文書やコーパスを増やすことで精度検証や応用が可能です。

## 課題
- 共通ワードコーパスの再現が出来ていない

## ライセンス
MIT License 

## 出力結果（strategy_words.csv）について

スクリプト実行後に生成される `strategy_words.csv` には、抽出されたN-gram（バイグラム）ごとに「score（重要度指標）」が付与されています。

- **score（重要度指標）** とは（勝手な解釈）：
    - 各N-gramがIR文書中で偶然出現したとは考えにくい度合い（戦略的に使われている可能性の高さ）を示す指標です。
    - 論文の数式（S_dw = 1 - P(X ≥ q_w)）に基づき、ポアソン分布を用いて計算しています。
    - 値が大きいほど「戦略ワードとして有力」とみなされます。
    - 0.8以上：特に重要な戦略ワード候補、0.5前後：それなりに重要、0に近い：偶然でも出現しうる頻度

詳しくは参考論文やスクリプト内のコメントもご参照ください。
