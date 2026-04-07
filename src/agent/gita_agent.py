"""
Pragya-Saarthi — AI Agent
Supports Grok (xAI) via xgrok library or OpenAI-compatible API.
Offline mode builds a TRULY unique answer from every word in the query.
"""

import os, json, re, sys, hashlib
from pathlib import Path
from typing import Dict, List, Any

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass

GROK_AVAILABLE = False
USE_OPENAI_CLIENT = False
try:
    import xgrok

    GROK_AVAILABLE = True
except ImportError:
    try:
        from openai import OpenAI

        GROK_AVAILABLE = True
        USE_OPENAI_CLIENT = True
    except ImportError:
        pass

sys.path.append(str(Path(__file__).parent.parent))
from agent.prompt_templates import SYSTEM_PROMPT, QUERY_TEMPLATE
from retrieval.vector_store import GitaVectorStore


class PragyaSaarthiAgent:
    _MODEL_CANDIDATES = [
        "grok-2",
        "grok-2-vision",
        "grok-beta",
    ]

    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY", "").strip()
        self.model = None
        self.client = None
        self.vector_store = GitaVectorStore()
        self.conversation_history: List[Dict] = []
        self._setup_grok()

    # ── Setup ──────────────────────────────────────────────────────────────────
    def _setup_grok(self):
        if not GROK_AVAILABLE:
            print("[WARNING] No Grok SDK. Running offline.")
            return
        if not self.api_key:
            print("[WARNING] XAI_API_KEY not set. Running offline.")
            return
        if USE_OPENAI_CLIENT:
            self._setup_openai_client()
        else:
            self._setup_xgrok()

    def _setup_xgrok(self):
        try:
            self.client = xgrok.Client(api_key=self.api_key)
            for c in self._MODEL_CANDIDATES:
                try:
                    self.client.chat.completions.create(
                        model=c,
                        messages=[{"role": "user", "content": "hi"}],
                        max_tokens=5,
                    )
                    self.model = c
                    print(f"[OK] xgrok → {self.model}")
                    return
                except Exception:
                    continue
            print("[WARNING] No accessible model. Running offline.")
            self.client = None
        except Exception as e:
            print(f"[ERROR] {e}")
            self.client = None

    def _setup_openai_client(self):
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
            )
            for c in self._MODEL_CANDIDATES:
                try:
                    self.client.chat.completions.create(
                        model=c,
                        messages=[{"role": "user", "content": "hi"}],
                        max_tokens=5,
                    )
                    self.model = c
                    print(f"[OK] Grok (OpenAI compat) → {self.model}")
                    return
                except Exception:
                    continue
            print("[WARNING] No accessible model. Running offline.")
            self.client = None
        except Exception as e:
            print(f"[ERROR] {e}")
            self.client = None

    # ── Public API ─────────────────────────────────────────────────────────────
    def get_response(self, query: str, language: str = "english") -> Dict[str, Any]:
        retrieved_verses = self.vector_store.search(query, top_k=4)
        is_online = self.client is not None
        if is_online:
            response = self._get_grok_response(query, retrieved_verses)
        else:
            response = self._build_unique_offline_response(
                query, retrieved_verses, language
            )
        response = self._enrich_verses(response, retrieved_verses)
        self.conversation_history.append(
            {"query": query, "response": response, "language": language}
        )
        return response

    # ── Grok ─────────────────────────────────────────────────────────────────
    def _build_prompt(self, query: str, context_verses: List[Dict]) -> str:
        verse_context = "\n\nMost relevant Gita verses:\n"
        for v in context_verses:
            verse_context += f"  Ch.{v['chapter']}:{v['verse']}: {v.get('english', '')[:120]} [Topic: {v.get('topic', '')}]\n"
        history_ctx = ""
        if self.conversation_history:
            recent = self.conversation_history[-2:]
            history_ctx = "\nRecent context:\n" + "\n".join(
                f"  Q: {t['query'][:80]}" for t in recent
            )
        return QUERY_TEMPLATE.format(query=query) + verse_context + history_ctx

    def _get_grok_response(self, query: str, context_verses: List[Dict]) -> Dict:
        prompt = self._build_prompt(query, context_verses)
        try:
            raw = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.9,
                    max_tokens=3000,
                )
                .choices[0]
                .message.content.strip()
            )
            return self._parse_json_response(raw)
        except Exception as e:
            print(f"[ERROR] Grok API error: {e}")
            return self._build_unique_offline_response(query, context_verses)

    # ── JSON Parsing ───────────────────────────────────────────────────────────
    def _parse_json_response(self, raw: str) -> Dict:
        cleaned = re.sub(r"```(?:json)?\s*", "", raw)
        cleaned = re.sub(r"```\s*$", "", cleaned).strip()
        for attempt in [
            cleaned,
            (
                re.search(r"\{.*\}", cleaned, re.DOTALL)
                or type("", (), {"group": lambda s: ""})()
            ).group(),
        ]:
            if not attempt:
                continue
            for text in [attempt, re.sub(r",\s*([}\]])", r"\1", attempt)]:
                try:
                    return self._normalize(json.loads(text))
                except:
                    continue
        return {
            "problem_type": "general",
            "answer": {
                "english": raw[:1500] if raw else "Seek the wisdom within.",
                "hindi": "भगवद गीता की शाश्वत शिक्षा आपकी यात्रा को प्रकाशित करे।",
                "marathi": "भगवद गीतेची शाश्वत शिकवण तुमच्या मार्गाला प्रकाशित करो।",
            },
            "four_day_guide": {},
            "verses": [],
            "key_teaching": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
            "key_teaching_meaning": {
                "english": "You have a right to your actions, never to the fruits.",
                "hindi": "कर्म में ही अधिकार है, फल में नहीं।",
                "marathi": "कर्मातच अधिकार आहे, फळात नाही.",
            },
        }

    def _normalize(self, data: dict) -> Dict:
        def pick(*keys):
            for k in keys:
                v = data.get(k, "")
                if v:
                    return v
            return ""

        ae = pick("answer_english", "answer")
        ah = pick("answer_hindi")
        am = pick("answer_marathi")
        if isinstance(ae, dict):
            ah = ah or ae.get("hindi", "")
            am = am or ae.get("marathi", "")
            ae = ae.get("english", "")
        if not ah and isinstance(data.get("answer"), dict):
            ah = data["answer"].get("hindi", "")
        if not am and isinstance(data.get("answer"), dict):
            am = data["answer"].get("marathi", "")
        ktm = data.get("key_teaching_meaning", {})
        if not isinstance(ktm, dict):
            ktm = {}
        guide = data.get("four_day_guide", {})
        if isinstance(guide, dict) and "days" not in guide:
            guide = {}
        return {
            "problem_type": data.get("problem_type", "general"),
            "answer": {"english": ae, "hindi": ah, "marathi": am},
            "four_day_guide": guide,
            "verses": data.get("verses", []),
            "key_teaching": data.get("key_teaching", ""),
            "key_teaching_meaning": {
                "english": ktm.get("english", ""),
                "hindi": ktm.get("hindi", ""),
                "marathi": ktm.get("marathi", ""),
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # UNIQUE OFFLINE ENGINE
    # Every answer is built word-by-word from what the user actually typed.
    # ══════════════════════════════════════════════════════════════════════════
    def _build_unique_offline_response(
        self, query: str, verses: List[Dict], language: str = "english"
    ) -> Dict:
        q = query.strip()
        q_lower = q.lower()
        ptype = self._classify_problem(q_lower)

        # ── 1. Extract specific details from the query ─────────────────────────
        # Key words (removes stop words)
        stop = {
            "i",
            "am",
            "is",
            "are",
            "my",
            "me",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "this",
            "that",
            "it",
            "be",
            "was",
            "have",
            "feel",
            "feeling",
            "very",
            "so",
            "too",
            "not",
            "no",
            "can",
            "cannot",
            "how",
            "what",
            "why",
            "when",
            "please",
            "help",
            "tell",
            "about",
            "just",
            "really",
            "do",
            "does",
            "will",
            "would",
            "should",
            "could",
            "been",
            "they",
            "them",
            "their",
            "we",
            "us",
            "our",
            "you",
            "your",
            "its",
            "also",
            "some",
            "any",
            "all",
            "if",
            "then",
            "than",
            "from",
            "had",
            "has",
            "who",
            "which",
            "there",
            "here",
            "after",
            "before",
        }
        raw_words = re.findall(r"[a-zA-Z\u0900-\u097F]+", q)
        key_words = [w for w in raw_words if w.lower() not in stop and len(w) > 3]

        # First meaningful phrase (up to 6 words) — THE person's own words
        first_phrase = " ".join(key_words[:6]) if key_words else ptype

        # Detect named people (capitalized words that are not first word)
        people = [w for w in raw_words[1:] if w[0].isupper() and w.lower() not in stop]
        person_ref = people[0] if people else ""

        # Detect numbers (age, years, months, days)
        numbers = re.findall(r"\b\d+\b", q)
        number_ctx = numbers[0] if numbers else ""

        # Detect emotion intensity words
        intense = any(
            w in q_lower
            for w in [
                "very",
                "extremely",
                "so much",
                "unbearable",
                "completely",
                "totally",
                "always",
                "never",
                "bahut",
                "bilkul",
                "khub",
            ]
        )
        intensity = "deeply" if intense else "sincerely"

        # Detect question type
        is_how = "how" in q_lower or "kaise" in q_lower
        is_why = "why" in q_lower or "kyun" in q_lower
        is_what = "what" in q_lower or "kya" in q_lower
        is_help = any(w in q_lower for w in ["help", "guide", "support", "sahayata"])

        # Dominant context word (most specific non-stop word)
        context_word = key_words[0] if key_words else ptype

        # ── 2. Select anchor verses ───────────────────────────────────────────
        anchor = verses[0] if verses else {}
        a_ch = anchor.get("chapter", 2)
        a_v = anchor.get("verse", 47)
        a_en = anchor.get(
            "english",
            "You have a right to perform your duties, but not the fruits thereof.",
        )[:180]
        a_hi = anchor.get("hindi", "तुम्हारा अधिकार कर्म करने में है, फल में नहीं।")[:180]
        a_mr = anchor.get("marathi", "तुमचा अधिकार कर्म करण्यात आहे, फळात नाही.")[:180]
        a_sk = anchor.get("sanskrit", "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन")
        a_topic = anchor.get("topic", "spiritual guidance")

        sec = verses[1] if len(verses) > 1 else {}
        s_ch = sec.get("chapter", 6)
        s_v = sec.get("verse", 5)
        s_en = sec.get("english", "Elevate yourself through your own mind.")[:140]
        s_hi = sec.get("hindi", "मन की सहायता से स्वयं का उद्धार करो।")[:140]
        s_mr = sec.get("marathi", "मनाच्या मदतीने स्वतःचा उद्धार करा.")[:140]

        third = verses[2] if len(verses) > 2 else {}
        t_ch = third.get("chapter", 18)
        t_v = third.get("verse", 66)
        t_en = third.get(
            "english", "Surrender unto Me and I shall free you from all fear."
        )[:140]

        # ── 3. Build opening line — always from the user's exact words ────────
        openers = {
            "anxiety": f"You came with the words '{first_phrase}' — and the weight you are carrying right now is real.",
            "career": f"Your question about '{first_phrase}' touches the exact challenge Arjuna faced — confusion about what path to take.",
            "financial": f"The pressure of '{first_phrase}' is one of the most practical challenges the Gita addresses.",
            "relationships": f"What you shared about '{first_phrase}' — this kind of pain goes to the very root of human connection.",
            "studies": f"The pressure behind '{first_phrase}' — the Gita was spoken before the greatest battle, so it knows pressure intimately.",
            "grief": f"You wrote '{first_phrase}' — and the Gita begins with exactly this kind of grief. Arjuna wept too.",
            "anger": f"The fire of '{first_phrase}' you feel — Chapter 2:62 maps exactly how anger takes hold and what to do.",
            "fear": f"The fear in '{first_phrase}' — Arjuna trembled on the battlefield, and Krishna's answer was for him and for you.",
            "purpose": f"Searching for meaning behind '{first_phrase}' — this is the oldest question and the Gita's deepest answer.",
            "mental_health": f"What you described as '{first_phrase}' — Chapter 6 of the Gita is almost entirely about the struggling mind.",
            "spiritual": f"Your seeking in '{first_phrase}' — the Gita is written for exactly this kind of soul.",
            "general": f"You asked about '{first_phrase}' — and the Gita has specific wisdom for what you are going through.",
        }
        opener = openers.get(ptype, openers["general"])

        # ── 4. Person-specific hook ───────────────────────────────────────────
        person_hook = ""
        if person_ref:
            person_hook = f" {person_ref} is part of this — the Gita says those who matter to us are often our greatest teachers."
        if number_ctx:
            person_hook += f" The fact that you mention {number_ctx} tells me this has been weighing on you for a real and specific time."

        # ── 5. Question-type response ─────────────────────────────────────────
        q_response = ""
        if is_how:
            q_response = (
                f"You asked HOW — the Gita gives concrete steps, not vague comfort."
            )
        elif is_why:
            q_response = f"You asked WHY — the Gita says suffering has a cause rooted in attachment, and a path out."
        elif is_what:
            q_response = f"You asked WHAT — the Gita's answer is always: begin with your duty in this moment."
        elif is_help:
            q_response = (
                f"You asked for help — and help is exactly what this wisdom offers."
            )

        # ── 6. Core teaching block ────────────────────────────────────────────
        teachings = {
            "anxiety": f"Chapter {a_ch}:{a_v} tells us: '{a_en}' This is the direct answer to anxiety — "
            f"your mind creates suffering when it tries to control outcomes that belong to the future. "
            f"When you redirect every ounce of energy to THIS moment's action, the anxiety has nothing to feed on. "
            f"Chapter 6:35 adds: the restless mind can be tamed through practice (abhyāsa) and letting go (vairāgya). "
            f"Both together — not one without the other.",
            "career": f"Chapter {a_ch}:{a_v} says: '{a_en}' This means: measure your day by effort, not by title or salary. "
            f"Chapter 18:45 adds that every person — every person — can find perfection by following their own nature. "
            f"Your svadharma (your unique calling) is different from everyone else's. "
            f"It shows up in what you do when nobody is watching, what you cannot stop thinking about.",
            "financial": f"Chapter {a_ch}:{a_v}: '{a_en}' In money terms: your work, your effort, your skill — these are YOURS. "
            f"The outcome of how much comes and when — that is governed by forces beyond any single person. "
            f"Chapter 9:22 makes a promise: those who dedicate their actions receive 'yoga-kṣema' — "
            f"both new abundance AND protection of what they have. Not wealth without effort — sustained effort WITH surrender.",
            "relationships": f"Chapter {a_ch}:{a_v}: '{a_en}' In relationships this becomes: give your love fully, "
            f"but do not make your peace conditional on the other person changing. "
            f"Chapter 12:13 describes the highest approach: 'adveṣṭā sarva-bhūtānāṁ' — no hatred toward any being. "
            f"This is not passivity — it is the strength to act from love rather than from wound.",
            "studies": f"Chapter {a_ch}:{a_v}: '{a_en}' For every student: your job right now is to open the book and study. "
            f"That's it. The result is not your burden to carry tonight. "
            f"Chapter 4:38 tells us: 'nothing in this world purifies like knowledge.' "
            f"Every hour of real study is a sacred act — not just exam preparation.",
            "grief": f"Chapter 2:20 says: 'The soul is never born nor dies. It is unborn, eternal, primeval.' "
            f"What you loved does not disappear — it transforms. "
            f"Chapter {a_ch}:{a_v}: '{a_en}' Even Krishna wept for the world. Grief is not weakness. "
            f"It is love that has nowhere to go right now. The Gita asks only that you not be destroyed by it.",
            "anger": f"Chapter 2:62-63 maps it perfectly: desire → attachment → frustration → anger → delusion → destruction. "
            f"Chapter {a_ch}:{a_v}: '{a_en}' Anger tells you what you want. "
            f"The Gita does not say suppress it — it says understand its root, "
            f"then transform that fire into purposeful action rather than letting it burn everything.",
            "fear": f"Chapter 11:33: 'Therefore get up. Prepare to act.' Not recklessly — but with the knowledge "
            f"that you are capable of far more than fear believes. "
            f"Chapter {a_ch}:{a_v}: '{a_en}' Fear lives in an imagined future. "
            f"Your duty exists in THIS moment — and that you can always choose.",
            "purpose": f"Chapter 18:45: 'By following one's own nature, every person can achieve perfection.' "
            f"Chapter {a_ch}:{a_v}: '{a_en}' Purpose is not found by thinking harder. "
            f"It is revealed through committed action. You discover your dharma by doing — "
            f"and noticing what lights you up when you forget to perform.",
            "mental_health": f"Chapter 6:5: 'Lift yourself up with your own mind. The mind is your friend and your enemy.' "
            f"This is not 'just be positive.' It says: the very mind that causes pain also holds the key. "
            f"Chapter {a_ch}:{a_v}: '{a_en}' Small daily actions matter more than grand gestures. "
            f"Please also speak to someone you trust — the Gita values community and guidance.",
            "spiritual": f"Chapter {a_ch}:{a_v}: '{a_en}' Spiritual growth in the Gita is not withdrawal from the world — "
            f"it is full engagement WITH the world while staying rooted in the Self. "
            f"Chapter 7:19: the highest realization is 'vāsudevaḥ sarvam iti' — seeing the divine in all things. "
            f"This is available in every ordinary moment.",
            "general": f"Chapter {a_ch}:{a_v}: '{a_en}' This verse applies directly to what you are carrying. "
            f"Chapter {s_ch}:{s_v}: '{s_en}' "
            f"The Gita consistently points to the same truth: you have complete control over your next action. "
            f"That is your entire domain — and it is enough.",
        }
        teaching = teachings.get(ptype, teachings["general"])

        # ── 7. Today's actions (UNIQUE to query context) ──────────────────────
        actions_en = {
            "anxiety": [
                f"Write in one sentence exactly what you are anxious about — not a paragraph, one sentence",
                f"Ask yourself: 'Can I do anything about this in the next 2 hours?' If yes, do it. If no, write 'released' next to it",
                f"Read Chapter {a_ch}:{a_v} aloud 3 times tonight before sleeping — let its rhythm slow your mind",
            ],
            "career": [
                f"List 3 work tasks that feel aligned with your natural strengths — spend tomorrow focused only on those",
                f"Write: 'My work today is ___. The outcome I will release is ___' — do this every morning for 7 days",
                f"Ask one person who knows you well: 'When do you see me most energized?'",
            ],
            "financial": [
                f"Write down every single expense from this week — clarity breaks panic",
                f"Identify ONE income-related action you can take in the next 48 hours — commit to only that",
                f"Read Chapter 9:22 each morning for the next week — let the promise of divine support ground you",
            ],
            "relationships": [
                f"Write a full honest letter to the person involved — you do not need to send it",
                f"Identify your ONE specific action that contributed to the situation — not to blame yourself, but to find your power",
                f"Set one clear and kind boundary today — the Gita fully supports boundaries rooted in truth",
            ],
            "studies": [
                f"Study in 45-minute blocks with 10-minute breaks — 3 blocks today, no more, no less",
                f"After each block, write 3 things you actually understood — not notes, your own words",
                f"Before starting tomorrow, read Chapter {a_ch}:{a_v} once — set your intention, not your target",
            ],
            "grief": [
                f"Allow yourself to grieve today — do not schedule, suppress, or rush it",
                f"Light a candle or diya and speak out loud to who or what you have lost — even 2 minutes",
                f"Do one small act of service for someone else — the Gita says action is the bridge back to life",
            ],
            "anger": [
                f"When you feel anger rising today, count to 6 before responding — just 6 seconds",
                f"Write: 'I am angry because I wanted ___ and instead got ___' — name it precisely",
                f"Channel the energy: pick ONE productive action toward what you actually want and do it today",
            ],
            "fear": [
                f"Write the fear in one specific sentence: 'I am afraid that ___'",
                f"Identify the single smallest step you can take TODAY toward the thing you fear — do it",
                f"Read Chapter 11:33 tonight: 'Therefore get up.' Let those words be your answer",
            ],
            "purpose": [
                f"List 5 things you would do even if you were never paid for them — these are clues",
                f"Ask 3 people who know you: 'When do you see me most alive?' — write their answers down",
                f"Take ONE small action today toward your most resonant answer",
            ],
            "mental_health": [
                f"Please speak to someone today — a friend, family member, or counselor",
                f"Go outside for 15 minutes and observe nature — no phone, no agenda",
                f"Write 3 sentences about exactly how you feel right now — naming it is the first step to shifting it",
            ],
            "spiritual": [
                f"Read one chapter of the Gita slowly — stop wherever a verse speaks to you and sit with it",
                f"Sit in silence for 10 minutes before picking up your phone tomorrow morning",
                f"Do one act of selfless service today with zero expectation of any return",
            ],
            "general": [
                f"Write down everything that is troubling you — in full, honest detail, right now",
                f"Identify the one action most within your control in the next 24 hours — do only that",
                f"Read Chapter {a_ch}:{a_v} three times today and let it speak to your specific situation",
            ],
        }
        actions = actions_en.get(ptype, actions_en["general"])
        action_block = "\n".join(f"{i + 1}. {a}" for i, a in enumerate(actions))

        # ── 8. Assemble full English answer ───────────────────────────────────
        ans_en = (
            f"{opener}{person_hook}\n\n"
            f"{q_response + chr(10) + chr(10) if q_response else ''}"
            f"{teaching}\n\n"
            f"What you can do right now — specific to your situation:\n{action_block}"
        )

        # ── 9. Hindi answer ───────────────────────────────────────────────────
        openers_hi = {
            "anxiety": f"आपने '{first_phrase}' के बारे में लिखा — और यह बोझ बिल्कुल वास्तविक है।",
            "career": f"'{first_phrase}' के बारे में आपका प्रश्न — यही वह दुविधा है जो अर्जुन को भी थी।",
            "financial": f"'{first_phrase}' का दबाव — गीता इसे बहुत व्यावहारिक तरीके से समझती है।",
            "relationships": f"'{first_phrase}' के बारे में जो आपने लिखा — यह दर्द मानवीय संबंधों की जड़ को छूता है।",
            "studies": f"'{first_phrase}' का बोझ — गीता महायुद्ध से पहले बोली गई, दबाव को वह जानती है।",
            "grief": f"'{first_phrase}' — गीता इसी दुःख से शुरू होती है। अर्जुन भी रोया था।",
            "anger": f"'{first_phrase}' की आग — अध्याय 2:62 बताता है यह कैसे भड़कती है और क्या करें।",
            "fear": f"'{first_phrase}' का डर — अर्जुन भी युद्धभूमि पर कांपा था।",
            "purpose": f"'{first_phrase}' की खोज — यह गीता का सबसे गहरा उत्तर है।",
            "general": f"आपने '{first_phrase}' के बारे में पूछा — गीता के पास इसका उत्तर है।",
        }
        teachings_hi = {
            "anxiety": f"अध्याय {a_ch}:{a_v}: '{a_hi}' — चिंता तब होती है जब मन भविष्य को नियंत्रित करने की कोशिश करता है। जब आप इस क्षण के कर्म पर ध्यान केंद्रित करते हैं, चिंता को खाने के लिए कुछ नहीं मिलता।",
            "career": f"अध्याय {a_ch}:{a_v}: '{a_hi}' — अपने काम को प्रयास से मापें, परिणाम से नहीं। आपका स्वधर्म — आपका अनूठा मार्ग — वह है जो आपकी प्रकृति से मेल खाता हो।",
            "financial": f"अध्याय {a_ch}:{a_v}: '{a_hi}' — आपका प्रयास, आपका कौशल — यह आपका है। अध्याय 9:22 वादा करता है: जो भक्ति से कर्म करते हैं, उनका योग-क्षेम परमात्मा वहन करता है।",
            "relationships": f"अध्याय {a_ch}:{a_v}: '{a_hi}' — अपना प्रेम पूरी तरह दो, लेकिन अपनी शांति दूसरे के बदलने पर निर्भर मत करो।",
            "studies": f"अध्याय {a_ch}:{a_v}: '{a_hi}' — अभी किताब खोलना और पढ़ना — यही आपका कर्म है। परिणाम आज की चिंता नहीं।",
            "grief": f"अध्याय 2:20: आत्मा कभी नष्ट नहीं होती। अध्याय {a_ch}:{a_v}: '{a_hi}' — दुःख प्रेम है जिसे अभी जाने की जगह नहीं मिली।",
            "anger": f"अध्याय 2:62-63 क्रोध का नक्शा देता है। अध्याय {a_ch}:{a_v}: '{a_hi}' — क्रोध को दबाओ नहीं, समझो और रूपांतरित करो।",
            "fear": f"अध्याय 11:33: 'उठो, लड़ो।' अध्याय {a_ch}:{a_v}: '{a_hi}' — डर भविष्य में रहता है। आपका कर्तव्य इस क्षण में है।",
            "general": f"अध्याय {a_ch}:{a_v}: '{a_hi}' — अध्याय {s_ch}:{s_v}: '{s_hi}' — आपके अगले कार्य पर आपका पूरा अधिकार है।",
        }
        actions_hi = {
            "anxiety": [
                f"एक वाक्य में लिखें: 'मैं ___ के बारे में चिंतित हूं'",
                f"पूछें: 'क्या मैं अगले 2 घंटे में कुछ कर सकता हूं?' हां तो करें, नहीं तो 'छोड़ा' लिखें",
                f"आज रात सोने से पहले अध्याय {a_ch}:{a_v} तीन बार जोर से पढ़ें",
            ],
            "career": [
                f"3 काम लिखें जो आपकी ताकत के साथ मेल खाते हों — कल उन्हीं पर ध्यान दें",
                f"हर सुबह लिखें: 'आज मेरा कर्म ___ है। परिणाम मैं छोड़ता/छोड़ती हूं'",
                f"एक करीबी से पूछें: 'मुझे सबसे ऊर्जावान कब देखते हो?'",
            ],
            "financial": [
                f"इस हफ्ते का हर खर्च लिखें — स्पष्टता घबराहट तोड़ती है",
                f"48 घंटों में एक आय-संबंधी कदम पहचानें और केवल उस पर ध्यान दें",
                f"अगले एक हफ्ते हर सुबह अध्याय 9:22 पढ़ें",
            ],
            "studies": [
                f"45 मिनट पढ़ाई, 10 मिनट आराम — आज 3 ब्लॉक, इससे ज्यादा नहीं",
                f"हर ब्लॉक के बाद 3 बातें लिखें जो आपने समझीं — अपने शब्दों में",
                f"कल शुरू करने से पहले अध्याय {a_ch}:{a_v} एक बार पढ़ें",
            ],
            "general": [
                f"जो परेशान कर रहा है वह सब ईमानदारी से लिखें",
                f"अगले 24 घंटों में जो एक काम आपके नियंत्रण में है — केवल वह करें",
                f"आज अध्याय {a_ch}:{a_v} तीन बार पढ़ें",
            ],
        }
        opener_hi = openers_hi.get(ptype, openers_hi["general"])
        teaching_hi = teachings_hi.get(ptype, teachings_hi["general"])
        act_hi = actions_hi.get(ptype, actions_hi["general"])
        act_block_hi = "\n".join(f"{i + 1}. {a}" for i, a in enumerate(act_hi))
        ans_hi = f"{opener_hi}\n\n{teaching_hi}\n\nआज के लिए विशिष्ट कदम:\n{act_block_hi}"

        # ── 10. Marathi answer ────────────────────────────────────────────────
        openers_mr = {
            "anxiety": f"तुम्ही '{first_phrase}' बद्दल लिहिलं — हे ओझं खरं आहे.",
            "career": f"'{first_phrase}' बद्दल तुमचा प्रश्न — हीच अर्जुनाची गोंधळ होती.",
            "financial": f"'{first_phrase}' चा दबाव — गीता हे व्यावहारिकपणे समजते.",
            "relationships": f"'{first_phrase}' बद्दल तुम्ही लिहिलं — हे दुःख माणसाच्या मूळाला स्पर्श करतं.",
            "studies": f"'{first_phrase}' चं दडपण — गीता महायुद्धापूर्वी सांगितली गेली, दबाव तिला माहित आहे.",
            "grief": f"'{first_phrase}' — गीता याच दुःखाने सुरू होते. अर्जुनही रडला होता.",
            "general": f"तुम्ही '{first_phrase}' बद्दल विचारलं — गीताकडे उत्तर आहे.",
        }
        teachings_mr = {
            "anxiety": f"अध्याय {a_ch}:{a_v}: '{a_mr}' — चिंता तेव्हा होते जेव्हा मन भविष्य नियंत्रित करण्याचा प्रयत्न करतं. वर्तमान कर्मावर लक्ष केंद्रित केल्यावर चिंतेला खाण्यासाठी काही उरत नाही.",
            "career": f"अध्याय {a_ch}:{a_v}: '{a_mr}' — काम प्रयत्नाने मोजा, निकालाने नाही. तुमचा स्वधर्म — तुमचा अनोखा मार्ग — तो आहे जो तुमच्या स्वभावाशी जुळतो.",
            "studies": f"अध्याय {a_ch}:{a_v}: '{a_mr}' — आत्ता पुस्तक उघडणे आणि अभ्यास करणे — हेच तुमचे कर्म आहे.",
            "grief": f"अध्याय 2:20: आत्मा कधीच नष्ट होत नाही. अध्याय {a_ch}:{a_v}: '{a_mr}' — दुःख म्हणजे प्रेम ज्याला आत्ता जायला जागा नाही.",
            "general": f"अध्याय {a_ch}:{a_v}: '{a_mr}' — तुमच्या पुढील कृतीवर तुमचा पूर्ण अधिकार आहे.",
        }
        opener_mr = openers_mr.get(ptype, openers_mr["general"])
        teaching_mr = teachings_mr.get(ptype, teachings_mr["general"])
        ans_mr = (
            f"{opener_mr}\n\n{teaching_mr}\n\n"
            f"आजसाठी विशिष्ट पावले:\n"
            f"1. जे त्रास देत आहे ते एका वाक्यात लिहा\n"
            f"2. विचारा: 'पुढील 2 तासांत मी काय करू शकतो?' — ते करा\n"
            f"3. अध्याय {a_ch}:{a_v} आज तीनदा मोठ्याने वाचा"
        )

        # ── 11. Key teaching selection ────────────────────────────────────────
        kt_map = {
            "anxiety": (
                "माँ ते सङ्गोऽस्त्वकर्मणि",
                "Do not be attached to inaction — act, release, repeat.",
                "अकर्म में आसक्त मत हो — कर्म करो, छोड़ो, दोहराओ।",
                "अकर्मात आसक्त होऊ नका — कृती करा, सोडा, पुन्हा करा.",
            ),
            "career": (
                "योगः कर्मसु कौशलम्",
                "Yoga is skill in action — excellence is your offering.",
                "योग कर्म में कुशलता है — उत्कृष्टता ही आपकी पूजा है।",
                "योग हे कर्मातील कौशल्य — उत्कृष्टता हीच तुमची पूजा.",
            ),
            "financial": (
                "योगक्षेमं वहाम्यहम्",
                "I carry what you lack and protect what you have.",
                "मैं तुम्हारा योग और क्षेम वहन करता हूं।",
                "मी तुमचे योग आणि क्षेम वहन करतो.",
            ),
            "relationships": (
                "अद्वेष्टा सर्वभूतानाम्",
                "Act from love, not from wound.",
                "प्रेम से कार्य करो, पीड़ा से नहीं।",
                "प्रेमातून कार्य करा, दुखातून नाही.",
            ),
            "studies": (
                "अभ्यासेन तु कौन्तेय वैराग्येण च गृह्यते",
                "Practice and detachment — the two keys to mastery.",
                "अभ्यास और वैराग्य — महारत की दो चाबियां।",
                "अभ्यास आणि वैराग्य — निपुणतेच्या दोन चाव्या.",
            ),
            "grief": (
                "नायं हन्ति न हन्यते",
                "The soul neither kills nor is killed — love is eternal.",
                "आत्मा न मारता है न मरता है — प्रेम शाश्वत है।",
                "आत्मा न मारतो न मरतो — प्रेम शाश्वत आहे.",
            ),
            "anger": (
                "क्रोधाद्भवति सम्मोहः",
                "From anger comes delusion — understand it before it consumes.",
                "क्रोध से मोह उत्पन्न होता है — इसे समझो।",
                "क्रोधातून मोह उत्पन्न होतो — समजून घ्या.",
            ),
            "fear": (
                "उत्तिष्ठ कौन्तेय",
                "Arise — your capacity is greater than your fear believes.",
                "उठो — तुम्हारी क्षमता डर से बड़ी है।",
                "उठा — तुमची क्षमता भीतीपेक्षा मोठी आहे.",
            ),
            "purpose": (
                "स्वे स्वे कर्मण्यभिरतः",
                "Each person, absorbed in their own work, finds perfection.",
                "अपने कर्म में लगा हर व्यक्ति सिद्धि पाता है।",
                "आपल्या कर्मात रत प्रत्येक माणूस सिद्धी मिळवतो.",
            ),
            "general": (
                "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन",
                "You have full right to act — never to the fruits.",
                "कर्म में ही अधिकार है, फल में नहीं।",
                "कर्मातच अधिकार आहे, फळात नाही.",
            ),
        }
        kt = kt_map.get(ptype, kt_map["general"])

        # ── 12. Verse relevance ────────────────────────────────────────────────
        verse_list = []
        for v in verses[:2]:
            verse_list.append(
                {
                    "chapter": v["chapter"],
                    "verse": v["verse"],
                    "sanskrit": v.get("sanskrit", ""),
                    "transliteration": v.get("transliteration", ""),
                    "english": v.get("english", ""),
                    "hindi": v.get("hindi", ""),
                    "marathi": v.get("marathi", ""),
                    "relevance_english": (
                        f"Chapter {v['chapter']}:{v['verse']} ({v.get('topic', '')}) applies directly to "
                        f"'{first_phrase}' — {v.get('keywords', '').split(',')[0] if v.get('keywords') else 'this teaching'} "
                        f"is at the heart of what you are asking."
                    ),
                    "relevance_hindi": f"यह श्लोक '{first_phrase}' के संदर्भ में सीधे आपकी स्थिति पर बोलता है।",
                    "relevance_marathi": f"हा श्लोक '{first_phrase}' च्या संदर्भात तुमच्या परिस्थितीशी थेट बोलतो.",
                }
            )

        return {
            "problem_type": ptype,
            "answer": {"english": ans_en, "hindi": ans_hi, "marathi": ans_mr},
            "verses": verse_list,
            "key_teaching": kt[0],
            "key_teaching_meaning": {
                "english": kt[1],
                "hindi": kt[2],
                "marathi": kt[3],
            },
        }

    # ══════════════════════════════════════════════════════════════════════════
    # 4-DAY GUIDE  — fully parameterized, unique per query
    # ══════════════════════════════════════════════════════════════════════════
    def _build_four_day_guide(
        self,
        query: str,
        ptype: str,
        phrase: str,
        ch1: int,
        v1: int,
        ch2: int,
        v2: int,
        ch3: int,
        v3: int,
        ctx: str,
        num: str,
    ) -> Dict:
        num_hint = f" (you mentioned {num})" if num else ""
        ctx_cap = ctx.capitalize() if ctx else "This"

        day_plans = {
            "anxiety": [
                (
                    "🌅",
                    "Name It — Stop Feeding It",
                    f"5:30am — Read Ch.{ch1}:{v1} aloud. Write one sentence: 'I am anxious about {phrase}.' Name it exactly.",
                    f"12pm — List everything that feels uncertain. Circle only what you can act on today. Do those. Release the rest.",
                    f"8pm — 10-minute breathing: inhale 4 counts, hold 4, exhale 6. No screens 1 hour before bed.",
                    f'"My duty is to act. The outcome is not mine to carry."',
                ),
                (
                    "☀️",
                    "Separate Action from Outcome",
                    f"6am — Write Ch.{ch1}:{v1} by hand. Sit with it 5 minutes before doing anything else.",
                    f"12pm — Choose ONE task. Give it your full, undivided attention for 45 minutes. Measure the day by THIS.",
                    f"8pm — Journal: 'Today I gave my best to ___. I release what comes next.'",
                    f'"I am responsible for the effort. Never for the fruit."',
                ),
                (
                    "🌿",
                    "Train the Mind",
                    f"5:30am — Read Ch.{ch2}:{v2}. Ask: 'Is my mind my friend or enemy today?'",
                    f"Throughout day — Each time anxiety rises, pause 6 seconds before reacting. Just 6.",
                    f"7pm — Walk outside 20 minutes. No phone. Just sky, trees, breath.",
                    f'"I choose what I feed my mind today."',
                ),
                (
                    "🌟",
                    "Commit and Continue",
                    f"Morning — Review your 3 days. Write what shifted, even slightly.",
                    f"Afternoon — Do the one thing anxiety made you avoid. Imperfectly. That is enough.",
                    f"Evening — Read Ch.{ch1}:{v1} final time. Carry it as your daily anchor going forward.",
                    f'"I acted with courage. The rest belongs to the divine."',
                ),
            ],
            "career": [
                (
                    "🌅",
                    "Discover Your Svadharma",
                    f"6am — Read Ch.18:45. List 5 tasks that energize you at work — not impress others, energize YOU.",
                    f"Work hours — Spend the day doing only those 5-type tasks. Track your energy level every 2 hours.",
                    f"Evening — Journal: 'My natural strengths are ___. Work that uses them is ___.'",
                    f'"My unique path exists. I am discovering it by acting."',
                ),
                (
                    "☀️",
                    "Work Without the Ego Score",
                    f"Morning intention — Today I work for the work itself. No checking what others think.",
                    f"Afternoon — Complete one long-delayed task fully. No half-measures.",
                    f"Evening — Write: 'Today I worked on ___ with full effort. I release the result.'",
                    f'"Excellence is my offering. Recognition is not my measure."',
                ),
                (
                    "🌿",
                    "Turn Challenges into Teachers",
                    f"6am — Read Ch.{ch1}:{v1}. Identify one career challenge that is teaching you something.",
                    f"Afternoon — Have one honest conversation at work you have been avoiding.",
                    f"Evening — Write: 'The lesson in this challenge is ___.'",
                    f'"Every difficulty is a teacher in disguise."',
                ),
                (
                    "🌟",
                    "Write Your Dharma Statement",
                    f"Morning — Write: 'I work to ___. My unique contribution is ___. My measure of success is ___.'",
                    f"Afternoon — Take one action aligned with that statement — even a small one.",
                    f"Evening — Read Ch.18:45-46. Feel: your work done with devotion IS worship.",
                    f'"My work is my prayer when done with full dedication."',
                ),
            ],
            "studies": [
                (
                    "🌅",
                    "Set Intention, Not Just Target",
                    f"6am — Read Ch.{ch1}:{v1}. Write: 'Today I study ___ with full attention. Result is not my burden.'",
                    f"Study time — 45 min study, 10 min break, 3 cycles. After each block: write 3 things understood.",
                    f"10pm — Review today's notes in 10 minutes, then sleep. No new material after 10pm.",
                    f'"I give my full effort. The rest follows."',
                ),
                (
                    "☀️",
                    "Master the Hardest Subject First",
                    f"Morning — Read Ch.6:35. Study your weakest subject FIRST when mind is freshest.",
                    f"Afternoon — Make summary notes in your own words only. No copy-paste. Your language.",
                    f"Evening — Teach what you studied today to a wall, mirror, or friend — out loud.",
                    f'"Each hour of study is a sacred act of knowledge."',
                ),
                (
                    "🌿",
                    "Test Yourself Honestly",
                    f"Morning — Take a timed mock test of yesterday's material. Grade yourself without mercy.",
                    f"Afternoon — Spend the entire afternoon ONLY on the weakest areas the test revealed.",
                    f"Evening — Write: 'Today I struggled with ___ and improved it by ___.'",
                    f'"Honest self-assessment is the fastest path to mastery."',
                ),
                (
                    "🌟",
                    "Offer Your Effort, Release the Result",
                    f"Morning — Write Ch.{ch1}:{v1} by hand. This is your exam mantra.",
                    f"Afternoon — Full revision from your own summary notes. No cramming. Just your own words.",
                    f"Night — Prepare your exam kit. Sleep by 10pm. Your effort is complete. Trust it.",
                    f'"I have given my best. The rest is in divine hands."',
                ),
            ],
            "relationships": [
                (
                    "🌅",
                    "See It Clearly Without Judgment",
                    f"Morning — Write everything that happened in this relationship — facts only, no interpretations.",
                    f"Afternoon — Identify YOUR one specific contribution to the situation. Not self-blame. Just your power.",
                    f"Evening — Read Ch.12:13. Ask: 'Am I acting from love or from wound?'",
                    f'"I see clearly. I choose consciously."',
                ),
                (
                    "☀️",
                    "Feel It Fully",
                    f"Morning — Write a full honest letter to the person. Do not send it. Just write everything.",
                    f"Afternoon — Speak to one trusted person about what you are feeling. Not advice — just presence.",
                    f"Evening — Read Ch.{ch1}:{v1}. Your duty in this relationship is to love well, not to control outcomes.",
                    f'"My love is real. My peace cannot depend on their choices."',
                ),
                (
                    "🌿",
                    "Set One Clear Boundary",
                    f"Morning — Define one boundary that protects your wellbeing. Write it in one sentence.",
                    f"Afternoon — Communicate or act on that boundary today — calmly, kindly, clearly.",
                    f"Evening — Journal: 'I honored myself today by ___.'",
                    f'"Love and clear boundaries are not opposites."',
                ),
                (
                    "🌟",
                    "Act from Your Highest Self",
                    f"Morning — Read Ch.12:13-15. Ask: 'What would my highest self do in this relationship?'",
                    f"Afternoon — Do that one thing. Not for them. For who you are choosing to be.",
                    f"Evening — Write: 'I acted with dignity today. That is enough.'",
                    f'"I give love freely. I receive peace from within."',
                ),
            ],
            "grief": [
                (
                    "🌅",
                    "Allow — Do Not Suppress",
                    f"Morning — Read Ch.2:20: 'The soul is never born nor dies.' Sit with it.",
                    f"Afternoon — Light a candle. Speak to who or what you have lost. Even 2 minutes out loud.",
                    f"Evening — Write about one specific memory you treasure. Honor it.",
                    f'"Grief is love that has nowhere to go. I honour both."',
                ),
                (
                    "☀️",
                    "Find One Thread of Life",
                    f"Morning — Read Ch.{ch1}:{v1}. Your duty to continue living is also a sacred act.",
                    f"Afternoon — Do one small act of service for another person. This is the bridge back.",
                    f"Evening — Write: 'One thing still beautiful in my world today is ___.'",
                    f'"Even in grief, life asks me forward."',
                ),
                (
                    "🌿",
                    "Connect",
                    f"Morning — Read Ch.9:22. The divine carries what you cannot.",
                    f"Afternoon — Call or visit one person who loved the same person or thing you lost.",
                    f"Evening — Sit in silence for 15 minutes. No agenda. Just be.",
                    f'"I do not grieve alone. The divine is present in this."',
                ),
                (
                    "🌟",
                    "Take One Step Forward",
                    f"Morning — Write: 'The person/thing I lost gave me ___. I carry that forward by ___.'",
                    f"Afternoon — Do ONE thing that honours their memory through action.",
                    f"Evening — Read Ch.2:20 again. The eternal never leaves.",
                    f'"My love continues. My life continues. Both are true."',
                ),
            ],
            "financial": [
                (
                    "🌅",
                    "Clarity Before Action",
                    f"Morning — Write every single expense from the past month. Every one. Clarity kills panic.",
                    f"Afternoon — Separate: what you OWE (fixed) vs what you SPEND (variable). Fix the second.",
                    f"Evening — Read Ch.9:22. The divine sustains those who act with dedication.",
                    f'"I face my numbers with courage. Clarity is power."',
                ),
                (
                    "☀️",
                    "One Income Action",
                    f"Morning — Identify ONE specific income-generating action you can complete this week.",
                    f"Afternoon — Begin that action. Only that action. No spiraling into the bigger picture.",
                    f"Evening — Write: 'I took one step toward abundance today: ___.'",
                    f'"One action at a time builds the whole path."',
                ),
                (
                    "🌿",
                    "Cut Without Guilt",
                    f"Morning — Read Ch.{ch1}:{v1}. Apply it to spending: your duty is responsible action, not results.",
                    f"Afternoon — Identify 3 expenses to reduce this month. Implement them today.",
                    f"Evening — Journal: 'I am taking care of my financial life. That is enough for today.'",
                    f'"Discipline today creates freedom tomorrow."',
                ),
                (
                    "🌟",
                    "Build the Habit",
                    f"Morning — Write your financial dharma: 'I handle money by ___. My principle is ___.'",
                    f"Afternoon — Set up one simple daily practice: check balance ONCE, note one expense.",
                    f"Evening — Read Ch.18:46. Your honest work IS worship. Money follows dharma.",
                    f'"I am the responsible steward of what I have been given."',
                ),
            ],
        }

        default_days = [
            (
                "🌅",
                "Awareness — See It Clearly",
                f"Morning — Read Ch.{ch1}:{v1}. Write exactly what is troubling you — no filter.",
                f"Afternoon — Identify ONE thing within your control today. Direct all energy there.",
                f"Evening — Sit quietly 10 minutes. No phone. Observe thoughts without reacting.",
                f'"I see clearly. I act on what is mine to act on."',
            ),
            (
                "☀️",
                "Acceptance — Work With What Is",
                f"Morning — Read Ch.2:14: all situations are temporary. What can this teach you?",
                f"Afternoon — Do one act of service with zero expectation of return.",
                f"Evening — Journal: 'This situation is teaching me ___.'",
                f'"This too shall pass. And I will have grown."',
            ),
            (
                "🌿",
                "Action — Move With Courage",
                f"Morning — Read Ch.{ch2}:{v2}. List 3 actions you can take toward your situation.",
                f"Afternoon — Take at least ONE of those actions. Imperfectly. That is enough.",
                f"Evening — Write: 'Today I acted. I did ___. The rest is in divine hands.'",
                f'"Courage is not the absence of fear. It is action despite it."',
            ),
            (
                "🌟",
                "Integration — Make It a Practice",
                f"Morning — Review the last 3 days. What shifted? What do you want to continue?",
                f"Afternoon — Share what you learned with one person you trust.",
                f"Evening — Read Ch.{ch1}:{v1} final time. This verse is your anchor going forward.",
                f'"I have grown. I carry this wisdom into every day ahead."',
            ),
        ]

        day_data = day_plans.get(ptype, default_days)

        days = []
        for i, d in enumerate(day_data):
            ico, theme, morn, aft, eve, aff = d
            days.append(
                {
                    "day": i + 1,
                    "theme": theme,
                    "icon": ico,
                    "verse_anchor": f"Chapter {[ch1, ch2, ch3, ch1][i]} · Verse {[v1, v2, v3, v1][i]}",
                    "morning": morn,
                    "afternoon": aft,
                    "evening": eve,
                    "affirmation": aff,
                }
            )

        title_map = {
            "anxiety": f"Your 4-Day Peace Plan — {phrase}",
            "career": f"Your 4-Day Career Clarity Plan — {phrase}",
            "financial": f"Your 4-Day Financial Clarity Plan — {phrase}",
            "relationships": f"Your 4-Day Relationship Healing Plan — {phrase}",
            "studies": f"Your 4-Day Study Focus Plan — {phrase}",
            "grief": f"Your 4-Day Grief and Healing Plan — {phrase}",
            "anger": f"Your 4-Day Anger Transformation Plan — {phrase}",
            "fear": f"Your 4-Day Courage-Building Plan — {phrase}",
            "purpose": f"Your 4-Day Purpose Discovery Plan — {phrase}",
            "mental_health": f"Your 4-Day Mind Healing Plan — {phrase}",
            "spiritual": f"Your 4-Day Spiritual Practice Plan — {phrase}",
            "general": f"Your Personal 4-Day Gita Healing Plan — {phrase}",
        }

        return {"title": title_map.get(ptype, title_map["general"]), "days": days}

    # ── Classify ───────────────────────────────────────────────────────────────
    def _classify_problem(self, q: str) -> str:
        keywords = {
            "anxiety": [
                "anxiety",
                "anxious",
                "stress",
                "tension",
                "worried",
                "overthink",
                "nervous",
                "panic",
                "restless",
                "चिंता",
                "तनाव",
                "ताण",
            ],
            "career": [
                "career",
                "job",
                "work",
                "profession",
                "office",
                "boss",
                "salary",
                "business",
                "interview",
                "promotion",
                "resign",
                "quit",
                "fired",
                "करियर",
                "नौकरी",
                "काम",
                "करिअर",
            ],
            "financial": [
                "money",
                "finance",
                "debt",
                "loan",
                "poor",
                "income",
                "rupee",
                "salary",
                "bill",
                "emi",
                "broke",
                "afford",
                "पैसा",
                "पैसे",
                "कर्ज",
                "आर्थिक",
            ],
            "relationships": [
                "relationship",
                "love",
                "family",
                "friend",
                "marriage",
                "divorce",
                "partner",
                "husband",
                "wife",
                "mother",
                "father",
                "brother",
                "sister",
                "रिश्ते",
                "प्यार",
                "परिवार",
                "नाते",
            ],
            "studies": [
                "study",
                "exam",
                "student",
                "education",
                "school",
                "college",
                "fail",
                "marks",
                "board",
                "test",
                "result",
                "grade",
                "पढ़ाई",
                "परीक्षा",
                "अभ्यास",
                "शिक्षण",
            ],
            "grief": [
                "grief",
                "death",
                "lost",
                "loss",
                "sad",
                "miss",
                "passed away",
                "died",
                "mourn",
                "gone",
                "दुःख",
                "मृत्यु",
                "उदास",
                "शोक",
            ],
            "anger": [
                "angry",
                "anger",
                "frustrated",
                "irritated",
                "rage",
                "conflict",
                "fight",
                "hate",
                "furious",
                "क्रोध",
                "गुस्सा",
                "राग",
            ],
            "fear": [
                "fear",
                "afraid",
                "scared",
                "phobia",
                "doubt",
                "uncertain",
                "terrified",
                "डर",
                "भय",
                "भीती",
                "शंका",
            ],
            "purpose": [
                "purpose",
                "meaning",
                "direction",
                "goal",
                "lost",
                "confused",
                "dharma",
                "destiny",
                "calling",
                "उद्देश्य",
                "लक्ष्य",
                "दिशा",
            ],
            "mental_health": [
                "mental",
                "depressed",
                "depression",
                "lonely",
                "alone",
                "empty",
                "hopeless",
                "suicidal",
                "worthless",
                "मानसिक",
                "अकेलापन",
                "एकटेपणा",
            ],
            "spiritual": [
                "spiritual",
                "god",
                "divine",
                "meditation",
                "soul",
                "karma",
                "prayer",
                "enlightenment",
                "आत्मा",
                "ईश्वर",
                "आध्यात्मिक",
            ],
        }
        for ptype, words in keywords.items():
            if any(w in q for w in words):
                return ptype
        return "general"

    # ── Verse Enrichment ───────────────────────────────────────────────────────
    def _enrich_verses(self, response: Dict, retrieved: List[Dict]) -> Dict:
        enriched = []
        for v in response.get("verses", []):
            try:
                ch, vs = int(v.get("chapter", 0)), int(v.get("verse", 0))
            except:
                enriched.append(v)
                continue
            db = self.vector_store.get_verse(ch, vs)
            if db:
                merged = {**db}
                merged["relevance_english"] = v.get("relevance_english", "")
                merged["relevance_hindi"] = v.get("relevance_hindi", "")
                merged["relevance_marathi"] = v.get("relevance_marathi", "")
                enriched.append(merged)
            else:
                enriched.append(v)
        if not enriched and retrieved:
            for v in retrieved[:2]:
                enriched.append(
                    {
                        **v,
                        "relevance_english": f"This verse ({v.get('topic', '')}) directly addresses your question.",
                        "relevance_hindi": f"यह श्लोक आपकी स्थिति से सीधे जुड़ता है।",
                        "relevance_marathi": f"हा श्लोक तुमच्या परिस्थितीशी थेट संबंधित आहे.",
                    }
                )
        response["verses"] = enriched
        return response

    def clear_history(self):
        self.conversation_history = []

    def get_history(self):
        return self.conversation_history
