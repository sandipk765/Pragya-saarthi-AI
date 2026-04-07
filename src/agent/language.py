"""Multi-language support for Pragya-Saarthi"""

LANGUAGES = {
    "english": {
        "name": "English 🇬🇧",
        "code": "en",
        "direction": "ltr"
    },
    "hindi": {
        "name": "हिंदी 🇮🇳",
        "code": "hi",
        "direction": "ltr"
    },
    "marathi": {
        "name": "मराठी 🇮🇳",
        "code": "mr",
        "direction": "ltr"
    }
}

UI_TEXT = {
    "greeting": {
        "english": "Pragya-Saarthi — Wisdom Charioteer",
        "hindi": "प्रज्ञा-सारथी — ज्ञान का सारथी",
        "marathi": "प्रज्ञा-सारथी — ज्ञानाचा सारथी"
    },
    "subtitle": {
        "english": "Divine Guidance from the Bhagavad Gita",
        "hindi": "भगवद गीता से दिव्य मार्गदर्शन",
        "marathi": "भगवद गीतेतून दिव्य मार्गदर्शन"
    },
    "input_placeholder": {
        "english": "Share your problem or question... (career, relationships, anxiety, purpose)",
        "hindi": "अपनी समस्या या प्रश्न साझा करें... (करियर, रिश्ते, तनाव, जीवन का उद्देश्य)",
        "marathi": "तुमची समस्या किंवा प्रश्न सांगा... (करिअर, नाते, ताण, जीवनाचा उद्देश)"
    },
    "ask_button": {
        "english": "✦ Seek Wisdom ✦",
        "hindi": "✦ ज्ञान प्राप्त करें ✦",
        "marathi": "✦ ज्ञान घ्या ✦"
    },
    "thinking": {
        "english": "🕉️ Consulting the eternal wisdom of Gita...",
        "hindi": "🕉️ गीता की शाश्वत बुद्धि से परामर्श कर रहे हैं...",
        "marathi": "🕉️ गीतेच्या शाश्वत ज्ञानाचा सल्ला घेत आहोत..."
    },
    "verse_label": {
        "english": "📿 Sacred Verses",
        "hindi": "📿 पवित्र श्लोक",
        "marathi": "📿 पवित्र श्लोक"
    },
    "languages": {
        "english": "Language",
        "hindi": "भाषा",
        "marathi": "भाषा"
    },
    "clear_chat": {
        "english": "🔄 Clear Conversation",
        "hindi": "🔄 बातचीत साफ़ करें",
        "marathi": "🔄 संभाषण साफ करा"
    },
    "no_history": {
        "english": "Ask your first question to receive Gita's wisdom...",
        "hindi": "गीता का ज्ञान पाने के लिए अपना पहला प्रश्न पूछें...",
        "marathi": "गीतेचे ज्ञान मिळवण्यासाठी तुमचा पहिला प्रश्न विचारा..."
    },
    "you_asked": {
        "english": "You asked:",
        "hindi": "आपने पूछा:",
        "marathi": "तुम्ही विचारले:"
    },
    "chapter": {
        "english": "Chapter",
        "hindi": "अध्याय",
        "marathi": "अध्याय"
    },
    "verse_word": {
        "english": "Verse",
        "hindi": "श्लोक",
        "marathi": "श्लोक"
    },
    "identified_as": {
        "english": "🧘 Identified as:",
        "hindi": "🧘 समस्या का प्रकार:",
        "marathi": "🧘 ओळखले गेले:"
    },
    "agent_title": {
        "english": "Wisdom Charioteer",
        "hindi": "ज्ञान सारथी",
        "marathi": "ज्ञान सारथी"
    },
    "verses_found": {
        "english": "verses",
        "hindi": "श्लोक",
        "marathi": "श्लोक"
    },
    "welcome_title": {
        "english": "ॐ नमो भगवते वासुदेवाय",
        "hindi": "ॐ नमो भगवते वासुदेवाय",
        "marathi": "ॐ नमो भगवते वासुदेवाय"
    },
    "welcome_translation": {
        "english": "I bow to the divine Lord Vasudeva",
        "hindi": "दिव्य भगवान वासुदेव को प्रणाम",
        "marathi": "दिव्य भगवान वासुदेवाला प्रणाम"
    }
}

PROBLEM_TYPES = {
    "anxiety": {
        "english": "Anxiety & Worry",
        "hindi": "चिंता और परेशानी",
        "marathi": "चिंता आणि काळजी"
    },
    "career": {
        "english": "Career & Work",
        "hindi": "करियर और काम",
        "marathi": "करिअर आणि काम"
    },
    "relationships": {
        "english": "Relationships",
        "hindi": "रिश्ते",
        "marathi": "नाते-संबंध"
    },
    "financial": {
        "english": "Financial Stress",
        "hindi": "वित्तीय तनाव",
        "marathi": "आर्थिक ताण"
    },
    "studies": {
        "english": "Studies & Education",
        "hindi": "पढ़ाई और शिक्षा",
        "marathi": "अभ्यास आणि शिक्षण"
    },
    "grief": {
        "english": "Grief & Loss",
        "hindi": "दुःख और हानि",
        "marathi": "दुःख आणि हानी"
    },
    "purpose": {
        "english": "Life Purpose",
        "hindi": "जीवन का उद्देश्य",
        "marathi": "जीवनाचा उद्देश"
    },
    "anger": {
        "english": "Anger & Frustration",
        "hindi": "क्रोध और निराशा",
        "marathi": "राग आणि निराशा"
    },
    "fear": {
        "english": "Fear & Doubt",
        "hindi": "भय और संदेह",
        "marathi": "भीती आणि शंका"
    },
    "spiritual": {
        "english": "Spiritual Growth",
        "hindi": "आध्यात्मिक विकास",
        "marathi": "आध्यात्मिक विकास"
    },
    "mental_health": {
        "english": "Mental Well-being",
        "hindi": "मानसिक स्वास्थ्य",
        "marathi": "मानसिक आरोग्य"
    },
    "general": {
        "english": "General Guidance",
        "hindi": "सामान्य मार्गदर्शन",
        "marathi": "सामान्य मार्गदर्शन"
    }
}


def get_text(key: str, language: str) -> str:
    """Get UI text in specified language."""
    if key in UI_TEXT:
        return UI_TEXT[key].get(language, UI_TEXT[key].get("english", key))
    return key


def get_problem_type_text(problem_type: str, language: str) -> str:
    """Get problem type display text in specified language."""
    if problem_type in PROBLEM_TYPES:
        return PROBLEM_TYPES[problem_type].get(language, PROBLEM_TYPES[problem_type].get("english", problem_type))
    return problem_type.replace("_", " ").title()
