// スクロールアニメーション用のIntersectionObserver
const animationObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      animationObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

// タイプライターエフェクト
function typeWriter(element, text, speed = 50) {
  let i = 0;
  element.textContent = '';
  
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  
  type();
}

// パーティクルエフェクト
function createParticles() {
  const hero = document.querySelector('.hero');
  const particlesCount = 50;
  
  for (let i = 0; i < particlesCount; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    particle.style.animationDelay = Math.random() * 20 + 's';
    particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
    hero.appendChild(particle);
  }
}

// カードのカスケードアニメーション
function animateCards() {
  const cards = document.querySelectorAll('.recommendation-card');
  cards.forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    
    setTimeout(() => {
      card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, index * 150);
  });
}

// 感情分析のプログレスバーアニメーション
function animateEmotionAnalysis() {
  const emotionItems = document.querySelectorAll('.emotion-item');
  
  emotionItems.forEach((item, index) => {
    const value = item.querySelector('.emotion-value');
    const originalText = value.textContent;
    
    // 初期状態
    item.style.opacity = '0';
    item.style.transform = 'scale(0.8)';
    value.textContent = '...';
    
    // アニメーション開始
    setTimeout(() => {
      item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      item.style.opacity = '1';
      item.style.transform = 'scale(1)';
      
      // テキストを元に戻す
      setTimeout(() => {
        value.style.transition = 'color 0.3s ease';
        value.style.color = '#c9a96e';
        value.textContent = originalText;
        
        setTimeout(() => {
          value.style.color = '#2c2c2c';
        }, 300);
      }, 300);
    }, index * 200);
  });
}

// 波紋エフェクト
function createRippleEffect(event) {
  const button = event.currentTarget;
  const ripple = document.createElement('span');
  const rect = button.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;
  
  ripple.style.width = ripple.style.height = size + 'px';
  ripple.style.left = x + 'px';
  ripple.style.top = y + 'px';
  ripple.classList.add('ripple');
  
  button.appendChild(ripple);
  
  setTimeout(() => {
    ripple.remove();
  }, 600);
}

// ストーリーセクションのスライドショー機能
function initStorySlideshow() {
  const images = document.querySelectorAll('.story-image');
  let currentIndex = 0;
  
  if (images.length <= 1) return;
  
  function showNextImage() {
    // 現在のアクティブな画像からactiveクラスを削除
    images[currentIndex].classList.remove('active');
    
    // 次のインデックスを計算
    currentIndex = (currentIndex + 1) % images.length;
    
    // 新しい画像にactiveクラスを追加
    images[currentIndex].classList.add('active');
  }
  
  // 4秒ごとに画像を切り替え
  setInterval(showNextImage, 4000);
}

// 基本的なDOM操作
document.addEventListener('DOMContentLoaded', function() {
  console.log('📁 [MAIN] DOM読み込み完了');
  
  // タイトルのタイプライターエフェクト
  const titleMain = document.querySelector('.hero-title-main');
  if (titleMain) {
    const originalText = titleMain.textContent;
    setTimeout(() => {
      typeWriter(titleMain, originalText, 100);
    }, 500);
  }
  
  // パーティクルエフェクト
  createParticles();
  
  // ストーリーセクションのスライドショーを初期化
  initStorySlideshow();
  
  // スクロールアニメーション用の要素を監視
  const animateElements = document.querySelectorAll('.experience-item, .story-image-container');
  animateElements.forEach(el => animationObserver.observe(el));
  
  // 送信ボタンに波紋エフェクト
  const submitButton = document.querySelector('.submit-button');
  if (submitButton) {
    submitButton.addEventListener('click', createRippleEffect);
  }
  
  // 確実な初期化のため、少し待機してから実行
  setTimeout(() => {
    console.log('📁 [MAIN] ファイルアップロード機能の初期化を開始');
    
    // ファイルアップロード機能を初期化
    initializeFileUpload();
    
    // 「その他」選択時のテキスト入力表示
    initializeOtherInputs();
    
    // モバイルナビゲーションを初期化
    initMobileNavigation();
    
    // タッチジェスチャーを初期化
    initTouchGestures();
    
    // デバイス検出と最適化
    detectDevice();
    optimizeForMobile();
    
    console.log('📁 [MAIN] 全ての初期化が完了しました');
  }, 250);
  
  // 基本的な初期化処理
  console.log('📁 [MAIN] EMOTABI_NASU loaded successfully with animations');
});

