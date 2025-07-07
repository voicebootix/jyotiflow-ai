import React, { useState } from 'react';
import { Globe, ChevronDown } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageSelector = ({ className = '' }) => {
  const { currentLanguage, changeLanguage, getAvailableLanguages, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  
  const languages = getAvailableLanguages();
  const currentLang = languages.find(lang => lang.code === currentLanguage);

  const handleLanguageChange = (langCode) => {
    changeLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-white hover:text-gray-200 transition-colors"
        aria-label={t('selectLanguage')}
      >
        <Globe size={18} />
        <span className="text-sm font-medium">{currentLang?.nativeName || 'English'}</span>
        <ChevronDown size={14} className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
            <div className="py-2">
              <div className="px-3 py-2 text-sm font-medium text-gray-700 border-b border-gray-100">
                {t('selectLanguage')}
              </div>
              {languages.map((language) => (
                <button
                  key={language.code}
                  onClick={() => handleLanguageChange(language.code)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-gray-50 transition-colors ${
                    language.code === currentLanguage 
                      ? 'bg-purple-50 text-purple-600 font-medium' 
                      : 'text-gray-700'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getLanguageFlag(language.code)}</span>
                    <div>
                      <div className="font-medium">{language.nativeName}</div>
                      <div className="text-xs text-gray-500">{language.name}</div>
                    </div>
                    {language.code === currentLanguage && (
                      <div className="ml-auto">
                        <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

const getLanguageFlag = (langCode) => {
  const flags = {
    'en': '🇺🇸',
    'ta': '🇮🇳',
    'hi': '🇮🇳'
  };
  return flags[langCode] || '🌐';
};

export default LanguageSelector;