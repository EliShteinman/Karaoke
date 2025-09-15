# ממשק משתמש Streamlit - מפתח E

## המשימה שלך
את/ה אחראי/ת על ממשק המשתמש העברי לקריוקי עם Streamlit.

## מה עליך לעשות:
1. השלם את הפונקציות ב-src/ui/
2. צור עמודים: בית, העלאה, קריוקי, סטטוס
3. הוסף תמיכה ב-RTL עברית מלאה
4. בנה נגן קריוקי עם סנכרון מילים
5. הצג מעקב סטטוס עבודות בזמן אמת

## קבצים שעליך לכתוב:
- src/ui/pages/home.py
- src/ui/pages/upload.py
- src/ui/pages/karaoke.py
- src/ui/pages/status.py
- src/ui/components/audio_player.py
- src/ui/components/lyrics_display.py
- src/ui/utils/kafka_client.py
- src/ui/utils/api_client.py

## המבנה שלך:
```
services/ui/
├── src/
│   ├── app.py              # Streamlit app (כבר קיים - שדרג אותו)
│   ├── ui/                 # קבצים שלך לכתוב
│   │   ├── pages/
│   │   │   ├── home.py
│   │   │   ├── upload.py
│   │   │   ├── karaoke.py
│   │   │   └── status.py
│   │   ├── components/
│   │   │   ├── audio_player.py
│   │   │   └── lyrics_display.py
│   │   └── utils/
│   │       ├── kafka_client.py
│   │       └── api_client.py
├── tests/
├── requirements.txt        # כבר קיים
├── Dockerfile             # כבר קיים
└── README.md              # קובץ זה
```

## הרצה:
```bash
cd services/ui
streamlit run src/app.py
```

## גישה:
```
http://localhost:8501
```

## טכנולוגיות בשימוש:
- streamlit - Web framework עברי
- plotly - גרפים וויזואליזציות
- kafka-python - תקשורת בין שירותים
- requests - קריאות API
- pymongo - MongoDB
- pandas - ניהול נתונים

## עמודים לפיתוח:

### עמוד בית
- ברכה בעברית
- רשימת שירים פופולריים
- סטטיסטיקות כלליות
- הנחיות שימוש

### עמוד העלאה
- טופס הזנת URL יוטיוב
- וולידציה של קישור
- התחלת עיבוד
- הצגת progress

### עמוד קריוקי
- בחירת שיר
- נגן אודיו עם controls
- הצגת מילים מסונכרנות
- עצירה/המשכה/אתחול

### עמוד סטטוס
- רשימת כל העבודות
- סטטוס עיבוד לכל שירות
- לוגים ושגיאות
- אפשרות לביטול עבודה

## תכונות מיוחדות:

### RTL Hebrew Support
```python
st.markdown("""
<style>
    .main > div {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)
```

### Real-time Updates
- האזן להודעות Kafka
- עדכן סטטוס בזמן אמת
- הצג התקדמות עיבוד

### Audio Player
- נגן HTML5 מובנה
- controls מותאמים לעברית
- סנכרון עם מילים

### Lyrics Display
- הצגת מילים בזמן אמת
- הדגשת השורה הנוכחית
- תמיכה ב-RTL מלאה

**בהצלחה! 🎵**