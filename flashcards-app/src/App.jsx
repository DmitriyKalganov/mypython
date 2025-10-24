import React, { useState } from 'react';
import { BookOpen, Sparkles, Plus, Trash2, RotateCw, ArrowLeftRight } from 'lucide-react';

const FlashcardApp = () => {
  const [cards, setCards] = useState([]);
  const [activeTab, setActiveTab] = useState('create');
  const [createMode, setCreateMode] = useState('ai');
  const [loading, setLoading] = useState(false);

  // AI Generation state
  const [aiTopic, setAiTopic] = useState('');
  const [aiCount, setAiCount] = useState(10);
  const [aiLanguage, setAiLanguage] = useState('ru-en');

  // Manual input state
  const [manualWord, setManualWord] = useState('');
  const [manualTranslation, setManualTranslation] = useState('');
  const [manualLang, setManualLang] = useState('ru-en');
  const [translating, setTranslating] = useState(false);

  // Study mode state
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [showStudyMode, setShowStudyMode] = useState(false);

  // Generate cards with AI
  const generateWithAI = async () => {
    if (!aiTopic.trim()) {
      alert('Пожалуйста, введите тему для генерации');
      return;
    }

    setLoading(true);
    try {
      const [fromLang, toLang] = aiLanguage.split('-');
      const fromLangName = fromLang === 'ru' ? 'русский' : 'английский';
      const toLangName = toLang === 'ru' ? 'русский' : 'английский';

      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 2000,
          messages: [
            {
              role: "user",
              content: `Создай ${aiCount} флеш-карточек для изучения языка на тему "${aiTopic}".

Язык оригинала: ${fromLangName}
Язык перевода: ${toLangName}

Верни ТОЛЬКО валидный JSON массив в следующем формате (без дополнительного текста, без markdown):
[
  {
    "front": "слово или фраза на ${fromLangName}",
    "back": "перевод на ${toLangName}"
  }
]

ВАЖНО: Верни только JSON массив, никакого другого текста!`
            }
          ]
        })
      });

      const data = await response.json();
      let responseText = data.content[0].text;

      // Remove markdown code blocks if present
      responseText = responseText.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim();

      const newCards = JSON.parse(responseText);
      setCards([...cards, ...newCards]);
      setAiTopic('');
      alert(`Создано ${newCards.length} карточек!`);
    } catch (error) {
      console.error('Error generating cards:', error);
      alert('Ошибка при генерации карточек. Попробуйте еще раз.');
    }
    setLoading(false);
  };

  // Auto-translate word
  const autoTranslate = async () => {
    if (!manualWord.trim()) return;

    setTranslating(true);
    try {
      const [fromLang, toLang] = manualLang.split('-');
      const fromLangName = fromLang === 'ru' ? 'русского' : 'английского';
      const toLangName = toLang === 'ru' ? 'русский' : 'английский';

      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 200,
          messages: [
            {
              role: "user",
              content: `Переведи с ${fromLangName} на ${toLangName}: "${manualWord}"

Верни ТОЛЬКО перевод, без дополнительного текста.`
            }
          ]
        })
      });

      const data = await response.json();
      const translation = data.content[0].text.trim();
      setManualTranslation(translation);
    } catch (error) {
      console.error('Error translating:', error);
      alert('Ошибка перевода');
    }
    setTranslating(false);
  };

  // Add manual card
  const addManualCard = () => {
    if (!manualWord.trim() || !manualTranslation.trim()) {
      alert('Заполните оба поля');
      return;
    }

    setCards([...cards, { front: manualWord, back: manualTranslation }]);
    setManualWord('');
    setManualTranslation('');
  };

  // Delete card
  const deleteCard = (index) => {
    setCards(cards.filter((_, i) => i !== index));
  };

  // Study mode functions
  const startStudy = () => {
    if (cards.length === 0) {
      alert('Сначала создайте карточки');
      return;
    }
    setShowStudyMode(true);
    setCurrentCardIndex(0);
    setIsFlipped(false);
  };

  const nextCard = () => {
    setIsFlipped(false);
    setCurrentCardIndex((currentCardIndex + 1) % cards.length);
  };

  const previousCard = () => {
    setIsFlipped(false);
    setCurrentCardIndex(currentCardIndex === 0 ? cards.length - 1 : currentCardIndex - 1);
  };

  const flipCard = () => {
    setIsFlipped(!isFlipped);
  };

  if (showStudyMode) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-2xl font-bold text-gray-800">Режим обучения</h2>
              <button
                onClick={() => setShowStudyMode(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                Выйти
              </button>
            </div>

            <div className="text-center mb-6 text-gray-600">
              Карточка {currentCardIndex + 1} из {cards.length}
            </div>

            <div
              onClick={flipCard}
              className="relative w-full h-64 cursor-pointer mb-8 perspective-1000"
            >
              <div className={`absolute w-full h-full transition-transform duration-500 transform-style-preserve-3d ${isFlipped ? 'rotate-y-180' : ''}`}>
                {/* Front */}
                <div className="absolute w-full h-full backface-hidden bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center p-8 shadow-2xl">
                  <p className="text-white text-3xl font-bold text-center">
                    {cards[currentCardIndex]?.front}
                  </p>
                </div>

                {/* Back */}
                <div className="absolute w-full h-full backface-hidden bg-gradient-to-br from-green-500 to-teal-600 rounded-2xl flex items-center justify-center p-8 shadow-2xl rotate-y-180">
                  <p className="text-white text-3xl font-bold text-center">
                    {cards[currentCardIndex]?.back}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={previousCard}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-medium"
              >
                ← Назад
              </button>
              <button
                onClick={flipCard}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium flex items-center gap-2"
              >
                <RotateCw size={20} />
                Перевернуть
              </button>
              <button
                onClick={nextCard}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-medium"
              >
                Вперед →
              </button>
            </div>
          </div>
        </div>

        <style jsx>{`
          .perspective-1000 {
            perspective: 1000px;
          }
          .transform-style-preserve-3d {
            transform-style: preserve-3d;
          }
          .backface-hidden {
            backface-visibility: hidden;
          }
          .rotate-y-180 {
            transform: rotateY(180deg);
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <BookOpen className="text-blue-600" size={40} />
            <h1 className="text-4xl font-bold text-gray-800">Флеш-карточки</h1>
          </div>
          <p className="text-gray-600">Изучайте слова с помощью ИИ или создавайте карточки вручную</p>

          <div className="mt-6 flex gap-4">
            <button
              onClick={startStudy}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-medium shadow-lg"
            >
              🎓 Начать обучение ({cards.length} карточек)
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Create Cards Section */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Создать карточки</h2>

            {/* Mode selector */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setCreateMode('ai')}
                className={`flex-1 py-3 rounded-lg font-medium transition ${
                  createMode === 'ai'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Sparkles className="inline mr-2" size={20} />
                Генерация ИИ
              </button>
              <button
                onClick={() => setCreateMode('manual')}
                className={`flex-1 py-3 rounded-lg font-medium transition ${
                  createMode === 'manual'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Plus className="inline mr-2" size={20} />
                Ручной ввод
              </button>
            </div>

            {/* AI Generation */}
            {createMode === 'ai' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Направление перевода
                  </label>
                  <select
                    value={aiLanguage}
                    onChange={(e) => setAiLanguage(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="ru-en">Русский → Английский</option>
                    <option value="en-ru">Английский → Русский</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Тема для генерации
                  </label>
                  <input
                    type="text"
                    value={aiTopic}
                    onChange={(e) => setAiTopic(e.target.value)}
                    placeholder="Например: путешествия, еда, работа..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Количество карточек: {aiCount}
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="20"
                    value={aiCount}
                    onChange={(e) => setAiCount(Number(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={generateWithAI}
                  disabled={loading}
                  className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {loading ? '⏳ Генерация...' : '✨ Сгенерировать карточки'}
                </button>
              </div>
            )}

            {/* Manual Input */}
            {createMode === 'manual' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Направление перевода
                  </label>
                  <select
                    value={manualLang}
                    onChange={(e) => setManualLang(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="ru-en">Русский → Английский</option>
                    <option value="en-ru">Английский → Русский</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {manualLang === 'ru-en' ? 'Слово на русском' : 'Word in English'}
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={manualWord}
                      onChange={(e) => setManualWord(e.target.value)}
                      placeholder={manualLang === 'ru-en' ? 'Введите слово...' : 'Enter word...'}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      onClick={autoTranslate}
                      disabled={translating || !manualWord.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ArrowLeftRight size={20} />
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {manualLang === 'ru-en' ? 'Translation' : 'Перевод'}
                  </label>
                  <input
                    type="text"
                    value={manualTranslation}
                    onChange={(e) => setManualTranslation(e.target.value)}
                    placeholder={manualLang === 'ru-en' ? 'Translation...' : 'Перевод...'}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <button
                  onClick={addManualCard}
                  className="w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium shadow-lg"
                >
                  ➕ Добавить карточку
                </button>
              </div>
            )}
          </div>

          {/* Cards List */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              Мои карточки ({cards.length})
            </h2>

            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {cards.length === 0 ? (
                <div className="text-center py-12 text-gray-400">
                  <BookOpen size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Пока нет карточек</p>
                  <p className="text-sm">Создайте их с помощью ИИ или вручную</p>
                </div>
              ) : (
                cards.map((card, index) => (
                  <div
                    key={index}
                    className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 flex justify-between items-center hover:shadow-md transition"
                  >
                    <div className="flex-1">
                      <div className="font-semibold text-gray-800">{card.front}</div>
                      <div className="text-gray-600 text-sm">→ {card.back}</div>
                    </div>
                    <button
                      onClick={() => deleteCard(index)}
                      className="ml-4 p-2 text-red-500 hover:bg-red-50 rounded-lg transition"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlashcardApp;