// 写真アップロード機能（LABEL要素使用 - 安定版）
function initializeFileUpload() {
  console.log('📁 [LABEL版] 写真アップロード機能を初期化');

  if (window.fileUploadInitialized) return;

  const uploadArea = document.querySelector('.upload-area');
  const uploadInput = document.getElementById('image');
  const uploadContent = document.querySelector('.upload-content');
  const uploadPreview = document.querySelector('.upload-preview');
  const previewImage = document.querySelector('.preview-image');
  const previewRemove = document.querySelector('.preview-remove');

  if (!uploadArea || !uploadInput || !uploadContent || !uploadPreview || !previewImage || !previewRemove) {
    console.error('📁 必要な要素が見つかりません');
    return;
  }

  let selectedFile = null;

  // グローバル関数
  window.getCurrentFile = function() {
    const file = selectedFile || uploadInput.files[0];
    console.log('📁 [LABEL版] getCurrentFile呼び出し - ファイル:', file ? file.name : 'なし');
    return file;
  };

  window.resetFileInput = function() {
    resetUploadState();
  };

  function resetUploadState() {
    console.log('📁 [LABEL版] アップロード状態をリセット');
    selectedFile = null;
    uploadInput.value = '';
    previewImage.src = '';
    previewImage.alt = 'プレビュー';
    uploadArea.classList.remove('drag-over');
    uploadPreview.classList.add('hidden');
    uploadContent.classList.remove('hidden');
    uploadContent.style.display = 'flex';
    uploadPreview.style.display = 'none';
  }

  function handleFileSelect(e) {
    console.log('📁 [LABEL版] ファイル選択イベント');
    
    const file = e.target.files[0];
    if (file) {
      console.log('📁 [LABEL版] ファイルが選択されました:', file.name);
      selectedFile = file;
      displayPreview(file);
    } else {
      console.log('📁 [LABEL版] ファイルが選択されませんでした');
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    if (uploadPreview.classList.contains('hidden')) {
      uploadArea.classList.add('drag-over');
    }
  }

  function handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');
  }

  function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');
    
    if (!uploadPreview.classList.contains('hidden')) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      console.log('📁 [LABEL版] ドロップされたファイル:', files[0].name);
      selectedFile = files[0];
      displayPreview(files[0]);
      
      // input要素にもファイルを設定
      try {
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(files[0]);
        uploadInput.files = dataTransfer.files;
      } catch (error) {
        console.log('📁 [LABEL版] DataTransfer設定時のエラー（無害）:', error);
      }
    }
  }

  function displayPreview(file) {
    console.log('📁 [LABEL版] プレビュー表示開始:', file.name);
    
    const reader = new FileReader();
    reader.onload = function(e) {
      previewImage.src = e.target.result;
      previewImage.alt = file.name;
      uploadContent.classList.add('hidden');
      uploadContent.style.display = 'none';
      uploadPreview.classList.remove('hidden');
      uploadPreview.style.display = 'block';
      console.log('📁 [LABEL版] プレビュー表示完了');
    };
    reader.onerror = function() {
      console.error('📁 [LABEL版] ファイル読み込みエラー');
      showError('ファイルの読み込みに失敗しました');
      resetUploadState();
    };
    reader.readAsDataURL(file);
  }

  function handlePreviewRemove(e) {
    e.preventDefault();
    e.stopPropagation();
    console.log('📁 [LABEL版] プレビュー削除');
    resetUploadState();
  }

  // イベントリスナーの設定
  uploadInput.addEventListener('change', handleFileSelect);
  uploadArea.addEventListener('dragenter', handleDragOver);
  uploadArea.addEventListener('dragover', handleDragOver);
  uploadArea.addEventListener('dragleave', handleDragLeave);
  uploadArea.addEventListener('drop', handleDrop);
  previewRemove.addEventListener('click', handlePreviewRemove);

  // 初期化
  window.fileUploadInitialized = true;
  resetUploadState();
  
  console.log('📁 [LABEL版] ファイルアップロード機能の初期化完了');
}

