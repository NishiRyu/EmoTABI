/**
 * 多言語対応システム (i18n)
 * Google Translate API を使用した自動翻訳
 */

class I18n {
  constructor() {
    // 現在の言語設定を取得 (localStorage または ブラウザ設定)
    const savedLocale = localStorage.getItem('locale');
    const browserLang = navigator.language.split('-')[0];
    
    this.locale = savedLocale || (browserLang === 'ja' ? 'ja' : 'en');
    
    // 翻訳キャッシュ（ローカルストレージに保存）
    const cacheStr = localStorage.getItem('translationCache');
    this.cache = cacheStr ? JSON.parse(cacheStr) : {};
    
    // 翻訳中フラグ
    this.isTranslating = false;
  }
  
  /**
   * 現在の言語を取得
   */
  getLocale() {
    return this.locale;
  }
  
  /**
   * 言語を変更してページをリロード
   */
  async setLocale(locale) {
    if (locale !== this.locale) {
      this.locale = locale;
      localStorage.setItem('locale', locale);
      
      // HTML lang 属性を更新
      document.documentElement.lang = locale;
      
      // 日本語に戻す場合は元のテキストを復元
      if (locale === 'ja') {
        this.restoreOriginalText();
        this.restoreDynamicContent();
      } else {
        // 他の言語の場合は翻訳
        this.translatePage();
        await this.retranslateDynamicContent();
      }
      
      // 言語切り替えボタンのスタイルを更新
      this.updateLanguageButtons();
    }
  }
  
