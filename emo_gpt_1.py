import json
import re
import os
import base64
import time
from openai import OpenAI

# OpenAIクライアントを初期化（新API対応）
client = None

# 高速モード（1回のAPI呼び出し）を使用するかどうか
USE_FAST_MODE = True

def init_openai_client():
    """OpenAI API クライアントの遅延初期化"""
    global client
    if client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                client = OpenAI(api_key=api_key)
            except TypeError as e:
                print(f"OpenAI client initialization error (emo_gpt): {e}")
                client = None
            except Exception as e:
                print(f"OpenAI client initialization error (emo_gpt): {e}")
                client = None


def resize_and_encode_image(image_path, max_size=512):
    """画像を縮小してBase64エンコード（案2：高速化）"""
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            # cv2で読めない場合は通常のBase64エンコード
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        
        h, w = img.shape[:2]
        # 大きい画像のみ縮小
        if max(h, w) > max_size:
            scale = max_size / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # JPEGとしてエンコード（品質80%で圧縮）
        _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return base64.b64encode(buffer).decode('utf-8')
    except ImportError:
        # cv2がない場合は通常のBase64エンコード
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"Image resize error: {e}")
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')


def process_emo_fast(image_path):
    """画像から直接感情を抽出（案1：1回のAPI呼び出し）"""
    try:
        start_time = time.time()
        init_openai_client()
        if client is None:
            return None
        
        # 画像を縮小してBase64エンコード（案2）
        base64_image = resize_and_encode_image(image_path, max_size=512)
        
        messages = [
            {
                "role": "system",
                "content": (
                    "あなたは画像の雰囲気を分析する専門家です。"
                    "画像を見て、その雰囲気から連想される感情と簡潔な説明を出力してください。"
                    "出力は必ずJSONのみで返してください。"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "この画像の雰囲気を分析し、以下のJSON形式で出力してください。\n"
                            "{\n"
                            '  "emotion": "日本語の形容詞1語（例：穏やかな、壮大な、静かな、にぎやかな）",\n'
                            '  "caption": "画像の簡潔な日本語説明（30文字以内）"\n'
                            "}"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=80,
            timeout=10,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        
        elapsed = time.time() - start_time
        emotion = result.get('emotion', '')
        caption = result.get('caption', '')
        
        # ログ出力
        print("=== 雰囲気感情抽出（高速版） ===")
        print(f"抽出感情: {emotion}")
        print(f"キャプション: {caption}")
        print(f"処理時間: {elapsed:.2f}秒")
        print("==============================")
        
        if emotion and emotion != 'api error':
            return {
                'emotion_label': emotion,
                'caption': caption
            }
        else:
            return None
        
    except json.JSONDecodeError as e:
        print(f"JSON parse error in fast mode: {e}")
        # 正規表現で抽出を試みる
        try:
            emotion_match = re.search(r'"emotion"\s*:\s*"([^"]+)"', content)
            if emotion_match:
                return {
                    'emotion_label': emotion_match.group(1),
                    'caption': ''
                }
        except:
            pass
        return None
    except Exception as e:
        print(f"Fast emotion extraction error: {e}")
        return None



def generate_caption_with_vision(image_path):
    """Vision APIを使用してキャプションを生成"""
    try:
        init_openai_client()
        if client is None:
            return None
        
        # 画像をBase64エンコード
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        messages = [
            {"role": "system", "content": "あなたは画像を詳細に説明するシステムです。画像の内容を簡潔に英語で説明してください。"},
            {"role": "user", "content": [
                {"type": "text", "text": "この画像の内容を簡潔な英語で説明してください。"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=100,
            timeout=15
        )

        caption = response.choices[0].message.content.strip()
        return caption

    except Exception as e:
        print(f"Caption generation error: {e}")
        return None


def process_text_with_gpt(caption_en):
    """英語キャプションを改善→日本語翻訳→感情語抽出"""
    try:
        init_openai_client()
        if client is None:
            return None
        
        messages = [
            {
                "role": "system",
                "content": (
                    "あなたは画像キャプションの要約/翻訳の専門家です。次の厳格な制約を守ってください。"
                    "1) 出力はJSONのみ。前後の説明文・コードフェンス・余分な文字は一切含めない。"
                    "2) すべてのキーを必ず含める（空でも文字列で埋める）。"
                    "3) ダブルクォートはASCIIの\\\"のみを使用。スマートクォート不可。"
                    "4) 値は簡潔で1行（改行や装飾を入れない）。"
                    "5) improved_caption_enは自然で簡潔な英語（最大180文字）。"
                    "6) translated_caption_jpは自然な日本語（最大120文字）。"
                    "7) extracted_emotionは日本語の形容詞/形容動詞を一語のみ（例: 穏やかな, 壮大な, 静かな）。名詞や句は不可。"
                )
            },
            {
                "role": "user",
                "content": (
                    f"次の英語キャプションを基に、以下3つを作成してください。\n"
                    "1) improved_caption_en: より自然で雰囲気を表す英語（簡潔）\n"
                    "2) translated_caption_jp: 1)の日本語訳\n"
                    "3) extracted_emotion: 2)を読んだときの一般的な感情（日本語の形容詞/形容動詞で一語）\n\n"
                    f"入力:\n{caption_en}\n\n"
                    "必ず次のJSON形式のみで出力:\n"
                    "{\\\"improved_caption_en\\\":\\\"...\\\", \\\"translated_caption_jp\\\":\\\"...\\\", \\\"extracted_emotion\\\":\\\"...\\\"}"
                )
            }
        ]
        
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=240,
            temperature=0.2,  # 安定性向上のため温度を下げる
            timeout=15,
            response_format={"type": "json_object"}  # JSON強制モード
        )
        
        content = response.choices[0].message.content.strip()
        
        # JSON パース（寛容版）
        try:
            # 直接JSON解析を試行
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # JSON部分のみ抽出を試行（複数パターン）
            json_patterns = [
                r'\{.*\}',  # 基本パターン
                r'\{[^}]*"improved_caption_en"[^}]*"extracted_emotion"[^}]*\}',  # より具体的
                r'\{[^}]*"extracted_emotion"[^}]*\}',  # 最小限
            ]
            
            for pattern in json_patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group())
                        # 必要なキーが存在するかチェック
                        if 'extracted_emotion' in result:
                            return result
                    except json.JSONDecodeError:
                        continue
            
            # JSON解析が完全に失敗した場合、フォールバック処理
            print(f"JSON parsing failed, attempting fallback extraction: {content[:200]}...")
            
            # 1) まず感情語だけ抽出
            emotion_value = ''
            emotion_match = re.search(r'"extracted_emotion":\s*"([^"]+)"', content)
            if emotion_match:
                emotion_value = emotion_match.group(1)
            else:
                japanese_emotion = re.search(r'[ぁ-んァ-ヶー一-龯]{2,6}(?:い|な|的)', content)
                if japanese_emotion:
                    emotion_value = japanese_emotion.group()

            # 2) 改善英語/日本語訳を別リクエストで取得
            try:
                init_openai_client()
                if client is not None:
                    fallback_messages = [
                        {"role": "system", "content": "あなたは翻訳と言い換えの専門家です。出力は必ずJSONのみ。説明は不要。"},
                        {"role": "user", "content": f'''次の英語文を1)自然な英語に改善、2)日本語に翻訳してください。\n文: {caption_en}\n形式: {{"improved_caption_en":"...","translated_caption_jp":"..."}}'''}
                    ]
                    fb = client.chat.completions.create(
                        model='gpt-4o-mini',
                        messages=fallback_messages,
                        max_tokens=160,
                        temperature=0.2,
                        response_format={"type": "json_object"},
                        timeout=15
                    )
                    import json as _json
                    fb_payload = _json.loads(fb.choices[0].message.content)
                    return {
                        'extracted_emotion': emotion_value or 'api error',
                        'translated_caption_jp': fb_payload.get('translated_caption_jp', '—'),
                        'improved_caption_en': fb_payload.get('improved_caption_en', '')
                    }
            except Exception:
                pass

            # 3) 最低限の構造で返却
            return {
                'extracted_emotion': emotion_value or 'api error',
                'translated_caption_jp': '—',
                'improved_caption_en': ''
            }

    except Exception as e:
        print(f"Text processing error: {e}")
        return None


def process_emo_with_api(image_path):
    """新しいワークフロー：キャプション生成→改善→翻訳→感情抽出"""
    try:
        # Step 1: Vision APIでキャプション生成
        caption_en = generate_caption_with_vision(image_path)
        if not caption_en or caption_en.strip() == '':
            return {'emotion_label': 'api error', 'caption': 'Caption generation failed'}
        
        # Step 2: キャプション改善→翻訳→感情抽出
        result = process_text_with_gpt(caption_en)
        if not result or not isinstance(result, dict):
            return {'emotion_label': 'api error', 'caption': 'Text processing failed'}
        
        # 結果をemo_gpt形式に変換（より寛容に）
        emotion_label = result.get('extracted_emotion', '').strip()
        if not emotion_label or emotion_label == 'api error':
            emotion_label = 'api error'
        
        caption = result.get('translated_caption_jp', '').strip()
        if not caption:
            caption = 'キャプション生成に失敗しました'
        
        # キャプション情報をターミナルに表示
        print("=== キャプション生成結果 ===")
        print(f"元の英語: {caption_en}")
        print(f"改善版英語: {result.get('improved_caption_en', '')}")
        print(f"日本語訳: {caption}")
        print(f"抽出感情: {emotion_label}")
        print("==========================")
        
        return {
            'emotion_label': emotion_label,
            'caption': caption,
            'improved_caption_en': result.get('improved_caption_en', ''),
            'original_caption_en': caption_en
        }

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return {'emotion_label': 'api error', 'caption': f'API error: {str(e)}'}



# 画像パスを受け取り、感情分析を行う
def process_emo(image_path):
    """画像パスを受け取り、感情分析を行う
    
    USE_FAST_MODE=True: 1回のAPI呼び出しで直接感情抽出（高速）
    USE_FAST_MODE=False: 従来の2段階処理（キャプション生成→感情抽出）
    """
    
    # 画像ファイル存在チェック
    if not os.path.exists(image_path):
        return {'emotion_label': 'api error', 'caption': f'Image file not found: {image_path}'}
    
    # OpenAI APIキーチェック
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or not api_key.strip():
        return {'emotion_label': 'api error', 'caption': 'OpenAI API key is not configured'}
    
    # OpenAI API実行
    try:
        # 高速モードを試行
        if USE_FAST_MODE:
            result = process_emo_fast(image_path)
            if result and isinstance(result, dict) and 'emotion_label' in result:
                emotion = result.get('emotion_label', '').strip()
                if emotion and emotion != 'api error':
                    return result
            # 高速モード失敗時は従来モードにフォールバック
            print("⚠️ 高速モード失敗、従来モードにフォールバック...")
        
        # 従来モード
        result = process_emo_with_api(image_path)
        if result and isinstance(result, dict) and 'emotion_label' in result:
            emotion = result.get('emotion_label', '').strip()
            if emotion and emotion != 'api error':
                return result
            else:
                return {'emotion_label': 'api error', 'caption': 'No valid emotion extracted'}
        else:
            return {'emotion_label': 'api error', 'caption': 'OpenAI API returned invalid result'}
    except Exception as e:
        print(f"OpenAI API processing failed: {e}")
        return {'emotion_label': 'api error', 'caption': f'Emotion analysis failed: {str(e)}'} 