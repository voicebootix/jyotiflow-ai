import React, { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// Comprehensive translations for all UI elements
const translations = {
  en: {
    // Navigation
    home: "Home",
    spiritualGuidance: "Spiritual Guidance",
    liveChat: "Live Chat",
    satsang: "Satsang",
    birthChart: "Birth Chart",
    remedies: "Remedies",
    followUps: "Follow-ups",
    profile: "Profile",
    adminDashboard: "Admin Dashboard",
    signIn: "Sign In",
    register: "Register",
    
    // Common
    loading: "Loading...",
    submit: "Submit",
    cancel: "Cancel",
    save: "Save",
    delete: "Delete",
    edit: "Edit",
    back: "Back",
    next: "Next",
    previous: "Previous",
    refresh: "Refresh",
    
    // Authentication
    email: "Email",
    password: "Password",
    confirmPassword: "Confirm Password",
    fullName: "Full Name",
    login: "Login",
    logout: "Logout",
    loginSuccess: "Login successful!",
    loginError: "Login failed. Please check your credentials.",
    registerSuccess: "Registration successful!",
    registerError: "Registration failed. Please try again.",
    
    // Credits
    credits: "Credits",
    creditPackages: "Credit Packages",
    purchaseCredits: "Purchase Credits",
    insufficientCredits: "Insufficient credits. Please purchase more credits.",
    creditsRequired: "Credits Required",
    creditsRemaining: "Credits Remaining",
    
    // Services
    services: "Services",
    serviceTypes: "Service Types",
    audioGuidance: "Audio Guidance",
    videoGuidance: "Video Guidance",
    interactiveChat: "Interactive Chat",
    comprehensiveReading: "Comprehensive Reading",
    
    // Spiritual Guidance
    spiritualQuestion: "Your Spiritual Question",
    spiritualQuestionPlaceholder: "Ask Swamiji about your spiritual journey, relationships, career, or any guidance you seek...",
    birthDetails: "Birth Details (Optional)",
    birthDate: "Birth Date",
    birthTime: "Birth Time",
    birthLocation: "Birth Location",
    generateGuidance: "Generate Guidance",
    divineGuidance: "Divine Guidance",
    
    // Follow-ups
    followUpOptions: "Follow-up Options",
    sendEmail: "Send Email",
    sendSMS: "Send SMS",
    sendWhatsApp: "Send WhatsApp",
    followUpSent: "Follow-up sent successfully!",
    followUpError: "Failed to send follow-up. Please try again.",
    
    // Donations
    donations: "Donations",
    donateNow: "Donate Now",
    donationSuccess: "Donation successful!",
    donationError: "Donation failed. Please try again.",
    
    // Profile
    overview: "Overview",
    sessions: "Sessions",
    settings: "Settings",
    personalInfo: "Personal Information",
    
    // Admin
    users: "Users",
    content: "Content",
    analytics: "Analytics",
    pricing: "Pricing",
    revenue: "Revenue",
    
    // Errors
    errorOccurred: "An error occurred",
    tryAgain: "Please try again",
    networkError: "Network error. Please check your connection.",
    
    // Success messages
    success: "Success!",
    operationCompleted: "Operation completed successfully",
    
    // Language selection
    language: "Language",
    selectLanguage: "Select Language",
    english: "English",
    tamil: "Tamil",
    hindi: "Hindi"
  },
  
  ta: {
    // Navigation
    home: "முகப்பு",
    spiritualGuidance: "ஆன்மீக வழிகாட்டுதல்",
    liveChat: "நேரடி அரட்டை",
    satsang: "சத்சங்கம்",
    birthChart: "ஜென்ம அட்டவணை",
    remedies: "பரிகாரங்கள்",
    followUps: "பின்தொடர்தல்",
    profile: "சுயவிவரம்",
    adminDashboard: "நிர்வாக டாஷ்போர்டு",
    signIn: "உள்நுழைவு",
    register: "பதிவு",
    
    // Common
    loading: "ஏற்றுகிறது...",
    submit: "சமர்ப்பிக்கவும்",
    cancel: "ரத்து செய்",
    save: "சேமிக்கவும்",
    delete: "நீக்கவும்",
    edit: "திருத்தவும்",
    back: "பின்",
    next: "அடுத்து",
    previous: "முந்தைய",
    refresh: "புதுப்பிக்கவும்",
    
    // Authentication
    email: "மின்னஞ்சல்",
    password: "கடவுச்சொல்",
    confirmPassword: "கடவுச்சொல்லை உறுதிப்படுத்துக",
    fullName: "முழு பெயர்",
    login: "உள்நுழைவு",
    logout: "வெளியேறு",
    loginSuccess: "வெற்றிகரமாக உள்நுழைந்தீர்கள்!",
    loginError: "உள்நுழைவு தோல்வியுற்றது. உங்கள் விவரங்களை சரிபார்க்கவும்.",
    registerSuccess: "பதிவு வெற்றிகரமாக முடிந்தது!",
    registerError: "பதிவு தோல்வியுற்றது. மீண்டும் முயற்சிக்கவும்.",
    
    // Credits
    credits: "கிரெடிட்கள்",
    creditPackages: "கிரெடிட் தொகுப்புகள்",
    purchaseCredits: "கிரெடிட்கள் வாங்கவும்",
    insufficientCredits: "போதிய கிரெடிட்கள் இல்லை. மேலும் கிரெடிட்கள் வாங்கவும்.",
    creditsRequired: "தேவையான கிரெடிட்கள்",
    creditsRemaining: "மீதமுள்ள கிரெடிட்கள்",
    
    // Services
    services: "சேவைகள்",
    serviceTypes: "சேவை வகைகள்",
    audioGuidance: "ஒலி வழிகாட்டுதல்",
    videoGuidance: "வீடியோ வழிகாட்டுதல்",
    interactiveChat: "இன்டராக்டிவ் சாட்",
    comprehensiveReading: "விரிவான வாசிப்பு",
    
    // Spiritual Guidance
    spiritualQuestion: "உங்கள் ஆன்மீக கேள்வி",
    spiritualQuestionPlaceholder: "உங்கள் ஆன்மீக பயணம், உறவுகள், தொழில் அல்லது எந்த வழிகாட்டுதலையும் ஸ்வாமிஜியிடம் கேளுங்கள்...",
    birthDetails: "பிறப்பு விவரங்கள் (விருப்பமானது)",
    birthDate: "பிறப்பு தேதி",
    birthTime: "பிறப்பு நேரம்",
    birthLocation: "பிறப்பு இடம்",
    generateGuidance: "வழிகாட்டுதல் உருவாக்கவும்",
    divineGuidance: "தெய்வீக வழிகாட்டுதல்",
    
    // Follow-ups
    followUpOptions: "பின்தொடர்தல் விருப்பங்கள்",
    sendEmail: "மின்னஞ்சல் அனுப்பவும்",
    sendSMS: "SMS அனுப்பவும்",
    sendWhatsApp: "WhatsApp அனுப்பவும்",
    followUpSent: "பின்தொடர்தல் வெற்றிகரமாக அனுப்பப்பட்டது!",
    followUpError: "பின்தொடர்தல் அனுப்ப முடியவில்லை. மீண்டும் முயற்சிக்கவும்.",
    
    // Donations
    donations: "தானங்கள்",
    donateNow: "இப்போது தானம் செய்யுங்கள்",
    donationSuccess: "தானம் வெற்றிகரமாக முடிந்தது!",
    donationError: "தானம் தோல்வியுற்றது. மீண்டும் முயற்சிக்கவும்.",
    
    // Profile
    overview: "கண்ணோட்டம்",
    sessions: "அமர்வுகள்",
    settings: "அமைப்புகள்",
    personalInfo: "தனிப்பட்ட தகவல்",
    
    // Admin
    users: "பயனர்கள்",
    content: "உள்ளடக்கம்",
    analytics: "பகுப்பாய்வு",
    pricing: "விலை நிர்ணயம்",
    revenue: "வருவாய்",
    
    // Errors
    errorOccurred: "பிழை ஏற்பட்டது",
    tryAgain: "மீண்டும் முயற்சிக்கவும்",
    networkError: "நெட்வொர்க் பிழை. உங்கள் இணைப்பை சரிபார்க்கவும்.",
    
    // Success messages
    success: "வெற்றி!",
    operationCompleted: "செயல்பாடு வெற்றிகரமாக முடிந்தது",
    
    // Language selection
    language: "மொழி",
    selectLanguage: "மொழி தேர்ந்தெடுக்கவும்",
    english: "ஆங்கிலம்",
    tamil: "தமிழ்",
    hindi: "இந்தி"
  },
  
  hi: {
    // Navigation
    home: "होम",
    spiritualGuidance: "आध्यात्मिक मार्गदर्शन",
    liveChat: "लाइव चैट",
    satsang: "सत्संग",
    birthChart: "जन्म कुंडली",
    remedies: "उपाय",
    followUps: "फॉलो-अप",
    profile: "प्रोफाइल",
    adminDashboard: "एडमिन डैशबोर्ड",
    signIn: "साइन इन",
    register: "रजिस्टर",
    
    // Common
    loading: "लोड हो रहा है...",
    submit: "सबमिट करें",
    cancel: "रद्द करें",
    save: "सेव करें",
    delete: "डिलीट करें",
    edit: "एडिट करें",
    back: "वापस",
    next: "अगला",
    previous: "पिछला",
    refresh: "रिफ्रेश करें",
    
    // Authentication
    email: "ईमेल",
    password: "पासवर्ड",
    confirmPassword: "पासवर्ड कन्फर्म करें",
    fullName: "पूरा नाम",
    login: "लॉगिन",
    logout: "लॉगआउट",
    loginSuccess: "सफलतापूर्वक लॉगिन हो गए!",
    loginError: "लॉगिन असफल। कृपया अपनी जानकारी जांचें।",
    registerSuccess: "रजिस्ट्रेशन सफल!",
    registerError: "रजिस्ट्रेशन असफल। कृपया फिर से कोशिश करें।",
    
    // Credits
    credits: "क्रेडिट",
    creditPackages: "क्रेडिट पैकेज",
    purchaseCredits: "क्रेडिट खरीदें",
    insufficientCredits: "अपर्याप्त क्रेडिट। कृपया अधिक क्रेडिट खरीदें।",
    creditsRequired: "आवश्यक क्रेडिट",
    creditsRemaining: "बचे हुए क्रेडिट",
    
    // Services
    services: "सेवाएं",
    serviceTypes: "सेवा प्रकार",
    audioGuidance: "ऑडियो मार्गदर्शन",
    videoGuidance: "वीडियो मार्गदर्शन",
    interactiveChat: "इंटरैक्टिव चैट",
    comprehensiveReading: "व्यापक रीडिंग",
    
    // Spiritual Guidance
    spiritualQuestion: "आपका आध्यात्मिक प्रश्न",
    spiritualQuestionPlaceholder: "अपनी आध्यात्मिक यात्रा, रिश्तों, करियर या किसी भी मार्गदर्शन के बारे में स्वामीजी से पूछें...",
    birthDetails: "जन्म विवरण (वैकल्पिक)",
    birthDate: "जन्म तिथि",
    birthTime: "जन्म समय",
    birthLocation: "जन्म स्थान",
    generateGuidance: "मार्गदर्शन जेनरेट करें",
    divineGuidance: "दिव्य मार्गदर्शन",
    
    // Follow-ups
    followUpOptions: "फॉलो-अप विकल्प",
    sendEmail: "ईमेल भेजें",
    sendSMS: "SMS भेजें",
    sendWhatsApp: "WhatsApp भेजें",
    followUpSent: "फॉलो-अप सफलतापूर्वक भेजा गया!",
    followUpError: "फॉलो-अप भेजने में असफल। कृपया फिर से कोशिश करें।",
    
    // Donations
    donations: "दान",
    donateNow: "अभी दान करें",
    donationSuccess: "दान सफल!",
    donationError: "दान असफल। कृपया फिर से कोशिश करें।",
    
    // Profile
    overview: "अवलोकन",
    sessions: "सत्र",
    settings: "सेटिंग्स",
    personalInfo: "व्यक्तिगत जानकारी",
    
    // Admin
    users: "उपयोगकर्ता",
    content: "सामग्री",
    analytics: "एनालिटिक्स",
    pricing: "मूल्य निर्धारण",
    revenue: "राजस्व",
    
    // Errors
    errorOccurred: "एक त्रुटि हुई",
    tryAgain: "कृपया फिर से कोशिश करें",
    networkError: "नेटवर्क त्रुटि। कृपया अपना कनेक्शन जांचें।",
    
    // Success messages
    success: "सफलता!",
    operationCompleted: "ऑपरेशन सफलतापूर्वक पूर्ण हुआ",
    
    // Language selection
    language: "भाषा",
    selectLanguage: "भाषा चुनें",
    english: "अंग्रेजी",
    tamil: "तमिल",
    hindi: "हिंदी"
  }
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    return localStorage.getItem('jyotiflow_language') || 'en';
  });

  useEffect(() => {
    localStorage.setItem('jyotiflow_language', currentLanguage);
    document.documentElement.lang = currentLanguage;
  }, [currentLanguage]);

  const t = (key, fallback = '') => {
    const translation = translations[currentLanguage]?.[key] || translations.en[key] || fallback || key;
    return translation;
  };

  const changeLanguage = (language) => {
    if (translations[language]) {
      setCurrentLanguage(language);
    }
  };

  const getAvailableLanguages = () => [
    { code: 'en', name: 'English', nativeName: 'English' },
    { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
    { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' }
  ];

  const value = {
    currentLanguage,
    changeLanguage,
    t,
    getAvailableLanguages,
    isRTL: false // None of our languages are RTL
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export default LanguageProvider;