// テスト・デバッグ用の関数（LABEL版対応）
window.testUpload = function() {
  console.log('📁 === アップロード機能診断（LABEL版） ===');
  
  const file = window.getCurrentFile ? window.getCurrentFile() : null;
  const uploadArea = document.querySelector('.upload-area');
  const uploadInput = document.getElementById('image');
  const uploadPreview = document.querySelector('.upload-preview');
  const uploadContent = document.querySelector('.upload-content');
  const previewImage = document.querySelector('.preview-image');
  
  console.log('📁 初期化状態:', window.fileUploadInitialized ? '✅' : '❌');
  console.log('📁 現在のファイル:', file ? file.name : 'なし');
  console.log('📁 プレビュー表示:', !uploadPreview.classList.contains('hidden') ? 'ON' : 'OFF');
  console.log('📁 アップロードコンテンツ:', !uploadContent.classList.contains('hidden') ? 'ON' : 'OFF');
  console.log('📁 input要素の存在:', uploadInput ? '✅' : '❌');
  console.log('📁 input要素の値:', uploadInput ? uploadInput.value : 'N/A');
  console.log('📁 input要素のファイル数:', uploadInput ? uploadInput.files.length : 'N/A');
  console.log('📁 プレビュー画像のsrc:', previewImage.src ? '設定済み' : '未設定');
  
  if (file) {
    console.log('📁 ファイル詳細:', {
      name: file.name,
      size: file.size + ' bytes',
      type: file.type,
      lastModified: new Date(file.lastModified).toLocaleString()
    });
  }
  
  console.log('📁 === 診断完了 ===');
};

// 強制リセット用の関数
window.forceReset = function() {
  console.log('📁 [LABEL版] 強制リセット実行');
  if (window.resetFileInput) {
    window.resetFileInput();
  }
  console.log('📁 [LABEL版] 強制リセット完了');
};

// 「自分で入力」選択時のテキスト入力表示を初期化
function initializeOtherInputs() {
  function toggleOther(selId, txtId) {
    const sel = document.getElementById(selId);
    const txt = document.getElementById(txtId);
    
    if (sel && txt) {
      sel.addEventListener('change', () => {
        if (sel.value === '自分で入力') {
          txt.classList.remove('hidden');
          txt.required = true;
          txt.focus();
          // フォーカス時のアニメーション
          txt.style.transform = 'scale(1.02)';
          setTimeout(() => {
            txt.style.transform = 'scale(1)';
          }, 200);
        } else {
          txt.classList.add('hidden');
          txt.required = false;
          txt.value = '';
        }
      });
    }
  }
  
  // 目的の選択に対応（地域は固定のため削除）
  toggleOther('purpose','purpose-other');
}

// フォーム送信処理（刷新版）
document.getElementById('analyze-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  console.log('📁 フォーム送信開始');
  
  // 地域は「那須」で固定
  const region = '那須';
  
  // 目的の値を取得
  const purposeSelect = document.getElementById('purpose');
  const purposeOther = document.getElementById('purpose-other');
  
  let purpose = '';
  if (purposeSelect.value === '自分で入力') {
    if (!purposeOther.value.trim()) {
      showError('「自分で入力」を選択した場合は、目的を入力してください。');
      return;
    }
    purpose = purposeOther.value.trim();
  } else {
    if (!purposeSelect.value) {
      showError('目的を選択してください。');
      return;
    }
    purpose = purposeSelect.value;
  }
  
  // ファイルを取得
  const file = window.getCurrentFile();
  
  if (!file) {
    showError('画像をアップロードしてください。');
    return;
  }
  
  console.log('📁 送信準備完了:', {
    region: region,
    purpose: purpose,
    file: file.name,
    size: file.size + ' bytes'
  });
  
  // FormDataを作成
  const formData = new FormData();
  formData.append('region', region);
  formData.append('purpose', purpose);
  formData.append('image', file);
  
  // ローディング表示
  const loadingOverlay = document.querySelector('.loading-overlay');
  loadingOverlay.classList.add('active');
  
  try {
    console.log('📁 サーバーへ送信中（初回分析）...');
    
    const response = await fetch('/analyze', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error || 'サーバーエラーが発生しました');
    }
    
    console.log('📁 解析成功（初回）:', result);
    
    // 色彩感情選択画面を表示
    showColorSelection(result);
    
  } catch (error) {
    console.error('📁 エラー:', error);
    showError(error.message);
  } finally {
    // ローディング非表示
    loadingOverlay.classList.remove('active');
  }
});

