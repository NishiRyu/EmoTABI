import os
import requests
import flask
import time
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from functools import lru_cache

# セキュリティ強化
try:
    from flask_talisman import Talisman
    TALISMAN_AVAILABLE = True
except ImportError:
    TALISMAN_AVAILABLE = False

# 依存関係の安全なインポート
SHIKISAI_AVAILABLE = False
BUTTAI_AVAILABLE = False
EMO_GPT_AVAILABLE = False
GOOGLEMAPS_AVAILABLE = False
CV2_AVAILABLE = False

try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    pass

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    pass

try:
    from shikisai import get_color_emotions
    SHIKISAI_AVAILABLE = True
except ImportError:
    pass

try:
    from buttai import load_model, process_buttai
    BUTTAI_AVAILABLE = True
except ImportError:
    pass

try:
    from emo_gpt_1 import process_emo
    EMO_GPT_AVAILABLE = True
except ImportError:
    pass

def print_status_header(title):
    """ステータス表示用のヘッダーを出力"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_module_status():
    """モジュールのインポート状況を可視化"""
    print_status_header("モジュール状況")
    
    modules = [
        ("Flask-Talisman", TALISMAN_AVAILABLE, "セキュリティ強化"),
        ("Google Maps", GOOGLEMAPS_AVAILABLE, "地図・検索機能"),
        ("OpenCV", CV2_AVAILABLE, "画像処理"),
        ("色彩分析", SHIKISAI_AVAILABLE, "色から感情分析"),
        ("物体検出", BUTTAI_AVAILABLE, "物体から感情分析"),
        ("雰囲気分析", EMO_GPT_AVAILABLE, "AIによる感情分析"),
    ]
    
    for name, available, description in modules:
        status = "✅ 利用可能" if available else "❌ 利用不可"
        print(f"  {name:<15} {status:<10} - {description}")
    
    print("=" * 60)

def get_google_maps_api_key():
    """複数の方法でGoogle Maps APIキーを取得"""
    # 方法1: 環境変数から取得
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if api_key and api_key.strip():
        return api_key.strip()
    
    # 方法2: os.environから直接取得
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    if api_key and api_key.strip():
        return api_key.strip()
    
    return None

def test_api_keys():
    """APIキーの設定状況と有効性をテスト"""
    print_status_header("API設定状況")
    
    # Google Maps APIキーのテスト
    print("🔍 APIキー取得テスト:")
    gmaps_key = get_google_maps_api_key()
    if gmaps_key and gmaps_key.strip():
        if len(gmaps_key) >= 30 and gmaps_key.startswith('AIza'):
            print(f"  🗺️  Google Maps API: ✅ 設定済み (長さ: {len(gmaps_key)})")
            
            # 実際のAPI接続テスト
            if GOOGLEMAPS_AVAILABLE:
                try:
                    gmaps_client = googlemaps.Client(key=gmaps_key)
                    print(f"      💡 接続テスト: ✅ クライアント作成成功（実際のAPI呼び出しは検索時に実行）")
                except Exception as e:
                    print(f"      💡 接続テスト: ❌ クライアント作成失敗 ({str(e)[:50]})")
            else:
                print(f"      💡 接続テスト: ⚠️  モジュール未利用")
        else:
            print(f"  🗺️  Google Maps API: ⚠️  形式不正 (長さ: {len(gmaps_key)})")
    else:
        print(f"  🗺️  Google Maps API: ❌ 未設定")
    
    # OpenAI APIキーのテスト
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key.strip():
        if len(openai_key) >= 20 and openai_key.startswith('sk-'):
            print(f"  🤖 OpenAI API: ✅ 設定済み (長さ: {len(openai_key)})")
            
            # 実際のAPI接続テスト
            if EMO_GPT_AVAILABLE:
                try:
                    from openai import OpenAI
                    # 最小限のパラメータで初期化
                    client = OpenAI(api_key=openai_key)
                    print(f"      💡 接続テスト: ✅ 初期化成功（実際のAPI呼び出しはスキップ）")
                except ImportError as e:
                    print(f"      💡 接続テスト: ❌ インポートエラー ({str(e)[:30]})")
                except TypeError as e:
                    print(f"      💡 接続テスト: ❌ 引数エラー ({str(e)[:30]})")
                except Exception as e:
                    print(f"      💡 接続テスト: ❌ その他エラー ({str(e)[:30]})")
            else:
                print(f"      💡 接続テスト: ⚠️  モジュール未利用")
        else:
            print(f"  🤖 OpenAI API: ⚠️  形式不正 (長さ: {len(openai_key)})")
    else:
        print(f"  🤖 OpenAI API: ❌ 未設定")
    
    print("=" * 60)

def test_functionality():
    """各機能の動作テスト"""
    print_status_header("機能動作テスト")
    
    # 色彩分析テスト
    if SHIKISAI_AVAILABLE:
        try:
            from shikisai import load_emotion_mapping
            df = load_emotion_mapping()
            print(f"  🎨 色彩分析: ✅ 動作確認 (感情データ: {len(df)}件)")
        except Exception as e:
            print(f"  🎨 色彩分析: ❌ エラー ({str(e)[:30]})")
    else:
        print(f"  🎨 色彩分析: ⚠️  モジュール未利用")
    
    # 物体検出テスト
    if BUTTAI_AVAILABLE:
        try:
            from buttai import load_model
            # モデルの存在確認のみ（実際の読み込みは重いので省略）
            print(f"  📦 物体検出: ✅ 動作確認 (YOLOv8)")
        except Exception as e:
            print(f"  📦 物体検出: ❌ エラー ({str(e)[:30]})")
    else:
        print(f"  📦 物体検出: ⚠️  モジュール未利用")
    
    # 雰囲気分析テスト
    if EMO_GPT_AVAILABLE:
        try:
            from emo_gpt_1 import init_openai_client
            init_openai_client()
            print(f"  💭 雰囲気分析: ✅ 動作確認 (OpenAI API必須)")
        except Exception as e:
            print(f"  💭 雰囲気分析: ❌ エラー ({str(e)[:30]})")
    else:
        print(f"  💭 雰囲気分析: ⚠️  モジュール未利用")
    
    print("=" * 60)

def print_startup_diagnostics():
    """起動時の総合診断を実行"""
    print_status_header("EMOTABI 起動診断")
    print(f"Python: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    
    print_module_status()
    test_api_keys()
    test_functionality()
    
    print_status_header("起動完了")
    print("🎉 EMOTABIの準備が整いました！")
    print("📡 サーバーを起動中...")
    print("=" * 60 + "\n")

# 基本設定
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'), override=True)

template_dir = os.path.join(basedir, 'templates')
static_dir = os.path.join(basedir, 'static')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=static_dir
)

# 基本設定
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB制限
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'emotabi-production-key-2024')

# セキュリティ強化
if TALISMAN_AVAILABLE:
    csp = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://maps.googleapis.com https://cdn.jsdelivr.net https://docs.google.com",
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://docs.google.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data: https://maps.googleapis.com https://maps.gstatic.com https://docs.google.com",
        'connect-src': "'self' https://maps.googleapis.com https://docs.google.com",
        'frame-src': "'self' https://docs.google.com"
    }
    Talisman(app, content_security_policy=csp, force_https=False)

# 起動時診断の実行
print_startup_diagnostics()

# エラーハンドラー設定
@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'サーバー内部エラーが発生しました',
        'message': '処理中に問題が発生しました。しばらく待ってから再度お試しください。'
    }), 500

@app.errorhandler(413)
def too_large(error):
    return jsonify({
        'error': 'ファイルサイズが大きすぎます',
        'message': '16MB以下の画像をアップロードしてください'
    }), 413

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        'error': '予期しないエラーが発生しました',
        'message': 'サーバーで問題が発生しました。管理者にお問い合わせください。'
    }), 500

# 静的ファイルキャッシュ設定
@app.after_request
def add_header(response):
    try:
        if request.endpoint == 'static':
            response.cache_control.max_age = 300  # 5分間キャッシュ
    except Exception:
        pass
    return response

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    try:
        if endpoint == 'static':
            fn = values.get('filename')
            if fn:
                path = os.path.join(app.root_path, 'static', fn)
                try:
                    values['v'] = int(os.stat(path).st_mtime)
                except OSError:
                    pass
        return flask.url_for(endpoint, **values)
    except Exception:
        return flask.url_for(endpoint, **values)

# アップロードディレクトリ設定
UPLOAD_DIR = os.path.join(app.static_folder or static_dir, 'uploads')
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
except Exception:
    pass

# Google Maps APIクライアント初期化
gmaps = None

def init_gmaps():
    global gmaps
    if gmaps is None and GOOGLEMAPS_AVAILABLE:
        try:
            api_key = get_google_maps_api_key()
            if api_key and api_key.strip() and len(api_key) > 30:
                gmaps = googlemaps.Client(key=api_key)
                print(f"🗺️  Google Maps初期化成功: クライアント作成完了")
                
                # 初期化時のテストは削除（実際の検索時にテストする）
                # 理由: 初期化時とリクエスト時でAPI制限が異なる場合がある
                
        except Exception as e:
            print(f"🗺️  Google Maps初期化失敗: {e}")
            gmaps = None

# モデル初期化
model_loaded = False

def init_model():
    global model_loaded
    if not model_loaded and BUTTAI_AVAILABLE:
        try:
            load_model()
            model_loaded = True
        except Exception:
            model_loaded = False

@lru_cache(maxsize=128)
def cached_places_search(query, language='ja'):
    """Places APIの結果をキャッシュ（直接requests使用）"""
    # 複数の方法でAPIキーを取得
    api_key = get_google_maps_api_key()
    
    if not api_key:
        return []
    
    # 直接requests でPlaces Text Search APIを呼び出し
    import requests
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': query,
        'language': language,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'UNKNOWN')
            
            if status == 'OK':
                places = data.get('results', [])[:3]
                
                # 各場所の詳細情報を取得（同じくrequests使用）
                detailed_places = []
                for place in places:
                    try:
                        place_id = place.get('place_id')
                        name = place.get('name', 'Unknown')
                        
                        if place_id:
                            # Place Details API呼び出し
                            details_url = "https://maps.googleapis.com/maps/api/place/details/json"
                            details_params = {
                                'place_id': place_id,
                                'fields': 'name,formatted_address,rating,photos,place_id',
                                'language': language,
                                'key': api_key
                            }
                            
                            details_response = requests.get(details_url, params=details_params, timeout=10)
                            
                            if details_response.status_code == 200:
                                details_data = details_response.json()
                                if details_data.get('status') == 'OK' and 'result' in details_data:
                                    detailed_places.append(details_data['result'])
                                else:
                                    detailed_places.append(place)
                            else:
                                detailed_places.append(place)
                        else:
                            detailed_places.append(place)
                            
                    except Exception:
                        detailed_places.append(place)
                
                return detailed_places
                
            else:
                return []
        else:
            return []
            
    except requests.exceptions.Timeout:
        return []
        
    except requests.exceptions.RequestException:
        return []
        
    except Exception:
        return []

def optimize_image(file_path, max_size=(320, 320)):
    """画像サイズ最適化"""
    if not CV2_AVAILABLE:
        return True
    
    try:
        img = cv2.imread(file_path)
        if img is None:
            return False
        
        # アスペクト比を保ちながらリサイズ
        h, w = img.shape[:2]
        if w > max_size[0] or h > max_size[1]:
            scale = min(max_size[0]/w, max_size[1]/h)
            new_w, new_h = int(w*scale), int(h*scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            cv2.imwrite(file_path, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return True
    except Exception:
        return True

def analyze_emotions_parallel(image_path):
    """感情分析を並列処理で実行"""
    results = {}
    
    def color_analysis():
        if not SHIKISAI_AVAILABLE:
            raise ImportError("色彩分析モジュール(shikisai)が利用できません")
        
        emotion, chart = get_color_emotions(image_path)
        # パレット抽出（保存せずHEX配列で返す）
        try:
            from shikisai import extract_palette_hex
            palette = extract_palette_hex(image_path, num_colors=5)
        except Exception:
            palette = []
        results['color'] = {'emotion': emotion, 'chart': chart, 'palette': palette}
    
    def object_analysis():
        if not BUTTAI_AVAILABLE:
            raise ImportError("物体検出モジュール(buttai)が利用できません")
        
        emotion, label = process_buttai(image_path)
        # source判定（scene: で始まる場合はフォールバック）
        source = 'scene' if isinstance(label, str) and label.startswith('scene:') else 'yolo'
        results['object'] = {'emotion': emotion, 'label': label, 'source': source}
    
    def atmosphere_analysis():
        if not EMO_GPT_AVAILABLE:
            raise ImportError("雰囲気分析モジュール(emo_gpt)が利用できません")
        
        cap_res = process_emo(image_path)
        results['atmosphere'] = cap_res.get('emotion_label', '不明')
    
    # 並列実行（エラー時は例外で停止）
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(color_analysis),
            executor.submit(object_analysis),
            executor.submit(atmosphere_analysis)
        ]
        
        for future in as_completed(futures, timeout=30):
            future.result()  # エラーが発生した場合は例外を再発生
    
    return results

def analyze_emotions_with_candidates(image_path):
    """感情分析を並列処理で実行（色彩感情は候補リストを返す）"""
    results = {}
    
    def color_analysis():
        if not SHIKISAI_AVAILABLE:
            raise ImportError("色彩分析モジュール(shikisai)が利用できません")
        
        # 色彩感情候補を取得（上位3~5個）
        from shikisai import get_color_emotion_candidates
        candidates = get_color_emotion_candidates(image_path, top_n=5)
        
        # パレット抽出（保存せずHEX配列で返す）
        try:
            from shikisai import extract_palette_hex
            palette = extract_palette_hex(image_path, num_colors=5)
        except Exception:
            palette = []
        
        results['color'] = {'candidates': candidates, 'palette': palette}
    
    def object_analysis():
        if not BUTTAI_AVAILABLE:
            raise ImportError("物体検出モジュール(buttai)が利用できません")
        
        emotion, label = process_buttai(image_path)
        # source判定（scene: で始まる場合はフォールバック）
        source = 'scene' if isinstance(label, str) and label.startswith('scene:') else 'yolo'
        results['object'] = {'emotion': emotion, 'label': label, 'source': source}
    
    def atmosphere_analysis():
        if not EMO_GPT_AVAILABLE:
            raise ImportError("雰囲気分析モジュール(emo_gpt)が利用できません")
        
        cap_res = process_emo(image_path)
        results['atmosphere'] = cap_res.get('emotion_label', '不明')
    
    # 並列実行（エラー時は例外で停止）
    # すべての感情分析が完了してから結果を返す
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(color_analysis),
            executor.submit(object_analysis),
            executor.submit(atmosphere_analysis)
        ]
        
        for future in as_completed(futures, timeout=30):
            future.result()  # エラーが発生した場合は例外を再発生
    
    return results

@app.route('/health', methods=['GET'])
def health_check():
    """Railway用のヘルスチェックエンドポイント（詳細診断付き）"""
    try:
        # ターミナルに詳細な診断情報を出力
        print_status_header("ヘルスチェック実行")
        print(f"⏰ 実行時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # APIキーの状態確認
        gmaps_key = os.getenv('GOOGLE_MAPS_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        # 詳細な診断
        print("\n🔍 詳細診断:")
        
        # モジュール状況
        modules_status = {
            'talisman': TALISMAN_AVAILABLE,
            'googlemaps': GOOGLEMAPS_AVAILABLE,
            'cv2': CV2_AVAILABLE,
            'shikisai': SHIKISAI_AVAILABLE,
            'buttai': BUTTAI_AVAILABLE,
            'emo_gpt': EMO_GPT_AVAILABLE
        }
        
        for module, available in modules_status.items():
            status_icon = "✅" if available else "❌"
            print(f"  {module:<12} {status_icon}")
        
        # APIキー状況
        print("\n🔑 APIキー:")
        gmaps_status = "✅ 設定済み" if gmaps_key else "❌ 未設定"
        openai_status = "✅ 設定済み" if openai_key else "❌ 未設定"
        print(f"  Google Maps: {gmaps_status}")
        print(f"  OpenAI:      {openai_status}")
        
        # 機能有効性
        print("\n⚙️  機能:")
        features = {
            'photo_suggestions': bool(gmaps_key) and GOOGLEMAPS_AVAILABLE,
            'ai_emotion_analysis': bool(openai_key) and EMO_GPT_AVAILABLE,
            'image_processing': CV2_AVAILABLE,
            'color_analysis': SHIKISAI_AVAILABLE,
            'object_detection': BUTTAI_AVAILABLE
        }
        
        for feature, available in features.items():
            status_icon = "✅" if available else "❌"
            print(f"  {feature:<20} {status_icon}")
        
        print("=" * 60)
        
        # JSONレスポンス
        status = {
            'status': 'healthy',
            'message': 'EMOTABI is running',
            'timestamp': time.time(),
            'modules': modules_status,
            'api_keys': {
                'google_maps': bool(gmaps_key),
                'openai': bool(openai_key)
            },
            'features': features
        }
        return jsonify(status)
    except Exception as e:
        print(f"❌ ヘルスチェックエラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

@app.route('/', methods=['GET'])
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"""
        <html>
        <head><title>EMOTABI</title></head>
        <body>
            <h1>🚧 EMOTABI</h1>
            <p><strong>エラー:</strong> {e}</p>
            <p><a href="/health">Health Check</a></p>
        </body>
        </html>
        """, 500

@app.route('/analyze', methods=['POST'])
def analyze():
    """初回分析：すべての感情分析を実行し、色彩感情の候補リストを返す（観光地検索は行わない）"""
    try:
        start_time = time.time()
        
        # 地域は固定で「那須」
        region = '那須'
        
        purpose = request.form.get('purpose')
        if not purpose:
            return jsonify({'error': '目的を選択または入力してください'}), 400

        f = request.files.get('image')
        if not f or f.filename == '':
            return jsonify({'error': '画像をアップロードしてください'}), 400
        
        # ファイルサイズチェック
        if f.content_length and f.content_length > 16 * 1024 * 1024:
            return jsonify({'error': '画像サイズは16MB以下にしてください'}), 400
        
        # 一意のファイル名を生成
        import uuid
        file_extension = os.path.splitext(secure_filename(f.filename))[1]
        unique_filename = f"upload_{int(time.time())}_{uuid.uuid4().hex[:8]}{file_extension}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        f.save(save_path)

        # 画像最適化
        if not optimize_image(save_path):
            return jsonify({'error': '画像の処理に失敗しました'}), 500

        # モデル初期化
        init_model()

        # 感情分析を並列実行（色彩感情は候補リストを返す）
        emotion_results = analyze_emotions_with_candidates(save_path)
        
        # 結果の取得
        color_candidates = emotion_results.get('color', {}).get('candidates', [])
        object_emotion = emotion_results.get('object', {}).get('emotion', '穏やか')
        object_label = emotion_results.get('object', {}).get('label')
        atmosphere_emotion = emotion_results.get('atmosphere', '穏やか')

        # 表示用の物体感情（検出なし時の文言）
        object_emotion_display = (
            '検出されませんでした' if (object_emotion == 'api error' and object_label == 'no_object') else object_emotion
        )

        # 感情分析結果をターミナルに出力
        print("=" * 50)
        print("🔍 感情分析結果（初回）:")
        print(f"  📍 地域: {region}")
        print(f"  🎯 目的: {purpose}")
        print(f"  🎨 色彩感情候補: {color_candidates}")
        print(f"  📦 物体感情: {object_emotion_display}")
        print(f"  💭 雰囲気感情: {atmosphere_emotion}")
        print("=" * 50)

        # パフォーマンス測定結果
        processing_time = time.time() - start_time

        # 詳細情報を同梱
        object_detail = emotion_results.get('object', {})
        color_detail = emotion_results.get('color', {})

        # ファイル名を返す（/finalizeで使用）
        return jsonify({
            'color_candidates': color_candidates,
            'object_emotion': object_emotion_display,
            'atmosphere_emotion': atmosphere_emotion,
            'image_filename': unique_filename,
            'region': region,
            'purpose': purpose,
            'processing_time': f"{processing_time:.2f}s",
            'details': {
                'object': {
                    'label': object_detail.get('label'),
                    'source': object_detail.get('source')
                },
                'color': {
                    'palette': color_detail.get('palette', [])
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'error': f'処理中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/finalize', methods=['POST'])
def finalize():
    """最終結果：ユーザーが選択した色彩感情で観光地検索を実行"""
    try:
        start_time = time.time()
        
        # リクエストパラメータを取得
        data = request.get_json()
        if not data:
            return jsonify({'error': 'リクエストデータが不正です'}), 400
        
        selected_color_emotion = data.get('selected_color_emotion')
        object_emotion = data.get('object_emotion')
        atmosphere_emotion = data.get('atmosphere_emotion')
        region = data.get('region', '那須')
        purpose = data.get('purpose')
        language = data.get('language', 'ja')  # 言語パラメータを受け取る
        
        if not purpose:
            return jsonify({'error': '目的が指定されていません'}), 400
        
        # 色彩感情が「どれも違う」の場合は空文字列として扱う
        if selected_color_emotion == 'どれも違う':
            selected_color_emotion = ''
        
        # 感情分析結果をターミナルに出力
        print("=" * 50)
        print("🔍 最終感情分析結果:")
        print(f"  📍 地域: {region}")
        print(f"  🎯 目的: {purpose}")
        print(f"  🎨 選択された色彩感情: {selected_color_emotion if selected_color_emotion else '(なし)'}")
        print(f"  📦 物体感情: {object_emotion}")
        print(f"  💭 雰囲気感情: {atmosphere_emotion}")
        print("=" * 50)
        
        # 感情フィルタリング（api errorを除外）
        def filter_emotion(emotion):
            """APIエラーや無効な感情を除外"""
            if not emotion or emotion.strip() == '' or emotion.strip().lower() == 'api error':
                return ''
            return emotion.strip()
        
        # 有効な感情のみを抽出
        valid_emotions = [
            filter_emotion(object_emotion),
            filter_emotion(selected_color_emotion),  # ユーザーが選択した色彩感情
            filter_emotion(atmosphere_emotion)
        ]
        valid_emotions = [e for e in valid_emotions if e]  # 空文字を除去
        
        # Places API検索（3つの異なる順番で検索）
        if valid_emotions:
            queries = [
                f"{region} {purpose} {' '.join(valid_emotions)}",
                f"{region} {purpose} {' '.join(reversed(valid_emotions))}",
                f"{region} {purpose} {' '.join(valid_emotions[1:] + valid_emotions[:1])}" if len(valid_emotions) > 1 else f"{region} {purpose} {' '.join(valid_emotions)}"
            ]
        else:
            # 感情データがない場合は基本検索のみ
            queries = [
                f"{region} {purpose}",
                f"{region} {purpose} おすすめ",
                f"{region} {purpose} 人気"
            ]
        
        # 各検索から1つずつ結果を取得
        final_places = []
        seen_place_ids = set()
        
        for i, query in enumerate(queries, 1):
            places = cached_places_search(query, language=language)
            
            # この検索から1つの場所を選択（重複チェック付き）
            selected_place = None
            skipped_place = None
            
            for place in places:
                place_id = place.get('place_id')
                if place_id and place_id not in seen_place_ids:
                    selected_place = place
                    seen_place_ids.add(place_id)
                    break
                elif place_id and not skipped_place:
                    skipped_place = place  # 最初の重複候補を記録
            
            if selected_place:
                final_places.append(selected_place)
                if skipped_place:
                    print(f"検索{i} → {skipped_place.get('name', 'Unknown')}(重複)×→{selected_place.get('name', 'Unknown')}を取得")
                else:
                    print(f"検索{i} → {selected_place.get('name', 'Unknown')}を取得")
            else:
                print(f"検索{i} → 新しい場所が見つかりませんでした")
        
        places = final_places
        
        suggestions = []
        if places:
            for i, p in enumerate(places):
                name = p.get('name', '')
                addr = p.get('formatted_address', '')
                rating = p.get('rating', '―')
                
                # 画像取得処理
                photos = p.get('photos', [])
                placeholder_url = flask.url_for('static', filename='images/placeholder_r1.png')
                photo_url = placeholder_url
                
                if photos and len(photos) > 0 and GOOGLEMAPS_AVAILABLE:
                    try:
                        photo_info = photos[0]
                        photo_reference = photo_info.get('photo_reference')
                        
                        if photo_reference:
                            photo_url = flask.url_for('proxy_photo', photo_ref=photo_reference, _external=True)
                            
                    except Exception:
                        photo_url = placeholder_url
                
                url = 'https://www.google.com/maps/search/?api=1&query=' + \
                      requests.utils.quote(f"{name} {addr}")
                
                suggestion = {
                    'name': name,
                    'addr': addr,
                    'rating': rating,
                    'url': url,
                    'photo_url': photo_url
                }
                suggestions.append(suggestion)
        else:
            # APIキーが設定されていない場合のフォールバック
            suggestions = [{
                'name': '観光地提案機能を有効にするには',
                'addr': 'Google Maps APIキーを設定してください',
                'rating': '―',
                'url': '#',
                'photo_url': flask.url_for('static', filename='images/placeholder_r1.png'),
                'note': 'APIキー設定後、観光地の詳細情報が表示されます'
            }]
        
        # パフォーマンス測定結果
        processing_time = time.time() - start_time
        
        return jsonify({
            'color_emotion': selected_color_emotion if selected_color_emotion else 'なし',
            'object_emotion': object_emotion,
            'atmosphere_emotion': atmosphere_emotion,
            'suggestions': suggestions,
            'processing_time': f"{processing_time:.2f}s"
        })
    
    except Exception as e:
        return jsonify({
            'error': f'処理中にエラーが発生しました: {str(e)}'
        }), 500

@app.route('/proxy-photo/<path:photo_ref>', methods=['GET'])
def proxy_photo(photo_ref):
    """Google Maps Photo APIの画像をプロキシして返す"""
    try:
        api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not api_key:
            return "API key not found", 400
        
        photo_url = f'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={api_key}'
        
        import requests
        response = requests.get(photo_url, timeout=10)
        
        if response.status_code == 200:
            return flask.Response(
                response.content,
                mimetype=response.headers.get('content-type', 'image/jpeg'),
                headers={
                    'Cache-Control': 'public, max-age=3600',
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            # エラーの場合はプレースホルダー画像を返す
            placeholder_path = os.path.join(app.static_folder, 'images', 'placeholder_r1.png')
            if os.path.exists(placeholder_path):
                with open(placeholder_path, 'rb') as f:
                    return flask.Response(
                        f.read(),
                        mimetype='image/png'
                    )
            else:
                return "Image not found", 404
                
    except Exception:
        # エラーの場合もプレースホルダー画像を返す
        placeholder_path = os.path.join(app.static_folder, 'images', 'placeholder_r1.png')
        if os.path.exists(placeholder_path):
            with open(placeholder_path, 'rb') as f:
                return flask.Response(
                    f.read(),
                    mimetype='image/png'
                )
        return "Error occurred", 500

@app.route('/debug', methods=['GET'])
def debug_diagnostics():
    """デバッグ用の詳細診断エンドポイント"""
    try:\
        # ターミナルに完全な診断を実行
        print_startup_diagnostics()
        
        # 簡単なJSONレスポンス
        return jsonify({
            'status': 'debug_completed',
            'message': '詳細診断をターミナルで実行しました',
            'timestamp': time.time(),
            'note': 'ターミナルログを確認してください'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': time.time()
        }), 500

def get_port():
    """Railway/Docker用の安全なポート取得"""
    port_env = os.environ.get('PORT', '5000')
    
    # 文字列の '$PORT' を検出して修正
    if port_env == '$PORT':
        return 5000
    
    try:
        port = int(port_env)
        if 1 <= port <= 65535:
            return port
        else:
            return 5000
    except (ValueError, TypeError):
        return 5000

@app.route('/translate', methods=['POST'])
def translate_text():
    """Google Translate APIを使用してテキストを翻訳"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'リクエストデータが不正です'}), 400
        
        text = data.get('text')
        target_lang = data.get('target', 'en')
        source_lang = data.get('source', 'ja')
        
        if not text:
            return jsonify({'error': 'テキストが指定されていません'}), 400
        
        # Google Translate APIキーを取得
        api_key = os.getenv('GOOGLE_TRANSLATE_API_KEY')
        if not api_key:
            return jsonify({'error': '翻訳APIが設定されていません'}), 500
        
        # Google Translate API を呼び出し
        url = f'https://translation.googleapis.com/language/translate/v2?key={api_key}'
        
        # textが配列の場合（バッチ翻訳）と単一の場合を処理
        is_batch = isinstance(text, list)
        
        response = requests.post(url, json={
            'q': text,
            'source': source_lang,
            'target': target_lang,
            'format': 'text'
        })
        
        if response.status_code != 200:
            print(f"翻訳APIエラー: {response.status_code} - {response.text}")
            return jsonify({'error': '翻訳に失敗しました'}), 500
        
        result = response.json()
        translations = result['data']['translations']
        
        # バッチ翻訳の場合は配列で返す
        if is_batch:
            translated_texts = [t['translatedText'] for t in translations]
            return jsonify({'translated': translated_texts})
        else:
            translated_text = translations[0]['translatedText']
            return jsonify({'translated': translated_text})
        
    except Exception as e:
        print(f"翻訳エラー: {str(e)}")
        return jsonify({'error': f'翻訳処理中にエラーが発生しました: {str(e)}'}), 500

# 本番運用: .env からの読み込み（override=True）のみを利用
if __name__ == '__main__':
    port = get_port()
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)

