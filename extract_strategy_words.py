import os
import MeCab
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import poisson
import csv

# N-gram生成
def generate_ngrams(text, n=2):
    tagger = MeCab.Tagger("-Owakati -r /opt/homebrew/etc/mecabrc")
    words = tagger.parse(text).strip().split()
    return [''.join(words[i:i+n]) for i in range(len(words)-n+1)]

# IR文書からN-gram抽出
def extract_ngrams_from_dir(dir_path, n=2):
    ngram_counter = Counter()
    doc_lengths = []
    for fname in os.listdir(dir_path):
        with open(os.path.join(dir_path, fname), encoding='utf-8') as f:
            text = f.read()
            ngrams = generate_ngrams(text, n)
            ngram_counter.update(ngrams)
            doc_lengths.append(len(ngrams))
    return ngram_counter, doc_lengths

# 共通語コーパスからN-gram抽出
def extract_common_ngrams(corpus_path, n=2):
    with open(corpus_path, encoding='utf-8') as f:
        text = f.read()
    return set(generate_ngrams(text, n))

# 文字列の独立性指標計算（I_w）
def calc_independence_index(ngram_counter, doc_lengths):
    # ngram_counter: {ngram: count}
    # doc_lengths: [各文書のN-gram数]
    total_ngrams = sum(ngram_counter.values())
    avg_doc_length = np.mean(doc_lengths)
    independence_index = {}
    for ngram, q_w in ngram_counter.items():
        # λ = np = L_d / K_dt * (K_dt = 文書中の有効文字列数, L_d = 文書長)
        # ここでは全体平均で近似
        lam = avg_doc_length / (len(ngram_counter) + 1)
        # P(X = q_w) = (λ^q_w * e^-λ) / q_w!
        px = poisson.pmf(q_w, lam)
        # I_w = 1 - P(X = q_w)
        I_w = 1 - px
        independence_index[ngram] = I_w
    return independence_index

# 重要度指標S_dwの計算（累積分布でP(X >= q_w)を計算）
def calc_importance_index(ngram_counter, doc_lengths, independence_index, threshold=0.5):
    avg_doc_length = np.mean(doc_lengths)
    importance_index = {}
    for ngram, q_w in ngram_counter.items():
        lam = avg_doc_length / (len(ngram_counter) + 1)
        # S_dw = 1 - P(X >= q_w) = 1 - Σ_{i=q_w}^{∞} P(X=i)
        # 実装上は十分大きい値まで合計
        max_i = int(q_w + 10 * np.sqrt(lam))
        px_cum = sum([poisson.pmf(i, lam) for i in range(q_w, max_i)])
        S_dw = 1 - px_cum
        if S_dw >= threshold:
            importance_index[ngram] = S_dw
    return importance_index

# 共通語除去（頻度比によるノイズ除去も考慮）
def remove_common_words(ngram_counter, common_ngrams, common_threshold=0.8):
    # 共通語コーパスに含まれるN-gramを除去
    return {k: v for k, v in ngram_counter.items() if k not in common_ngrams}

if __name__ == "__main__":
    ir_dir = "ir_texts"
    common_corpus = "common_corpus.txt"
    n = 2  # バイグラム

    print("IR文書からN-gram抽出中...")
    ngram_counter, doc_lengths = extract_ngrams_from_dir(ir_dir, n)
    print(f"抽出N-gram数: {len(ngram_counter)}")

    print("共通語コーパスからN-gram抽出中...")
    common_ngrams = extract_common_ngrams(common_corpus, n)
    print(f"共通語N-gram数: {len(common_ngrams)}")

    print("共通語除去中...")
    filtered_ngrams = remove_common_words(ngram_counter, common_ngrams)
    print(f"除去後N-gram数: {len(filtered_ngrams)}")

    # ここで独立性指標・重要度指標の計算を呼び出す
    print("独立性指標計算中...")
    independence_index = calc_independence_index(filtered_ngrams, doc_lengths)
    print("重要度指標計算中...")
    importance_index = calc_importance_index(filtered_ngrams, doc_lengths, independence_index)
    print("上位戦略ワード候補:")
    for word, score in sorted(importance_index.items(), key=lambda x: -x[1])[:30]:
        print(f"{word}: {score:.3f}")

    # 結果をCSV出力
    with open("strategy_words.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "score"])
        for word, score in sorted(importance_index.items(), key=lambda x: -x[1]):
            writer.writerow([word, score])
    print("strategy_words.csv に保存しました。") 