# summarizer.py
# 必要なライブラリのインポート（スクリプト冒頭に追加）
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from PIL import Image
import os
import string
import re

# 初回実行時は以下を有効化（1回だけ必要）
# nltk.download('punkt')
# nltk.download('stopwords')


def extractor(full_context_text, question_text, top_n=5):
    """
    問題文からキーワードを抽出し、全文から関連する文脈を抽出して返す。
    
    Parameters:
    - full_context_text: すべてのページのテキスト（text_output_pathの内容）
    - question_text: クイズの問題文（例: "What did John do after the party?"）
    - top_n: 抽出する上位スコアの文脈数（デフォルト5）

    Returns:
    - relevant_context: GPTに渡す文脈文字列
    """

    # 1. 全ページを辞書に分割
    page_texts = re.findall(
        r'===== Page (\d+) =====\n\n(.*?)(?=(?:\n\n===== Page \d+ =====|$))',
        full_context_text, re.DOTALL)
    context_by_page = {int(p): t.strip() for p, t in page_texts}

    # 2. 問題文をトークン化してキーワード抽出
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(question_text.lower())
    keywords = [w for w in words if w not in stop_words and w not in string.punctuation]

    keyword_set = set(keywords)

    # 3. 各ページごとにスコアリング
    scored_pages = []
    for page, text in context_by_page.items():
        try:
            text_words = word_tokenize(text.lower())
        except Exception as e:
            print(f"Error tokenizing text on page {page}: {e}")
            return full_context_text[:4000]  # Fallback
        word_counts = Counter(text_words)
        score = sum(word_counts[k] for k in keyword_set if k in word_counts)
        if score > 0:
            scored_pages.append((score, page, text))

    # 4. スコア順に並び替え & 上位のみ抽出
    scored_pages.sort(reverse=True)
    selected_texts = [f"===== Page {page} =====\n{text}" for _, page, text in scored_pages[:top_n]]

    relevant_context = "\n\n".join(selected_texts)

    return relevant_context if relevant_context else full_context_text[:4000]  # Fallback

def noisereducer(text):
    
    page_markers = re.findall(r"(=+\s*Page\s*\d+\s*=+)", text, re.IGNORECASE)
    for i, marker in enumerate(page_markers):
        text = text.replace(marker, f"__PAGEMARKER_{i}__")

    cleaned_lines = []
    allowed_short_words = {"a", "i", "he", "we", "by", "is", "in", "on", "of", "to", "it", "do", "my"}

    for line in text.splitlines():

        if line.strip() == "":
            cleaned_lines.append("")
            continue

        line = re.sub(r"[‐–—•◆◇★☆※→←↑↓◎●○■□△▽▼▲@\$%\^&=\|\~\[\]{}<>:/\\()]", "", line)

        line = line.replace('\t', ' ')
        line = re.sub(r"\s+", " ", line)

        words = line.split()
        filtered_words = [w for w in words if len(w) > 2 or w.lower() in allowed_short_words]

        cleaned_line = " ".join(filtered_words)
        cleaned_lines.append(cleaned_line)

    text = "\n".join(cleaned_lines)

    for i, marker in enumerate(page_markers):
        text = text.replace(f"__PAGEMARKER_{i}__", marker)

    return text.strip()


def remover(text):
    lines = text.splitlines()
    filtered_lines = [line for line in lines if line.strip() != '']
    return '\n'.join(filtered_lines)


def howmanyans(text):
        lines = text.strip().splitlines()
        if not lines:
            print("Error: No lines found in the text.")
            return 1
    
        last_line = lines[-1].strip()
    
        match = re.match(r'^(\d+)', last_line)
        if match:
            return int(match.group(1))
        else:
            print(f"Error: Last line '{last_line}' does not match expected format.")
            return 1

def converter(folder_path, output_pdf_name="archived.pdf", delete_png_after=True):
    image_files = sorted([
        f for f in os.listdir(folder_path)
        if f.lower().endswith('.png')
    ])

    if not image_files:
        print("Error: png is not found.")
        return

    images = [Image.open(os.path.join(folder_path, f)).convert('RGB') for f in image_files]

    base_name, ext = os.path.splitext(output_pdf_name)
    output_path = os.path.join(folder_path, output_pdf_name)
    counter = 1
    while os.path.exists(output_path):
        output_pdf_name = f"{base_name}_{counter}{ext}"
        output_path = os.path.join(folder_path, output_pdf_name)
        counter += 1

    images[0].save(output_path, save_all=True, append_images=images[1:])
    print(f"pdf is created in: {output_path}")

    if delete_png_after:
        for f in image_files:
            os.remove(os.path.join(folder_path, f))
        print("png files deleted.")