function showError(message) {
  // エラーメッセージを表示（アニメーション付き）
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: -300px;
    background: #f8d7da;
    color: #721c24;
    padding: 12px 20px;
    border-radius: 8px;
    border: 1px solid #f5c6cb;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 3000;
    font-size: 0.9rem;
    max-width: 300px;
    transition: right 0.3s ease;
  `;
  
  errorDiv.innerHTML = `
    <strong>エラー:</strong><br>
    ${message}
  `;
  
  document.body.appendChild(errorDiv);
  
  // スライドイン
  setTimeout(() => {
    errorDiv.style.right = '20px';
  }, 100);
  
  // スライドアウト
  setTimeout(() => {
    errorDiv.style.right = '-300px';
    setTimeout(() => {
      errorDiv.remove();
    }, 300);
  }, 3000);
}

// グローバル変数（色彩感情選択用のデータを保持）
let emotionData = null;

// グローバル変数（検索結果データを保持 - 言語切り替え用）
let searchResultData = null;

async function showColorSelection(json) {
  console.log('📁 色彩感情選択画面を表示');
  
  // データを保存
  emotionData = json;
  
  // 色彩感情選択セクションを表示
  const colorSelectionSection = document.getElementById('color-selection');
  colorSelectionSection.classList.remove('hidden');
  
  // 色彩感情候補ボタンを生成
  const candidatesContainer = document.getElementById('color-candidates');
  candidatesContainer.innerHTML = '';
  
  const candidates = json.color_candidates || [];
  
  // 候補がない場合のエラーハンドリング
  if (candidates.length === 0) {
    const errorMsg = document.createElement('p');
    errorMsg.style.textAlign = 'center';
    errorMsg.style.color = '#888';
    errorMsg.textContent = '色彩感情の候補を取得できませんでした。';
    candidatesContainer.appendChild(errorMsg);
    return;
  }
  
  // 各候補のボタンを作成（翻訳付き）
  for (const emotion of candidates) {
    const button = document.createElement('button');
    button.className = 'candidate-button';
    
    // 感情語を翻訳（英語モードの場合）
    const translatedEmotion = await i18n.translate(emotion);
    button.textContent = translatedEmotion;
    
    // 元のデータを保持（バックエンドに送る用）
    button.dataset.originalEmotion = emotion;
    button.addEventListener('click', () => {
      selectColorEmotion(emotion); // 元の日本語で送信
    });
    candidatesContainer.appendChild(button);
  }
  
  // 「どれも違う」ボタンを追加
  const noneButton = document.createElement('button');
  noneButton.className = 'candidate-button none-option';
  const translatedNone = await i18n.translate('どれも違う');
  noneButton.textContent = translatedNone;
  noneButton.dataset.originalEmotion = 'どれも違う'; // 元のテキストを保存
  noneButton.addEventListener('click', () => {
    selectColorEmotion('どれも違う');
  });
  candidatesContainer.appendChild(noneButton);
  
  // 色彩感情選択セクションへスクロール
  setTimeout(() => {
    smoothScrollTo(colorSelectionSection.offsetTop - 80, 800);
  }, 300);
}

async function selectColorEmotion(selectedEmotion) {
  console.log('📁 色彩感情を選択:', selectedEmotion);
  
  // ローディング表示
  const loadingOverlay = document.querySelector('.loading-overlay');
  loadingOverlay.classList.add('active');
  
  try {
    console.log('📁 最終結果を取得中...');
    
    // /finalize エンドポイントを呼び出し
    const response = await fetch('/finalize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        selected_color_emotion: selectedEmotion,
        object_emotion: emotionData.object_emotion,
        atmosphere_emotion: emotionData.atmosphere_emotion,
        region: emotionData.region,
        purpose: emotionData.purpose,
        language: i18n.getLocale()  // 現在の言語を送信
      })
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.error || 'サーバーエラーが発生しました');
    }
    
    console.log('📁 最終結果取得成功:', result);
    
    // 検索結果データを保存（言語切り替え用）
    searchResultData = {
      selectedEmotion: selectedEmotion,
      objectEmotion: emotionData.object_emotion,
      atmosphereEmotion: emotionData.atmosphere_emotion,
      region: emotionData.region,
      purpose: emotionData.purpose,
      result: result
    };
    
    // 色彩感情選択セクションを非表示
    const colorSelectionSection = document.getElementById('color-selection');
    colorSelectionSection.classList.add('hidden');
    
    // 最終結果を表示
    await showResults(result);
    
  } catch (error) {
    console.error('📁 エラー:', error);
    showError(error.message);
  } finally {
    // ローディング非表示
    loadingOverlay.classList.remove('active');
  }
}

async function showResults(json) {
  // 結果セクションを表示
  const resultsSection = document.getElementById('results');
  resultsSection.classList.remove('hidden');
  
  // 感情分析結果を表示（翻訳付き）
  const translatedColorEmotion = await i18n.translate(json.color_emotion);
  const translatedObjectEmotion = await i18n.translate(json.object_emotion);
  const translatedAtmosphereEmotion = await i18n.translate(json.atmosphere_emotion);
  
  const colorEmotionEl = document.getElementById('color-emotion');
  const objectEmotionEl = document.getElementById('object-emotion');
  const atmosphereEmotionEl = document.getElementById('atmosphere-emotion');
  
  // 翻訳されたテキストを表示
  colorEmotionEl.textContent = translatedColorEmotion;
  objectEmotionEl.textContent = translatedObjectEmotion;
  atmosphereEmotionEl.textContent = translatedAtmosphereEmotion;
  
  // 元のテキストを保存（再翻訳用）
  colorEmotionEl.dataset.originalEmotion = json.color_emotion;
  objectEmotionEl.dataset.originalEmotion = json.object_emotion;
  atmosphereEmotionEl.dataset.originalEmotion = json.atmosphere_emotion;

  // 各感情の「詳細を見る」トグル（色彩=パレット、物体=名称、雰囲気=日本語訳）
  // 詳細UIは不要になったため処理なし
  
  // 感情分析のアニメーション
  animateEmotionAnalysis();
  
  // 推奨カードを表示（非同期対応）
  const suggestionsList = document.getElementById('suggestions-list');
  suggestionsList.innerHTML = '';
  
  // カードを順番に生成して追加
  for (let index = 0; index < json.suggestions.length; index++) {
    const item = json.suggestions[index];
    const card = await createRecommendationCard(item, index);
    suggestionsList.appendChild(card);
  }
  
  // カードアニメーション
  setTimeout(() => {
    animateCards();
  }, 500);
  
  // アンケートはシンプルな外部リンクのため、追加の表示処理は不要
  
  // 🎯 結果セクションへの自動スクロール
  scrollToResults();
}

// アンケート埋め込み・バナー機能は廃止

async function createRecommendationCard(item, index) {
  console.log(`🎯 カードを作成: ${item.name}`);
  
  const card = document.createElement('div');
  card.className = 'recommendation-card';
  
  // 画像要素の作成
  const img = document.createElement('img');
  img.className = 'card-image';
  img.alt = item.name;
  img.style.opacity = '0.5';
  img.style.transition = 'opacity 0.3s ease';
  
  // 画像読み込み成功時
  img.onload = function() {
    this.style.opacity = '1';
  };
  
  // 画像読み込みエラー時
  img.onerror = function() {
    console.warn(`画像の読み込みエラー: ${item.name}`);
    this.onerror = null;
    this.src = window.PLACEHOLDER_IMG || '/static/images/placeholder_r1.png';
    this.alt = 'プレースホルダー画像';
    this.style.opacity = '1';
  };
  
  img.src = item.photo_url;
  
  // カードコンテンツ
  const cardContent = document.createElement('div');
  cardContent.className = 'card-content';
  
  if (item.note) {
    // APIキーが設定されていない場合（翻訳対応）
    const translatedSettingNeeded = await i18n.translate('設定が必要です');
    const translatedNote = await i18n.translate(item.note);
    const translatedApiInfo = await i18n.translate('Google Maps APIキーを設定することで、実際の観光地情報と写真が表示されます。');
    
    cardContent.innerHTML = `
      <h3 class="card-title">${item.name}</h3>
      <p class="card-address">${item.addr}</p>
      <div class="api-note" style="
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px;
        margin: 12px 0;
        border-radius: 4px;
        color: #856404;
        font-size: 0.9rem;
      ">
        <strong>⚠️ ${translatedSettingNeeded}</strong><br>
        ${translatedNote}
      </div>
      <div class="api-info" style="
        background: #f8f9fa;
        padding: 12px;
        border-radius: 4px;
        color: #6c757d;
        font-size: 0.85rem;
        line-height: 1.5;
      ">
        ${translatedApiInfo}
      </div>
    `;
  } else {
    // 通常のカード（翻訳対応）
    const translatedRating = await i18n.translate('評価');
    const translatedViewMap = await i18n.translate('地図を見る');
    
    // データ取得時の言語を記録
    const currentLang = i18n.getLocale();
    
    cardContent.innerHTML = `
      <h3 class="card-title" 
          data-original-name="${item.name}" 
          data-original-lang="${currentLang}">${item.name}</h3>
      <p class="card-address" 
         data-original-address="${item.addr}" 
         data-original-lang="${currentLang}">${item.addr}</p>
      <p class="card-rating" data-original-label="評価" data-rating-value="${item.rating}">${translatedRating}: ${item.rating}</p>
      <a href="${item.url}" target="_blank" class="card-link" data-original-text="地図を見る">${translatedViewMap} →</a>
    `;
  }
  
  card.appendChild(img);
  card.appendChild(cardContent);
  
  return card;
}

// CSS アニメーション用のスタイル追加
const style = document.createElement('style');
style.textContent = `
  /* パーティクルエフェクト */
  .particle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
    pointer-events: none;
    animation: float linear infinite;
  }
  
  @keyframes float {
    0% {
      transform: translateY(100vh) rotate(0deg);
      opacity: 1;
    }
    100% {
      transform: translateY(-100px) rotate(360deg);
      opacity: 0;
    }
  }
  
  /* スクロールアニメーション */
  .animate-in {
    animation: slideInUp 0.8s ease-out;
  }
  
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(50px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* 波紋エフェクト */
  .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.6);
    transform: scale(0);
    animation: ripple-animation 0.6s ease-out;
    pointer-events: none;
  }
  
  @keyframes ripple-animation {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
  
  /* ホバー効果強化 */
  .experience-item:hover {
    transform: translateY(-8px) rotateX(5deg);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
  
  .recommendation-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
  
  /* ドラッグ&ドロップ強化 */
  .upload-area.drag-over {
    transform: scale(1.02) !important;
    border-color: #6b8e3d !important;
    background: rgba(107, 142, 61, 0.1) !important;
    box-shadow: 0 0 20px rgba(107, 142, 61, 0.3);
  }
  
  /* エラーメッセージアニメーション */
  .error-message {
    animation: none;
  }
  
  /* ローディング強化 */
  .loading-spinner {
    animation: spin 1s linear infinite, pulse 2s ease-in-out infinite;
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
  `;
  document.head.appendChild(style);

// モバイルナビゲーション機能
function initMobileNavigation() {
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');
  
  if (!navToggle || !navMenu) return;
  
  // ハンバーガーメニューのクリック
  navToggle.addEventListener('click', () => {
    navToggle.classList.toggle('active');
    navMenu.classList.toggle('mobile-active');
    
    // body のスクロールを制御
    if (navMenu.classList.contains('mobile-active')) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  });
  
  // ナビリンクのクリック時にメニューを閉じる
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navToggle.classList.remove('active');
      navMenu.classList.remove('mobile-active');
      document.body.style.overflow = '';
    });
  });
  
  // 画面サイズ変更時の処理
  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      navToggle.classList.remove('active');
      navMenu.classList.remove('mobile-active');
      document.body.style.overflow = '';
    }
  });
}

// タッチジェスチャー対応
function initTouchGestures() {
  // スライドショーにスワイプ機能を追加
  const slideshow = document.querySelector('.story-slideshow');
  if (!slideshow) return;
  
  let startX = 0;
  let startY = 0;
  let isScrolling = false;
  
  slideshow.addEventListener('touchstart', (e) => {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    isScrolling = false;
  }, { passive: true });
  
  slideshow.addEventListener('touchmove', (e) => {
    if (!startX || !startY) return;
    
    const currentX = e.touches[0].clientX;
    const currentY = e.touches[0].clientY;
    
    const diffX = Math.abs(startX - currentX);
    const diffY = Math.abs(startY - currentY);
    
    if (diffY > diffX) {
      isScrolling = true;
    }
  }, { passive: true });
  
  slideshow.addEventListener('touchend', (e) => {
    if (!startX || isScrolling) return;
    
    const endX = e.changedTouches[0].clientX;
    const diffX = startX - endX;
    
    // スワイプ閾値
    if (Math.abs(diffX) > 50) {
      if (diffX > 0) {
        // 左スワイプ - 次の画像
        triggerNextSlide();
      } else {
        // 右スワイプ - 前の画像
        triggerPrevSlide();
      }
    }
    
    startX = 0;
    startY = 0;
  }, { passive: true });
}

// スライド制御関数
function triggerNextSlide() {
  const images = document.querySelectorAll('.story-image');
  const activeImage = document.querySelector('.story-image.active');
  const currentIndex = Array.from(images).indexOf(activeImage);
  const nextIndex = (currentIndex + 1) % images.length;
  
  activeImage.classList.remove('active');
  images[nextIndex].classList.add('active');
}

function triggerPrevSlide() {
  const images = document.querySelectorAll('.story-image');
  const activeImage = document.querySelector('.story-image.active');
  const currentIndex = Array.from(images).indexOf(activeImage);
  const prevIndex = currentIndex === 0 ? images.length - 1 : currentIndex - 1;
  
  activeImage.classList.remove('active');
  images[prevIndex].classList.add('active');
}

// デバイス検出とモバイル最適化
function detectDevice() {
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const isTablet = /iPad|Android(?!.*Mobile)/i.test(navigator.userAgent);
  
  if (isMobile && !isTablet) {
    document.body.classList.add('mobile-device');
    
    // iOS Safariのビューポート調整
    if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
      document.body.classList.add('ios-device');
      
      // iOS Safariのアドレスバー問題への対処
      const setVH = () => {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
      };
      
      setVH();
      window.addEventListener('resize', setVH);
      window.addEventListener('orientationchange', () => {
        setTimeout(setVH, 100);
      });
    }
  }
  
  if (isTablet) {
    document.body.classList.add('tablet-device');
  }
}

// パフォーマンス最適化
function optimizeForMobile() {
  // 画像の遅延読み込み
  const images = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        imageObserver.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
  
  // タッチデバイスでのホバー効果を無効化
  if ('ontouchstart' in window) {
    document.body.classList.add('touch-device');
  }
}

// 🎯 感情分析結果へのスクロール機能
function scrollToResults() {
  // 少し遅延してからスクロール（DOM更新とアニメーションを待つ）
  setTimeout(() => {
    const emotionAnalysis = document.querySelector('.emotion-analysis');
    if (!emotionAnalysis) return;
    
    // ナビゲーションバーの高さを考慮したオフセット
    const navHeight = 80; // ナビバー + 余白
    const targetPosition = emotionAnalysis.offsetTop - navHeight;
    
    // スムーズスクロール（全ブラウザ対応）
    smoothScrollTo(targetPosition, 800);
    
    // 📍 スクロール後にハイライト効果
    setTimeout(() => {
      highlightEmotionResults();
    }, 900); // スクロールアニメーション完了後
    
    // 🎯 結果を見た後にアンケート誘導通知表示
    setTimeout(() => {
      // アンケートの通知表示は廃止
    }, 5000); // 5秒後に通知表示
    
    // 🎯 さらに後にCTA表示
    setTimeout(() => {
      // CTA表示は廃止
    }, 8000); // 8秒後にCTA表示（結果を見終わったタイミング）
    
  }, 300); // 結果表示アニメーションの後にスクロール
}

// アンケート関連のCTA/バナー/スクロール関数は不要のため削除

// 感情分析結果のハイライト効果
function highlightEmotionResults() {
  const emotionItems = document.querySelectorAll('.emotion-item');
  
  emotionItems.forEach((item, index) => {
    setTimeout(() => {
      // パルス効果を追加
      item.style.transform = 'scale(1.05)';
      item.style.boxShadow = '0 12px 30px rgba(107, 142, 61, 0.3)';
      item.style.transition = 'all 0.3s ease';
      
      // 元に戻す
      setTimeout(() => {
        item.style.transform = 'scale(1)';
        item.style.boxShadow = '0 8px 25px var(--color-shadow)';
      }, 600);
      
    }, index * 150); // 各アイテムを順番にハイライト
  });
}

// クロスブラウザ対応のスムーズスクロール
function smoothScrollTo(targetY, duration = 600) {
  const startY = window.pageYOffset;
  const distance = targetY - startY;
  const startTime = performance.now();
  
  // イージング関数（ease-in-out）
  function easeInOut(t) {
    return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
  }
  
  function step(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = easeInOut(progress);
    
    window.scrollTo(0, startY + distance * ease);
    
    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }
  
  // モダンブラウザではネイティブのsmoothスクロールを優先
  if ('scrollBehavior' in document.documentElement.style) {
    window.scrollTo({
      top: targetY,
      behavior: 'smooth'
    });
  } else {
    // 古いブラウザではカスタムアニメーション
    requestAnimationFrame(step);
  }
}