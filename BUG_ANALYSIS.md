# Bug 分析與修復方案

## 🔴 主要問題總結

### 1. **參數名稱不匹配** (最嚴重)
- **問題**: Actor 期望 `uid` 和 `status`，但測試/前端發送 `student_uuid` 和 `student_status`
- **影響**: 所有 update 和 status APIs 失敗
- **修復**: 統一參數命名規範

### 2. **Score Model 設計與 API 不匹配**
- **問題**: Score API 期望 `update_field` + `score_value`，但測試發送完整成績物件
- **影響**: 無法創建成績記錄
- **修復**: 需要重新設計 Score API 或調整測試

### 3. **缺少資料庫約束**
- **問題**: 學號沒有唯一性約束
- **影響**: 可以創建重複學號
- **修復**: 添加 `unique=True` 約束

---

## 📋 詳細問題列表

### 問題 1: Student Update API 參數錯誤
**位置**: `student_actor.py` Line 143

```python
# 目前代碼 (錯誤)
is_valid, missing_keys = ValidationService.validate_required_keys(data, ['uid'])

# 測試發送的參數
{
    "student_uuid": "stu_xxx",  # ❌ 不是 'uid'
    "student_name": "新名字",
    "student_number": "B123"
}
```

**修復方案**:
```python
# 選項 A: 修改 Actor 接受 student_uuid
is_valid, missing_keys = ValidationService.validate_required_keys(data, ['student_uuid'])
student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])

# 選項 B: 修改測試發送 uid (不建議，不直觀)
```

---

### 問題 2: Student Status API 參數錯誤
**位置**: `student_actor.py` Line 231

```python
# 目前代碼 (錯誤)
is_valid, missing_keys = ValidationService.validate_required_keys(data, ['uid', 'status'])

# 測試發送的參數
{
    "student_uuid": "stu_xxx",    # ❌ 不是 'uid'
    "student_status": "修業完畢"  # ❌ 不是 'status'
}
```

**修復方案**:
```python
# 修改為接受 student_uuid 和 student_status
is_valid, missing_keys = ValidationService.validate_required_keys(
    data, ['student_uuid', 'student_status']
)
student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])

# 後續使用 data['student_status'] 而非 data['status']
```

---

### 問題 3: Student Delete API 參數錯誤
**位置**: `student_actor.py` Line 188

```python
# 目前代碼
is_valid, missing_keys = ValidationService.validate_required_keys(data, ['uid'])

# 應該改為
is_valid, missing_keys = ValidationService.validate_required_keys(data, ['student_uuid'])
student = SqlDbBusinessService.get_entity(Students, 'student_uuid', data['student_uuid'])
```

---

### 問題 4: Test Update/Status/Delete APIs 同樣問題
**位置**: `test_actor.py` 多處

所有 Test Actor 的 APIs 都有相同問題：
- 使用 `uid` 而非 `test_uuid`
- 使用 `status` 而非 `test_state`

**需要修改的方法**:
- `update()`: `uid` → `test_uuid`
- `delete()`: `uid` → `test_uuid`  
- `status()`: `uid` + `status` → `test_uuid` + `test_state`
- `setweight()`: `uids` + `weights` → `test_uuids` + `test_weights`

---

### 問題 5: Score API 設計問題
**位置**: `score_actor.py` Line 40

```python
# 目前設計 (適合單一欄位更新)
{
    "f_student_uuid": "stu_xxx",
    "update_field": "score_quiz1",  # 指定要更新哪個欄位
    "score_value": 85.5              # 該欄位的值
}

# 測試發送的參數 (完整物件創建)
{
    "f_student_uuid": "stu_xxx",
    "f_test_uuid": "tst_xxx",       # ❌ Model 沒有這個欄位
    "score_total": 85.5,            # ❌ 不符合 update_field 設計
    "score_percentage": 0.855        # ❌ Model 沒有這個欄位
}
```

**問題根源**: Score Model 設計與需求不符

```python
# 目前 Score Model
class Score(models.Model):
    score_quiz1 = ...      # 小考1
    score_midterm = ...    # 期中考
    score_quiz2 = ...      # 小考2
    score_finalexam = ...  # 期末考
    score_total = ...      # 總分
    f_student_uuid = ...   # 學生外鍵
    # 缺少: f_test_uuid (考卷外鍵)
    # 缺少: score_percentage
```

**修復方案**:

**選項 A: 保持現有設計，修改測試**
```python
# 測試改為逐一更新各項成績
{
    "f_student_uuid": "stu_xxx",
    "update_field": "score_midterm",
    "score_value": 85.5
}
```

**選項 B: 重新設計 Score Model (建議)**
```python
class Score(models.Model):
    score_uuid = ...
    f_student_uuid = ...   # 外鍵：學生
    f_test_uuid = ...      # 外鍵：考卷 (新增)
    score_value = ...      # 分數值
    score_percentage = ... # 百分比 (新增)
    # 移除 quiz1, midterm 等欄位，改為一對多關係
```

這樣一個學生可以有多個成績記錄（對應不同考卷）。

---

### 問題 6: 學號唯一性約束缺失
**位置**: `models/students.py` Line 25

```python
# 目前代碼 (缺少唯一性約束)
student_number = models.CharField(
    max_length=255,
    help_text="學生學號"
)

# 應該改為
student_number = models.CharField(
    max_length=255,
    unique=True,  # 添加唯一性約束
    db_index=True,  # 添加索引提升查詢效能
    help_text="學生學號"
)
```

修改後需要重新生成 migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🛠️ 完整修復步驟

### Step 1: 修復 Student Actor 參數名稱

修改 3 個方法中的參數：
1. `update()`: `uid` → `student_uuid`
2. `delete()`: `uid` → `student_uuid`
3. `status()`: `uid` + `status` → `student_uuid` + `student_status`

### Step 2: 修復 Test Actor 參數名稱

修改 4 個方法中的參數：
1. `update()`: `uid` → `test_uuid`
2. `delete()`: `uid` → `test_uuid`
3. `status()`: `uid` + `status` → `test_uuid` + `test_state`
4. `setweight()`: `uids` + `weights` → `test_uuids` + `test_weights`

### Step 3: 修復 Score Actor (選擇一個方案)

**方案 A**: 修改測試腳本適應現有 API
**方案 B**: 重新設計 Score Model 和 API (推薦但工作量大)

### Step 4: 添加學號唯一性約束

修改 Model 並重新遷移資料庫

### Step 5: 驗證修復

重新執行測試腳本確認所有問題已解決

---

## ⚡ 快速修復腳本

我將幫您創建修復所需的代碼變更。請確認是否要：

1. ✅ 修復所有 Actor 的參數名稱 (建議)
2. ✅ 添加學號唯一性約束 (建議)
3. ❓ 重新設計 Score Model (需要您決定)

---

## 📊 預期修復結果

修復後測試成功率應該從 **45%** 提升到 **85%+**

- ✅ 所有 CRUD 操作正常
- ✅ 狀態更新功能正常
- ✅ 權重設定功能正常
- ✅ 資料驗證正常
- ❌ Score APIs 需要重新設計 (如果選擇方案 B)