  /**
   * テキストを翻訳（バックエンド経由）
   */
  async translate(text, options = {}) {
    // 日本語モードならそのまま返す
    if (this.locale === 'ja') {
      return text;
    }
    
    // 空文字チェック
    if (!text || text.trim() === '') {
      return text;
    }
    
    const { target = this.locale, source = 'ja' } = options;
    
    // キャッシュをチェック
    const cacheKey = `${text}_${source}_${target}`;
    if (this.cache[cacheKey]) {
      return this.cache[cacheKey];
    }
    
    try {
      const response = await fetch('/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          source: source,
          target: target
        })
      });
      
      if (!response.ok) {
        console.error('翻訳エラー:', response.statusText);
        return text; // フォールバック
      }
      
      const data = await response.json();
      const translated = data.translated;
      
      // キャッシュに保存
      this.cache[cacheKey] = translated;
      localStorage.setItem('translationCache', JSON.stringify(this.cache));
      
      return translated;
      
    } catch (error) {
      console.error('翻訳処理エラー:', error);
      return text; // フォールバック
    }
  }
  
  /**
   * 複数のテキストを一度に翻訳（バッチ処理）
   */
  async translateBatch(texts, options = {}) {
    if (this.locale === 'ja') {
      return texts;
    }
    
    const { target = this.locale, source = 'ja' } = options;
    
    // キャッシュされていないテキストのみ翻訳
    const uncachedTexts = [];
    const uncachedIndices = [];
    const results = [...texts]; // コピー
    
    texts.forEach((text, index) => {
      const cacheKey = `${text}_${source}_${target}`;
      if (this.cache[cacheKey]) {
        results[index] = this.cache[cacheKey];
      } else if (text && text.trim() !== '') {
        uncachedTexts.push(text);
        uncachedIndices.push(index);
      }
    });
    
    // 全てキャッシュされていれば即座に返す
    if (uncachedTexts.length === 0) {
      return results;
    }
    
    try {
      const response = await fetch('/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: uncachedTexts,
          source: source,
          target: target
        })
      });
      
      if (!response.ok) {
        console.error('バッチ翻訳エラー:', response.statusText);
        return texts; // フォールバック
      }
      
      const data = await response.json();
      const translations = data.translated;
      
      // 結果を配列に戻し、キャッシュに保存
      translations.forEach((translated, i) => {
        const originalIndex = uncachedIndices[i];
        const originalText = uncachedTexts[i];
        results[originalIndex] = translated;
        
        const cacheKey = `${originalText}_${source}_${target}`;
        this.cache[cacheKey] = translated;
      });
      
      localStorage.setItem('translationCache', JSON.stringify(this.cache));
      
      return results;
      
    } catch (error) {
      console.error('バッチ翻訳処理エラー:', error);
      return texts; // フォールバック
    }
  }
  
  /**
   * ページ全体を翻訳
   */
  async translatePage() {
    if (this.locale === 'ja' || this.isTranslating) {
      return;
    }
    
    this.isTranslating = true;
    
    try {
      // data-i18n 属性を持つすべての要素を取得
      const elements = document.querySelectorAll('[data-i18n]');
      
      if (elements.length === 0) {
        this.isTranslating = false;
        return;
      }
      
      // 翻訳対象のテキストを収集
      const textsToTranslate = [];
      const elementsArray = Array.from(elements);
      
      elementsArray.forEach(el => {
        const originalText = el.dataset.i18nOriginal || el.textContent.trim();
        if (!el.dataset.i18nOriginal) {
          el.dataset.i18nOriginal = originalText; // 元のテキストを保存
        }
        textsToTranslate.push(originalText);
      });
      
      // バッチ翻訳を実行
      const translatedTexts = await this.translateBatch(textsToTranslate);
      
      // 翻訳結果を適用
      elementsArray.forEach((el, index) => {
        const translatedText = translatedTexts[index];
        
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          if (el.hasAttribute('placeholder')) {
            el.placeholder = translatedText;
          }
          if (el.hasAttribute('value') && el.type !== 'file') {
            el.value = translatedText;
          }
        } else {
          el.textContent = translatedText;
        }
      });
      
      console.log(`✅ ${translatedTexts.length}個のテキストを翻訳しました`);
      
    } catch (error) {
      console.error('ページ翻訳エラー:', error);
    } finally {
      this.isTranslating = false;
    }
  }
  
  /**
   * 言語切り替えボタンの状態を更新
   */
  updateLanguageButtons() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
      if (btn.dataset.lang === this.locale) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }
  
  /**
   * 日本語に戻す
   */
  restoreOriginalText() {
    let restoredCount = 0;
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const originalText = el.dataset.i18nOriginal;
      
      if (originalText) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          if (el.hasAttribute('placeholder')) {
            el.placeholder = originalText;
            restoredCount++;
          }
        } else {
          el.textContent = originalText;
          restoredCount++;
        }
      }
    });
    
    console.log(`✅ ${restoredCount}個のテキストを日本語に復元しました`);
  }
  
  /**
   * 動的コンテンツを再翻訳
   */
  async retranslateDynamicContent() {
    console.log('🔄 動的コンテンツを再翻訳中...');
    
    // 1. 色彩感情候補ボタンを再翻訳
    await this.retranslateColorCandidates();
    
    // 2. 結果画面の感情語を再翻訳
    await this.retranslateEmotions();
    
    // 3. 観光地カードを再翻訳
    await this.retranslateRecommendations();
    
    console.log('✅ 動的コンテンツの再翻訳完了');
  }
  
  /**
   * 色彩感情候補ボタンを再翻訳
   */
  async retranslateColorCandidates() {
    const buttons = document.querySelectorAll('#color-candidates .candidate-button');
    
    for (const button of buttons) {
      const originalEmotion = button.dataset.originalEmotion;
      if (originalEmotion) {
        const translated = await this.translate(originalEmotion);
        button.textContent = translated;
      }
    }
  }
  
  /**
   * 結果画面の感情語を再翻訳
   */
  async retranslateEmotions() {
    const colorEmotion = document.getElementById('color-emotion');
    const objectEmotion = document.getElementById('object-emotion');
    const atmosphereEmotion = document.getElementById('atmosphere-emotion');
    
    if (colorEmotion && colorEmotion.dataset.originalEmotion) {
      const translated = await this.translate(colorEmotion.dataset.originalEmotion);
      colorEmotion.textContent = translated;
    }
    
    if (objectEmotion && objectEmotion.dataset.originalEmotion) {
      const translated = await this.translate(objectEmotion.dataset.originalEmotion);
      objectEmotion.textContent = translated;
    }
    
    if (atmosphereEmotion && atmosphereEmotion.dataset.originalEmotion) {
      const translated = await this.translate(atmosphereEmotion.dataset.originalEmotion);
      atmosphereEmotion.textContent = translated;
    }
  }
  
  /**
   * 観光地カードを再翻訳（完全版：データを再取得）
   */
  async retranslateRecommendations() {
    // refetchRecommendations 関数が定義されているか確認
    if (typeof refetchRecommendations === 'function') {
      // 観光地データをバックエンドから再取得（観光地名と住所も英語化）
      await refetchRecommendations();
    } else {
      // フォールバック：固定テキストのみ再翻訳
      const cards = document.querySelectorAll('.recommendation-card');
      
      for (const card of cards) {
        const rating = card.querySelector('.card-rating');
        const link = card.querySelector('.card-link');
        
        if (rating && rating.dataset.originalLabel) {
          const translated = await this.translate(rating.dataset.originalLabel);
          const value = rating.dataset.ratingValue;
          rating.textContent = `${translated}: ${value}`;
        }
        
        if (link && link.dataset.originalText) {
          const translated = await this.translate(link.dataset.originalText);
          link.textContent = `${translated} →`;
        }
      }
    }
  }
  
  /**
   * 動的コンテンツを日本語に復元
   */
  restoreDynamicContent() {
    console.log('🔄 動的コンテンツを日本語に復元中...');
    
    // 1. 色彩感情候補ボタン
    const buttons = document.querySelectorAll('#color-candidates .candidate-button');
    buttons.forEach(button => {
      const original = button.dataset.originalEmotion;
      if (original) {
        button.textContent = original;
      }
    });
    
    // 2. 結果画面の感情語
    const colorEmotion = document.getElementById('color-emotion');
    const objectEmotion = document.getElementById('object-emotion');
    const atmosphereEmotion = document.getElementById('atmosphere-emotion');
    
    if (colorEmotion && colorEmotion.dataset.originalEmotion) {
      colorEmotion.textContent = colorEmotion.dataset.originalEmotion;
    }
    if (objectEmotion && objectEmotion.dataset.originalEmotion) {
      objectEmotion.textContent = objectEmotion.dataset.originalEmotion;
    }
    if (atmosphereEmotion && atmosphereEmotion.dataset.originalEmotion) {
      atmosphereEmotion.textContent = atmosphereEmotion.dataset.originalEmotion;
    }
    
    // 3. 観光地カード（完全版：データを再取得）
    if (typeof refetchRecommendations === 'function') {
      // 日本語でデータを再取得
      refetchRecommendations();
    } else {
      // フォールバック：固定テキストのみ復元
      const cards = document.querySelectorAll('.recommendation-card');
      cards.forEach(card => {
        const rating = card.querySelector('.card-rating');
        const link = card.querySelector('.card-link');
        
        if (rating && rating.dataset.originalLabel) {
          const value = rating.dataset.ratingValue;
          rating.textContent = `${rating.dataset.originalLabel}: ${value}`;
        }
        
        if (link && link.dataset.originalText) {
          link.textContent = `${link.dataset.originalText} →`;
        }
      });
    }
    
    console.log('✅ 動的コンテンツの日本語復元完了');
  }
}

// グローバルインスタンス
const i18n = new I18n();

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
  // 言語切り替えボタンの状態を設定
  i18n.updateLanguageButtons();
  
  // 英語モードならページを翻訳
  if (i18n.getLocale() === 'en') {
    setTimeout(() => {
      i18n.translatePage();
    }, 100);
  }
});

