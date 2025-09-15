# שירות יצירת LRC - מפתח D

## המשימה שלך
את/ה אחראי/ת על יצירת קבצי קריוקי LRC מסונכרנים מתמלול עברי.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/lrc_generator/
2. המר תמלול לפורמט LRC
3. סנכרן עם beat detection מהעיבוד
4. טפל ב-RTL עברית בקובץ LRC
5. שלח הודעה ל-ui_notifications

## קבצים שעליך לכתוב:
- src/lrc_generator/lrc_formatter.py
- src/lrc_generator/beat_synchronizer.py
- src/lrc_generator/rtl_handler.py

## המבנה שלך:
```
services/lrc-generator/
├── src/
│   ├── app.py              # FastAPI app (כבר קיים)
│   ├── config/
│   │   └── settings.py     # הגדרות לכתוב
│   └── lrc_generator/      # קבצים שלך לכתוב
│       ├── lrc_formatter.py
│       ├── beat_synchronizer.py
│       └── rtl_handler.py
├── tests/
├── requirements.txt        # כבר קיים
├── Dockerfile             # כבר קיים
└── README.md              # קובץ זה
```

## הרצה:
```bash
cd services/lrc-generator
python src/app.py
```

## Kafka Topics:
- **מאזין ל:** `lrc_generation_requests`
- **שולח ל:** `ui_notifications`

## טכנולוגיות בשימוש:
- FastAPI - Web framework
- python-bidi - טיפול ב-RTL עברית
- arabic-reshaper - עיצוב טקסט דו-כיווני
- kafka-python - תקשורת בין שירותים
- pymongo - MongoDB

## זרימת עבודה:
1. קבל הודעת Kafka עם נתוני תמלול ו-beat detection
2. טען transcript segments ו-beat timestamps
3. סנכרן מילים עם ביטים
4. צור קובץ LRC מעוצב
5. טפל ב-RTL עברית
6. שמור ב-MongoDB
7. הודע לממשק המשתמש

## פורמט LRC:
```
[ar:שם אמן]
[ti:שם שיר]
[al:אלבום]
[by:HebKaraoke]

[00:12.34]שורת מילים ראשונה
[00:15.67]שורת מילים שנייה
[00:18.90]שורת מילים שלישית
```

## משימות עיקריות:
### LRC Formatting
- המר TranscriptSegment ל-LRC format
- וודא timestamps מדויקים
- הוסף metadata headers

### Beat Synchronization
- סנכרן מילים עם beat timestamps
- התאם לקצב השיר
- שמור על זרימה טבעית

### RTL Handling
- טפל בעברית RTL
- וודא תצוגה נכונה בנגנים
- עבד mixed content (עברית + אנגלית)

## אתגרים מיוחדים:
- סנכרון מדויק עם המוזיקה
- תמיכה ב-RTL בנגני קריוקי
- טיפול בשירים מהירים/איטיים

**בהצלחה! 🎵**