# Quick Start Examples

## Example 1: Bulk Upload 10 Students for Class 9

**File: class_9_students.csv**
```csv
roll_number,name,house_name,class_grade
2001,Samir Khan,Iqbal,9
2002,Zara Ali,Quaid,9
2003,Omar Farooq,Allama,9
2004,Laiba Ahmed,Iqbal,9
2005,Bilal Hassan,Quaid,9
2006,Amna Malik,Allama,9
2007,Fahad Sheikh,Iqbal,9
2008,Sara Hussain,Quaid,9
2009,Imran Karim,Allama,9
2010,Hana Rashid,Iqbal,9
```

**Steps:**
1. Save the above as `class_9_students.csv`
2. Go to Admin Dashboard
3. Click "👥 Bulk Upload Students"
4. Select the file
5. Click "📤 Upload & Register Students"
6. ✓ 10 students registered with their roll numbers as passwords

---

## Example 2: Upload 1st Term Results for Class 9 - All Subjects

**File: class_9_1st_term.csv**
```csv
roll_number,subject,mark
2001,English,72
2001,Urdu,68
2001,Math,75
2001,Bio,60
2001,Physics,62
2001,Chemistry,65
2001,Islamiyat,85
2001,Tarjamat-ul-Quran,45
2001,Computer,55
2002,English,78
2002,Urdu,72
2002,Math,80
2002,Bio,65
2002,Physics,68
2002,Chemistry,70
2002,Islamiyat,90
2002,Tarjamat-ul-Quran,48
2002,Computer,58
2003,English,70
2003,Urdu,65
2003,Math,72
2003,Bio,58
2003,Physics,60
2003,Chemistry,62
2003,Islamiyat,82
2003,Tarjamat-ul-Quran,42
2003,Computer,52
2004,English,75
2004,Urdu,70
2004,Math,78
2004,Bio,62
2004,Physics,65
2004,Chemistry,68
2004,Islamiyat,88
2004,Tarjamat-ul-Quran,46
2004,Computer,56
2005,English,68
2005,Urdu,64
2005,Math,70
2005,Bio,55
2005,Physics,58
2005,Chemistry,60
2005,Islamiyat,80
2005,Tarjamat-ul-Quran,40
2005,Computer,50
2006,English,73
2006,Urdu,69
2006,Math,76
2006,Bio,61
2006,Physics,63
2006,Chemistry,66
2006,Islamiyat,86
2006,Tarjamat-ul-Quran,44
2006,Computer,54
2007,English,71
2007,Urdu,67
2007,Math,74
2007,Bio,59
2007,Physics,61
2007,Chemistry,64
2007,Islamiyat,84
2007,Tarjamat-ul-Quran,43
2007,Computer,53
2008,English,77
2008,Urdu,73
2008,Math,79
2008,Bio,64
2008,Physics,67
2008,Chemistry,69
2008,Islamiyat,89
2008,Tarjamat-ul-Quran,47
2008,Computer,57
2009,English,69
2009,Urdu,65
2009,Math,71
2009,Bio,56
2009,Physics,59
2009,Chemistry,61
2009,Islamiyat,81
2009,Tarjamat-ul-Quran,41
2009,Computer,51
2010,English,74
2010,Urdu,70
2010,Math,77
2010,Bio,60
2010,Physics,62
2010,Chemistry,65
2010,Islamiyat,87
2010,Tarjamat-ul-Quran,45
2010,Computer,55
```

**Steps:**
1. Save the above as `class_9_1st_term.csv`
2. Go to Admin Dashboard
3. Click "📋 Bulk Upload Results"
4. Select **Class 9**
5. Select **1st Term**
6. Upload the file
7. ✓ 90 marks for all 10 students across all 9 subjects

---

## Example 3: Quick Upload for Board Exams (Select Subjects Only)

**File: board_exam_class_10.csv**
```csv
roll_number,subject,mark
1001,English,70
1001,Math,75
1001,Physics,72
1001,Chemistry,74
1002,English,68
1002,Math,72
1002,Physics,70
1002,Chemistry,72
1003,English,65
1003,Math,68
1003,Physics,68
1003,Chemistry,70
1004,English,72
1004,Math,74
1004,Physics,73
1004,Chemistry,75
1005,English,67
1005,Math,70
1005,Physics,69
1005,Chemistry,71
```

**Steps:**
1. Save the above as `board_exam_class_10.csv`
2. Go to Admin Dashboard
3. Click "📋 Bulk Upload Results"
4. Select **Class 10**
5. Select **Board Exam**
6. Upload the file
7. ✓ 20 board exam marks imported for 5 students (Core subjects only)

---

## Example 4: Uploading with Excel

You can also use Excel files (.xlsx or .xls) with the same format:

### Spreadsheet 1: Students (upload_students.xlsx)

| roll_number | name | house_name | class_grade |
|---|---|---|---|
| 3001 | Fatima Zahra | Iqbal | 11 |
| 3002 | Ali Raza | Quaid | 11 |
| 3003 | Hana Karim | Allama | 11 |
| 3004 | Hassan Malik | Iqbal | 11 |
| 3005 | Sophia Ahmed | Quaid | 11 |

### Spreadsheet 2: Results (upload_results.xlsx)

| roll_number | subject | mark |
|---|---|---|
| 3001 | English | 85 |
| 3001 | Math | 92 |
| 3001 | Physics | 88 |
| 3002 | English | 82 |
| 3002 | Math | 88 |
| 3002 | Physics | 85 |

---

## Automated Login Credentials After Bulk Upload

After uploading students, they can login immediately with:

**Username:** Their roll number (e.g., 2001)
**Password:** Their roll number (e.g., 2001)

### Example Login Flow:
1. Student visits http://127.0.0.1:5000/login?role=student
2. Enters username: 2001
3. Enters password: 2001
4. ✓ Login successful - Student can view their marks

---

## Tips for Data Entry

### Roll Number Format
- Use consistent format (e.g., always 4 digits like 1001, 1002)
- No spaces or special characters except hyphens (1001-A is OK, but avoid if possible)
- Must be unique across all students

### Names
- Full name recommended
- Include middle name if available
- Use proper capitalization

### House Names
- Standard format (e.g., Iqbal, Quaid, Allama, etc.)
- Be consistent with spelling
- Optional but recommended

### Marks
- Numeric values only (no text)
- Decimals allowed (e.g., 72.5)
- Must not exceed the full mark for that subject/class
- Must be 0 or positive

### Subject Names
Must match exactly (case-sensitive). See BULK_UPLOAD_GUIDE.md for complete list.

**Common mistakes:**
- ❌ "math" should be ✅ "Math"
- ❌ "English Language" should be ✅ "English"
- ❌ "Pak. Studies" should be ✅ "Pak Studies"

---

## Validation & Error Handling

The system performs automatic validation:

✅ Checks for duplicate roll numbers
✅ Verifies all required fields are present
✅ Validates class grades (must be 8-12)
✅ Ensures marks don't exceed full marks
✅ Confirms students exist before uploading marks
✅ Validates subject names

Errors are reported with row numbers so you can easily fix them.

---

## Performance

- **Students:** Can upload up to 1,000 students per file
- **Marks:** Can upload up to 10,000 marks per file
- **File size:** Maximum 16MB per file
- **Processing time:** Usually instant (< 1 second for typical files)

---

Last Updated: December 2025
