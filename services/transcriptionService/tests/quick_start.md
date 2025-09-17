# הרצה מהירה - בדיקת איכות תמלול

## הרצת המבחן עכשיו

```bash
cd /Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests
python manual_transcription_test.py
```

## מה יקרה

הסקריפט יבדוק את הקובץ:
```
/Users/lyhwstynmn/פרוייקטים/python/Karaoke/data/audio/rgSvk335zis/vocals.wav
```

ויצור תוצאות ב:
```
/Users/lyhwstynmn/פרוייקטים/python/Karaoke/services/transcriptionService/tests/output/test_transcription.lrc
```

## בדיקת התוצאות

לאחר הרצת המבחן:

1. **פתח את הקובץ** `output/test_transcription.lrc`
2. **בדוק עברית תקינה** - הטקסט צריך להיות בעברית Unicode
3. **בדוק זמנים** - האם הזמנים הגיוניים?
4. **בדוק איכות** - האם המילים נכונות?

## מה להקשיב לתיקונים שלנו

התיקונים שביצענו:
- ✅ **הסרת unidecode** - עברית לא תתרגם ללטינית
- ✅ **Hebrew prompt** - הקשר עברי לשיפור זיהוי
- ✅ **VAD optimized** - זיהוי טוב יותר במוסיקה

התוצאות צריכות להיות משמעותית טובות יותר!