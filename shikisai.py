import os
import cv2
import numpy as np
import pandas as pd
from collections import Counter
from sklearn.cluster import MiniBatchKMeans
from PIL import Image
from functools import lru_cache

# CSVファイルの場所（アプリ直下）
# Dockerコンテナでは作業ディレクトリが/appになる
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output_emo.csv')

# グローバルキャッシュでデータ読み込みを1回だけに
_emotion_mapping_cache = None

def load_emotion_mapping(path=CSV_PATH):
    """感情マッピングデータの読み込み（フォールバック機能付き）"""
    global _emotion_mapping_cache
    if _emotion_mapping_cache is None:
        # 複数のパスを試行
        possible_paths = [
            path,  # デフォルトパス
            '/app/output_emo.csv',  # Docker作業ディレクトリ
            os.path.join(os.getcwd(), 'output_emo.csv'),  # カレントディレクトリ
            'output_emo.csv'  # 相対パス
        ]
        
        for csv_path in possible_paths:
            try:
                _emotion_mapping_cache = pd.read_csv(csv_path)
                print(f"Emotion mapping loaded from {csv_path}")
                return _emotion_mapping_cache
            except FileNotFoundError:
                print(f"CSV file {csv_path} not found. Trying next path...")
                continue
            except Exception as e:
                print(f"Error loading {csv_path}: {e}")
                continue
                
        # すべてのパスで失敗した場合はエラーで停止
        error_msg = f"CSV file 'output_emo.csv' not found in any location. Tried paths: {possible_paths}"
        print(f"CRITICAL ERROR: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    return _emotion_mapping_cache

def extract_colors(image, num_colors=5, sample_size=2000):
    """色抽出（メモリ効率改善版）"""
    # 1) 低解像度リサイズ（メモリ効率向上）
    img = cv2.resize(image, (150, 100), interpolation=cv2.INTER_AREA)
    pixels = img.reshape(-1, 3)

    # 2) ピクセル数が多い場合はランダムサンプリング
    if pixels.shape[0] > sample_size:
        idx = np.random.choice(pixels.shape[0], sample_size, replace=False)
        pixels = pixels[idx]

    # 3) MiniBatchKMeans による高速クラスタリング（最適化）
    km = MiniBatchKMeans(
        n_clusters=num_colors,
        random_state=42,
        batch_size=min(sample_size, 100),  # バッチサイズ最適化
        max_iter=10,  # イテレーション数制限
        n_init=1      # 初期化回数削減
    )
    labels = km.fit_predict(pixels)

    counts = np.bincount(labels)
    centers = km.cluster_centers_
    order = counts.argsort()[::-1]
    return counts[order], centers[order]

def extract_palette_hex(image_path, num_colors=5):
    """上位色のHEXパレットを返す（保存なし）"""
    try:
        img = cv2.imread(image_path)
        if img is None:
            return []
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        _, centers = extract_colors(rgb, num_colors=num_colors)
        hex_colors = [f"#{int(c[0]):02x}{int(c[1]):02x}{int(c[2]):02x}" for c in centers]
        return hex_colors[:num_colors]
    except Exception:
        return []

def create_color_pie_chart(counts, centers, image_path):
    """円グラフ作成（無効化）"""
    # 要望によりカラーチャート生成・保存を無効化
    return ''

@lru_cache(maxsize=64)
def cached_color_distance(r, g, b, df_hash):
    """色距離計算のキャッシュ機能"""
    df = load_emotion_mapping()
    color = np.array([r, g, b])
    dists = np.linalg.norm(df[['R', 'G', 'B']].values - color, axis=1)
    idx = np.argmin(dists)
    
    # word1列以降の感情データを取得（R,G,B列を除く）
    word_cols = [col for col in df.columns if col.startswith('word')]
    
    if word_cols:
        emotions = df.iloc[idx][word_cols].dropna().tolist()
        # 空文字列を除去
        emotions = [emotion for emotion in emotions if emotion and str(emotion).strip()]
        return emotions if emotions else ['api error']
    else:
        # word列がない場合はエラー
        return ['api error']

def get_color_emotions(image_path):
    """色感情分析（最適化＆エラーハンドリング強化版）"""
    try:
        # 画像読み込み
        img = cv2.imread(image_path)
        if img is None:
            print(f"Cannot open image: {image_path}")
            return 'api error', ''
            
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        df = load_emotion_mapping()
        
        # 色抽出
        counts, centers = extract_colors(rgb)

        words = []
        df_hash = hash(tuple(df.values.flatten()))  # DataFrameのハッシュ値作成
        
        # 各色について感情を取得（キャッシュ使用）
        for c in centers:
            try:
                color_emotions = cached_color_distance(
                    int(c[0]), int(c[1]), int(c[2]), df_hash
                )
                words.extend(color_emotions)
            except Exception as e:
                print(f"Error processing color {c}: {e}")
                continue

        # 最頻感情を取得
        if words:
            top = Counter(words).most_common(1)[0][0]
        else:
            top = 'api error'  # エラー時

        # チャート作成は無効化
        chart = ''
        return top, chart
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return 'api error', ''
    except Exception as e:
        print(f"Error in color emotion analysis: {e}")
        return 'api error', ''

def get_color_emotion_candidates(image_path, top_n=5):
    """色感情分析：上位候補をスコア順で返す（ユーザー選択用）"""
    try:
        # 画像読み込み
        img = cv2.imread(image_path)
        if img is None:
            print(f"Cannot open image: {image_path}")
            return []
            
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        df = load_emotion_mapping()
        
        # 色抽出
        counts, centers = extract_colors(rgb)

        words = []
        df_hash = hash(tuple(df.values.flatten()))  # DataFrameのハッシュ値作成
        
        # 各色について感情を取得（キャッシュ使用）
        for c in centers:
            try:
                color_emotions = cached_color_distance(
                    int(c[0]), int(c[1]), int(c[2]), df_hash
                )
                words.extend(color_emotions)
            except Exception as e:
                print(f"Error processing color {c}: {e}")
                continue

        # 上位候補を取得（スコア順、同点は全て含む）
        if words:
            # 出現回数をカウント
            emotion_counts = Counter(words)
            most_common = emotion_counts.most_common()
            
            if not most_common:
                return []
            
            # 上位5位までのスコアを取得（同点を含む）
            candidates = []
            rank_limit = min(5, len(most_common))
            
            # 5位のスコアを取得
            if len(most_common) >= rank_limit:
                fifth_score = most_common[rank_limit - 1][1]
            else:
                fifth_score = 0
            
            # 5位以上のスコアを持つ感情語をすべて追加
            for emotion, count in most_common:
                if len(candidates) < rank_limit:
                    candidates.append(emotion)
                elif count >= fifth_score:
                    # 5位と同点の場合は制限を超えても追加
                    candidates.append(emotion)
                else:
                    # スコアが5位未満になったら終了
                    break
            
            return candidates
        else:
            return []  # エラー時は空リスト
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except Exception as e:
        print(f"Error in color emotion candidate analysis: {e}")
        return [] 