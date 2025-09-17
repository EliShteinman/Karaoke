# Manual Transcription Quality Tests

תיקיה זו מכילה כלים לבדיקת איכות התמלול באופן ידני.

## קבצים

### `manual_transcription_test.py`
הסקריפט הראשי לבדיקת איכות התמלול. מאפשר לך לבדוק קבצי אודיו ספציפיים ולראות את איכות התמלול.

### `test_config_example.py`
דוגמאות קונפיגורציה למבחנים שונים. העתק ועדכן לפי הצרכים שלך.

## שימוש מהיר

### 1. הרצה בסיסית
```bash
cd /Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests
python manual_transcription_test.py
```

### 2. עריכת נתיבים
ערוך את הקובץ `manual_transcription_test.py` וקבע:
- `INPUT_AUDIO_PATH` - נתיב לקובץ האודיו שלך
- `OUTPUT_DIR` - תיקיית הפלט לתוצאות
- `OUTPUT_LRC_FILE` - שם קובץ הפלט

### 3. דוגמה עם הקובץ הקיים שלך
הסקריפט כבר מוגדר לעבוד עם הקובץ:
```
/Users/lyhwstynmn/פרוייקטים/python/Karaoke/data/audio/rgSvk335zis/original.wav
```

## מה הסקריפט עושה

1. **אמת קובץ קלט** - בודק שהקובץ קיים
2. **יוצר תיקיית פלט** - יוצר את תיקיית הפלט אם לא קיימת
3. **מתחיל תמלול** - מריץ את שירות התמלול על הקובץ
4. **יוצר קובץ LRC** - שומר את התוצאות בפורמט LRC
5. **מציג סיכום** - מראה סטטיסטיקות ודוגמאות

## תוצאות

הסקריפט יציג:
- ⏱️ זמן עיבוד
- 🎯 ציון ביטחון (confidence score)
- 🌍 שפה שזוהתה
- 📊 מספר מילים וקטעים
- 📜 דוגמה של הקטעים הראשונים

## בדיקת איכות

לאחר הרצת המבחן, בדוק:

### ✅ דברים טובים לחפש:
- טקסט עברי תקין (Unicode, לא transliteration)
- זמנים מדויקים של הקטעים
- מילים נכונות ומובנות
- פיסוק הגיוני

### ❌ בעיות לזהות:
- טקסט לטיני במקום עברי (hyvm במקום היום)
- זמנים לא מדויקים
- מילים שגויות או חסרות
- קטעים ארוכים מדי או קצרים מדי

## הרצת מבחנים מרובים

ליצירת מבחנים מרובים:

1. העתק את `test_config_example.py` ל-`test_config.py`
2. ערוך את הקונפיגורציות
3. שנה את `manual_transcription_test.py` לייבא מ-`test_config`

## פתרון בעיות

### שגיאת יבוא
```bash
# ודא שאתה בתיקייה הנכונה
cd /Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests

# הפעל עם Python
python manual_transcription_test.py
```

### קובץ לא נמצא
ערוך את `INPUT_AUDIO_PATH` בסקריפט להצביע על הקובץ הנכון.

### שגיאות מודל
ודא שהמודל `ivrit-ai/whisper-large-v3-turbo-ct2` מותקן ונטען כראוי.