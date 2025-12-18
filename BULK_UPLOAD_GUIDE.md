# Bulk Upload Features - User Guide

## Overview
The RMS now supports two bulk upload features:
1. **Bulk Upload Students** - Register multiple students at once
2. **Bulk Upload Results** - Import marks for multiple students at once

---

## 1. Bulk Upload Students

### Location
- Admin Dashboard → **👥 Bulk Upload Students** button
- Direct URL: `/admin/upload_students`

### Purpose
Quickly register multiple students by uploading a CSV or Excel file. Each student is automatically created with:
- Username = Roll Number
- Password = Roll Number (for initial login)
- Role = Student
- Approved = Yes (automatically approved)

### File Format

The file must contain exactly these 4 columns (order doesn't matter):

| Column Name  | Description | Example |
|---|---|---|
| `roll_number` | Unique student ID | 1001 |
| `name` | Full name of student | Ahmad Ali |
| `house_name` | Student's house (residence) | Iqbal |
| `class_grade` | Class/Grade (8-12) | 10 |

### Supported File Types
- CSV (.csv)
- Excel (.xlsx, .xls)

### Example CSV
```
roll_number,name,house_name,class_grade
1001,Ahmad Ali,Iqbal,10
1002,Fatima Khan,Quaid,10
1003,Hassan Ahmed,Allama,10
1004,Ayesha Malik,Iqbal,10
1005,Muhammad Usman,Quaid,10
```

### Example Excel Format
| roll_number | name | house_name | class_grade |
|---|---|---|---|
| 1001 | Ahmad Ali | Iqbal | 10 |
| 1002 | Fatima Khan | Quaid | 10 |
| 1003 | Hassan Ahmed | Allama | 10 |

### Validation Rules
- Roll number must be unique (not already registered)
- Username (roll number) must be unique
- Class grade must be 8, 9, 10, 11, or 12
- All required fields must be filled

### Errors & Warnings
- **Duplicate roll number**: If the roll number already exists
- **Invalid class**: If class is not between 8-12
- **Missing fields**: If any required column is missing

### Important Notes
- ✅ Students are automatically **approved** (no admin approval needed)
- ✅ Roll number serves as both **username and password**
- ✅ House name is optional but recommended
- ✅ Up to 1000 students can be uploaded at once (depends on file size)

---

## 2. Bulk Upload Results/Marks

### Location
- Admin Dashboard → **📋 Bulk Upload Results** button
- Direct URL: `/admin/upload_results`

### Purpose
Import marks for multiple students in a specific term/exam. Each row creates or updates a Mark record.

### Required Selections (Before Upload)
1. **Class Grade** - Select which class (8-12) the marks are for
2. **Result Type** - Choose which marks to import:
   - **1st Term** - Updates the 1st term column
   - **2nd Term** - Updates the 2nd term column
   - **Board Exam** - Updates the board exam column

### File Format

The file must contain exactly these 3 columns (order doesn't matter):

| Column Name | Description | Example |
|---|---|---|
| `roll_number` | Student's roll number | 1001 |
| `subject` | Subject name | Math |
| `mark` | Marks obtained | 72 |

### Supported File Types
- CSV (.csv)
- Excel (.xlsx, .xls)

### Example CSV (1st Term Marks for Class 10)
```
roll_number,subject,mark
1001,English,68
1001,Math,72
1001,Physics,65
1001,Chemistry,70
1002,English,72
1002,Math,78
1002,Physics,75
1002,Chemistry,80
```

### Example Excel Format
| roll_number | subject | mark |
|---|---|---|
| 1001 | English | 68 |
| 1001 | Math | 72 |
| 1001 | Physics | 65 |
| 1001 | Chemistry | 70 |
| 1002 | English | 72 |

### Subject Names by Class

**Class 8 & 9:**
- English, Urdu, Math, Bio, Physics, Chemistry, Islamiyat, Tarjamat-ul-Quran, Computer

**Class 10:**
- English, Urdu, Math, Bio, Physics, Chemistry, Pak Studies, Islamiyat, Computer

**Class 11:**
- English, Urdu, Math, Bio, Physics, Chemistry, Tarjamat-ul-Quran, Islamiyat, Computer

**Class 12:**
- English, Urdu, Math, Bio, Physics, Chemistry, Pak Studies, Computer

### Full Marks by Subject (Maximum Allowed)

**Class 8 & 9:**
| Subject | Full Marks |
|---|---|
| English | 75 |
| Urdu | 75 |
| Math | 75 |
| Bio | 65 |
| Physics | 65 |
| Chemistry | 65 |
| Islamiyat | 100 |
| Tarjamat-ul-Quran | 50 |
| Computer | 60 |

**Class 10:**
| Subject | Full Marks |
|---|---|
| English | 75 |
| Urdu | 75 |
| Math | 75 |
| Bio | 65 |
| Physics | 65 |
| Chemistry | 65 |
| Pak Studies | 50 |
| Islamiyat | 50 |
| Computer | 55 |

**Class 11:**
| Subject | Full Marks |
|---|---|
| English | 100 |
| Urdu | 100 |
| Math | 100 |
| Bio | 80 |
| Physics | 80 |
| Chemistry | 80 |
| Tarjamat-ul-Quran | 50 |
| Islamiyat | 50 |
| Computer | 80 |

**Class 12:**
| Subject | Full Marks |
|---|---|
| English | 100 |
| Urdu | 100 |
| Math | 100 |
| Bio | 85 |
| Physics | 85 |
| Chemistry | 85 |
| Pak Studies | 50 |
| Computer | 75 |

### Validation Rules
1. **Student must exist** - Roll number must be a registered student in the selected class
2. **Valid subject** - Subject must be valid for the selected class
3. **Mark validation** - Mark must not exceed the full mark for that subject
   - For example: Math in Class 10 cannot exceed 75
4. **Numeric mark** - Mark must be a valid number

### Errors & Warnings
- **Student not found**: Roll number doesn't exist in selected class
- **Invalid subject**: Subject not valid for selected class
- **Mark exceeds full mark**: Mark is higher than allowed maximum
- **Invalid mark**: Mark is not a number

### Important Notes
- ✅ Marks update the **specific result type** selected (1st, 2nd, or Board)
- ✅ Does **not** overwrite other term marks (e.g., uploading 1st term won't affect 2nd term marks)
- ✅ If a student-subject mark already exists, it **updates** the selected term
- ✅ If a student-subject mark doesn't exist, it **creates** a new record
- ✅ Up to 10,000 marks can be uploaded at once

### Workflow Example

**Scenario:** Upload 1st Term English marks for Class 10 students

1. Go to `/admin/upload_results`
2. Select **Class 10**
3. Select **1st Term**
4. Upload CSV file with columns: `roll_number`, `subject` (all "English"), `mark`
5. Example file:
   ```
   roll_number,subject,mark
   1001,English,68
   1002,English,72
   1003,English,65
   ```
6. System validates all marks ≤ 75 (full mark for English Class 10)
7. All marks are saved to the database
8. Success message shows: "✓ Successfully imported 3 mark(s) for 1st term"

---

## Sample Files

Sample files are provided in the project root:
- `sample_students.csv` - Example student list
- `sample_results_1st.csv` - Example 1st term marks

### Testing Steps

1. **Upload Students:**
   - Go to `/admin/upload_students`
   - Upload `sample_students.csv`
   - 5 students should be registered
   - Each can login with username = roll_number, password = roll_number

2. **Upload Results:**
   - Go to `/admin/upload_results`
   - Select **Class 10**
   - Select **1st Term**
   - Upload `sample_results_1st.csv`
   - 20 marks should be imported

3. **View Results:**
   - Go to `/admin/class_results`
   - Select **Class 10**
   - View the editable grid with all marks

---

## Troubleshooting

| Issue | Solution |
|---|---|
| "No file selected" | Make sure to select a file before uploading |
| "Invalid file type" | Use only CSV, XLSX, or XLS files |
| "File must contain columns..." | Check that your file has the exact column names required |
| "Row X: Roll number already exists" | That roll number is already registered; use a unique number |
| "Row X: Student not found" | The roll number doesn't exist in that class; register the student first |
| "Row X: Mark exceeds full mark" | Reduce the mark to be within the allowed maximum for that subject |

---

## API Integration

### Upload Students Endpoint
- **URL:** `/admin/upload_students`
- **Method:** POST
- **File Parameter:** `file` (CSV or Excel)
- **Response:** Redirects to admin dashboard with flash messages

### Upload Results Endpoint
- **URL:** `/admin/upload_results`
- **Method:** POST
- **Parameters:**
  - `file` (CSV or Excel file)
  - `class_grade` (8-12)
  - `result_type` (1st, 2nd, or board)
- **Response:** Redirects to admin dashboard with flash messages

---

## Tips & Best Practices

✅ **DO:**
- Validate your data before uploading
- Use consistent formatting (especially for roll numbers)
- Keep subject names exactly as specified
- Use unique roll numbers for each student
- Test with sample files first

❌ **DON'T:**
- Use marks exceeding the full mark for a subject
- Upload duplicate roll numbers
- Mix different class grades in one file
- Leave required columns empty
- Use special characters in roll numbers

---

Last Updated: December 2025
