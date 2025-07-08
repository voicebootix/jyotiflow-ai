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
    
    // Additional Navigation
    user: "User",
    admin: "Admin",
    socialMedia: "Social Media",
    joinSacredJourney: "Join Sacred Journey",
    swamijiStory: "Swamiji's Story",
    digitalAshram: "The Digital Ashram",
    fourPillars: "Four Sacred Pillars",
    tamilHeritage: "Tamil Heritage",
    
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
    adminLogin: "Admin Login",
    welcomeBack: "Welcome back to your spiritual journey",
    emailPlaceholder: "Enter your email",
    passwordPlaceholder: "Enter your password",
    signingIn: "Signing In...",
    quickAccess: "Quick Access",
    adminAccess: "Admin",
    userAccess: "User",
    anyPassword: "any password",
    noAccount: "Don't have an account?",
    registerHere: "Register here",
    backToHome: "Back to Home",
    
    // Registration
    nameRequired: "Please enter your sacred name",
    emailRequired: "Please enter your email address",
    emailInvalid: "Please enter a valid email address",
    passwordTooShort: "Password must be at least 6 characters long",
    passwordMismatch: "Passwords do not match",
    agreeTermsRequired: "Please agree to the Terms of Service",
    birthDateRequired: "Birth date is required for accurate spiritual guidance",
    birthTimeRequired: "Birth time helps provide more precise guidance",
    birthLocationRequired: "Birth location is needed for astrological calculations",
    registerSuccessLogin: "Registration successful! Please sign in.",
    welcomeLiveChat: "Join to access live video guidance with Swami Jyotirananthan",
    welcomeSatsang: "Create your account to register for sacred community gatherings",
    welcomeClarity: "Begin your spiritual journey with personalized guidance",
    welcomeLove: "Discover divine insights about love and relationships",
    welcomePremium: "Unlock premium features including AI avatar videos",
    welcomeElite: "Access the complete spiritual transformation experience",
    welcomeDefault: "Welcome to your divine digital guidance journey",
    createAccountDefault: "Create your account for divine digital guidance",
    accountDetails: "Account Details",
    birthInformation: "Birth Information",
    createSacredAccount: "Create Your Sacred Account",
    step1Of2: "Step 1 of 2: Basic Information",
    namePlaceholder: "Your sacred name",
    createPasswordPlaceholder: "Create a secure password",
    confirmPasswordPlaceholder: "Confirm your password",
    agreeTerms: "I agree to the",
    termsOfService: "Terms of Service",
    and: "and",
    privacyPolicy: "Privacy Policy",
    subscribeNewsletter: "Subscribe to spiritual wisdom newsletter and satsang updates",
    continueToBirthDetails: "Continue to Birth Details",
    step2Of2: "Step 2 of 2: For Accurate Spiritual Guidance",
    birthDate: "Birth Date",
    birthTime: "Birth Time",
    birthLocation: "Birth Location",
    birthTimeHelp: "Exact time helps provide more accurate guidance",
    birthLocationPlaceholder: "City, State/Province, Country",
    birthLocationHelp: "Used for astrological calculations and spiritual insights",
    privacyNote: "Your birth information is kept completely private and secure. It's only used to provide accurate spiritual guidance and astrological insights.",
    creatingAccount: "Creating Account...",
    completeSacredRegistration: "Complete Sacred Registration",
    alreadyHaveAccount: "Already have an account?",
    signInToJourney: "Sign In to Your Journey",
    
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
    
    // Additional Navigation
    user: "பயனர்",
    admin: "நிர்வாகி",
    socialMedia: "சமூக ஊடகம்",
    joinSacredJourney: "புனித பயணத்தில் சேரவும்",
    swamijiStory: "ஸ்வாமிஜியின் கதை",
    digitalAshram: "டிஜிட்டல் ஆசிரமம்",
    fourPillars: "நான்கு புனித தூண்கள்",
    tamilHeritage: "தமிழ் பாரம்பரியம்",
    
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
    adminLogin: "நிர்வாக உள்நுழைவு",
    welcomeBack: "உங்கள் ஆன்மீக பயணத்திற்கு மீண்டும் வரவேற்கிறோம்",
    emailPlaceholder: "உங்கள் மின்னஞ்சலை உள்ளிடவும்",
    passwordPlaceholder: "உங்கள் கடவுச்சொல்லை உள்ளிடவும்",
    signingIn: "உள்நுழைந்து கொண்டிருக்கிறது...",
    quickAccess: "விரைவு அணுகல்",
    adminAccess: "நிர்வாகி",
    userAccess: "பயனர்",
    anyPassword: "எந்த கடவுச்சொல்",
    noAccount: "கணக்கு இல்லையா?",
    registerHere: "இங்கே பதிவு செய்யவும்",
    backToHome: "முகப்பிற்கு திரும்பு",
    
    // Registration
    nameRequired: "தயவுசெய்து உங்கள் புனித பெயரை உள்ளிடவும்",
    emailRequired: "தயவுசெய்து உங்கள் மின்னஞ்சல் முகவரியை உள்ளிடவும்",
    emailInvalid: "தயவுசெய்து சரியான மின்னஞ்சல் முகவரியை உள்ளிடவும்",
    passwordTooShort: "கடவுச்சொல் குறைந்தபட்சம் 6 எழுத்துக்கள் நீளமாக இருக்க வேண்டும்",
    passwordMismatch: "கடவுச்சொற்கள் பொருந்தவில்லை",
    agreeTermsRequired: "தயவுசெய்து சேவை நிபந்தனைகளை ஒப்புக்கொள்ளவும்",
    birthDateRequired: "துல்லியமான ஆன்மீக வழிகாட்டுதலுக்காக பிறப்பு தேதி தேவை",
    birthTimeRequired: "பிறப்பு நேரம் மிகவும் துல்லியமான வழிகாட்டுதலை வழங்க உதவுகிறது",
    birthLocationRequired: "ஜோதிட கணக்கீடுகளுக்கு பிறப்பு இடம் தேவை",
    registerSuccessLogin: "பதிவு வெற்றிகரம்! தயவுசெய்து உள்நுழைவு செய்யவும்.",
    welcomeLiveChat: "ஸ்வாமி ஜோதிரானந்தனுடன் நேரடி வீடியோ வழிகாட்டுதல் அணுக சேரவும்",
    welcomeSatsang: "புனித சமுதாய கூட்டங்களில் பதிவு செய்ய உங்கள் கணக்கை உருவாக்கவும்",
    welcomeClarity: "தனிப்பட்ட வழிகாட்டுதலுடன் உங்கள் ஆன்மீக பயணத்தை தொடங்குங்கள்",
    welcomeLove: "அன்பு மற்றும் உறவுகளைப் பற்றிய தெய்வீக நுண்ணறிவுகளைக் கண்டுபிடியுங்கள்",
    welcomePremium: "AI அவதார் வீடியோக்கள் உட்பட பிரீமியம் அம்சங்களைத் திறக்கவும்",
    welcomeElite: "முழுமையான ஆன்மீக மாற்றம் அனுபவத்தை அணுகவும்",
    welcomeDefault: "உங்கள் தெய்வீக டிஜிட்டல் வழிகாட்டுதல் பயணத்திற்கு வரவேற்கிறோம்",
    createAccountDefault: "தெய்வீக டிஜிட்டல் வழிகாட்டுதலுக்காக உங்கள் கணக்கை உருவாக்கவும்",
    accountDetails: "கணக்கு விவரங்கள்",
    birthInformation: "பிறப்பு தகவல்",
    createSacredAccount: "உங்கள் புனித கணக்கை உருவாக்கவும்",
    step1Of2: "படி 1 of 2: அடிப்படை தகவல்",
    namePlaceholder: "உங்கள் புனித பெயர்",
    createPasswordPlaceholder: "பாதுகாப்பான கடவுச்சொல்லை உருவாக்கவும்",
    confirmPasswordPlaceholder: "உங்கள் கடவுச்சொல்லை உறுதிப்படுத்துங்கள்",
    agreeTerms: "நான் ஒப்புக்கொள்கிறேன்",
    termsOfService: "சேவை நிபந்தனைகள்",
    and: "மற்றும்",
    privacyPolicy: "தனியுரிமை கொள்கை",
    subscribeNewsletter: "ஆன்மீக ஞானம் செய்திமடல் மற்றும் சத்சங்க புதுப்பிப்புகளைப் பெற சந்தா செலுத்துங்கள்",
    continueToBirthDetails: "பிறப்பு விவரங்களுக்கு தொடரவும்",
    step2Of2: "படி 2 of 2: துல்லியமான ஆன்மீக வழிகாட்டுதலுக்காக",
    birthDate: "பிறப்பு தேதி",
    birthTime: "பிறப்பு நேரம்",
    birthLocation: "பிறப்பு இடம்",
    birthTimeHelp: "சரியான நேரம் மிகவும் துல்லியமான வழிகாட்டுதலை வழங்க உதவுகிறது",
    birthLocationPlaceholder: "நகரம், மாநிலம்/மாகாணம், நாடு",
    birthLocationHelp: "ஜோதிட கணக்கீடுகள் மற்றும் ஆன்மீக நுண்ணறிவுகளுக்கு பயன்படுத்தப்படுகிறது",
    privacyNote: "உங்கள் பிறப்பு தகவல் முற்றிலும் தனிப்பட்டதாகவும் பாதுகாப்பாகவும் வைக்கப்படுகிறது. இது துல்லியமான ஆன்மீக வழிகாட்டுதல் மற்றும் ஜோதிட நுண்ணறிவுகளை வழங்க மட்டுமே பயன்படுத்தப்படுகிறது.",
    creatingAccount: "கணக்கை உருவாக்கிக்கொண்டிருக்கிறது...",
    completeSacredRegistration: "புனித பதிவை முடிக்கவும்",
    alreadyHaveAccount: "ஏற்கனவே கணக்கு உள்ளதா?",
    signInToJourney: "உங்கள் பயணத்திற்கு உள்நுழைவு செய்யவும்",
    
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
    
    // Additional Navigation
    user: "उपयोगकर्ता",
    admin: "एडमिन",
    socialMedia: "सोशल मीडिया",
    joinSacredJourney: "पवित्र यात्रा में शामिल हों",
    swamijiStory: "स्वामीजी की कहानी",
    digitalAshram: "डिजिटल आश्रम",
    fourPillars: "चार पवित्र स्तंभ",
    tamilHeritage: "तमिल विरासत",
    
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
    adminLogin: "एडमिन लॉगिन",
    welcomeBack: "आपकी आध्यात्मिक यात्रा में वापस स्वागत है",
    emailPlaceholder: "अपना ईमेल डालें",
    passwordPlaceholder: "अपना पासवर्ड डालें",
    signingIn: "साइन इन हो रहे हैं...",
    quickAccess: "त्वरित पहुँच",
    adminAccess: "एडमिन",
    userAccess: "उपयोगकर्ता",
    anyPassword: "कोई भी पासवर्ड",
    noAccount: "कोई खाता नहीं है?",
    registerHere: "यहाँ रजिस्टर करें",
    backToHome: "होम पर वापस जाएं",
    
    // Registration
    nameRequired: "कृपया अपना पवित्र नाम दर्ज करें",
    emailRequired: "कृपया अपना ईमेल पता दर्ज करें",
    emailInvalid: "कृपया एक वैध ईमेल पता दर्ज करें",
    passwordTooShort: "पासवर्ड कम से कम 6 अक्षर लंबा होना चाहिए",
    passwordMismatch: "पासवर्ड मेल नहीं खा रहे",
    agreeTermsRequired: "कृपया सेवा की शर्तों से सहमत हों",
    birthDateRequired: "सटीक आध्यात्मिक मार्गदर्शन के लिए जन्म तिथि आवश्यक है",
    birthTimeRequired: "जन्म समय अधिक सटीक मार्गदर्शन प्रदान करने में मदद करता है",
    birthLocationRequired: "ज्योतिषीय गणना के लिए जन्म स्थान आवश्यक है",
    registerSuccessLogin: "रजिस्ट्रेशन सफल! कृपया साइन इन करें।",
    welcomeLiveChat: "स्वामी ज्योतिरानंतन के साथ लाइव वीडियो मार्गदर्शन के लिए शामिल हों",
    welcomeSatsang: "पवित्र समुदायिक सभाओं के लिए पंजीकरण करने के लिए अपना खाता बनाएं",
    welcomeClarity: "व्यक्तिगत मार्गदर्शन के साथ अपनी आध्यात्मिक यात्रा शुरू करें",
    welcomeLove: "प्रेम और रिश्तों के बारे में दिव्य अंतर्दृष्टि खोजें",
    welcomePremium: "AI अवतार वीडियो सहित प्रीमियम सुविधाओं को अनलॉक करें",
    welcomeElite: "पूर्ण आध्यात्मिक परिवर्तन अनुभव तक पहुंचें",
    welcomeDefault: "आपकी दिव्य डिजिटल मार्गदर्शन यात्रा में स्वागत है",
    createAccountDefault: "दिव्य डिजिटल मार्गदर्शन के लिए अपना खाता बनाएं",
    accountDetails: "खाता विवरण",
    birthInformation: "जन्म की जानकारी",
    createSacredAccount: "अपना पवित्र खाता बनाएं",
    step1Of2: "चरण 1 of 2: बुनियादी जानकारी",
    namePlaceholder: "आपका पवित्र नाम",
    createPasswordPlaceholder: "एक सुरक्षित पासवर्ड बनाएं",
    confirmPasswordPlaceholder: "अपना पासवर्ड कन्फर्म करें",
    agreeTerms: "मैं सहमत हूं",
    termsOfService: "सेवा की शर्तें",
    and: "और",
    privacyPolicy: "गोपनीयता नीति",
    subscribeNewsletter: "आध्यात्मिक ज्ञान न्यूज़लेटर और सत्संग अपडेट के लिए सदस्यता लें",
    continueToBirthDetails: "जन्म विवरण पर जाएं",
    step2Of2: "चरण 2 of 2: सटीक आध्यात्मिक मार्गदर्शन के लिए",
    birthDate: "जन्म तिथि",
    birthTime: "जन्म समय",
    birthLocation: "जन्म स्थान",
    birthTimeHelp: "सटीक समय अधिक सटीक मार्गदर्शन प्रदान करने में मदद करता है",
    birthLocationPlaceholder: "शहर, राज्य/प्रांत, देश",
    birthLocationHelp: "ज्योतिषीय गणना और आध्यात्मिक अंतर्दृष्टि के लिए उपयोग किया जाता है",
    privacyNote: "आपकी जन्म की जानकारी पूरी तरह से निजी और सुरक्षित रखी जाती है। इसका उपयोग केवल सटीक आध्यात्मिक मार्गदर्शन और ज्योतिषीय अंतर्दृष्टि प्रदान करने के लिए किया जाता है।",
    creatingAccount: "खाता बनाया जा रहा है...",
    completeSacredRegistration: "पवित्र पंजीकरण पूरा करें",
    alreadyHaveAccount: "पहले से खाता है?",
    signInToJourney: "अपनी यात्रा में साइन इन करें",
    
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