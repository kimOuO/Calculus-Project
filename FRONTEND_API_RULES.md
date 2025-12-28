# 前端 API 對接規範文檔

## 基本資訊

### Base URL
```
http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/
```

### 通用規則
1. **所有 API 均使用 POST 方法**
2. **Content-Type**: `application/json` (檔案上傳除外)
3. **回應格式**: 統一 JSON 格式
4. **CSRF**: 前端請求需包含 CSRF Token（開發環境可能已關閉）

### 統一回應結構

#### 成功回應
```json
{
  "status": "success",
  "message": "操作成功訊息",
  "data": { ... },
  "code": 200/201
}
```

#### 錯誤回應
```json
{
  "status": "error",
  "message": "錯誤訊息",
  "data": null,
  "code": 400/404/500
}
```

---

## 1. 學生管理 API (Student_MetadataWriter)

### 1.1 創建學生
**Endpoint**: `POST /Student_MetadataWriter/create`

**Request Body**:
```json
{
  "student_name": "王小明",
  "student_number": "110001234",
  "student_semester": "1141",
  "student_status": "修業中"  // 選填，預設為 "修業中"
}
```

**必填欄位**:
- `student_name`: string - 學生姓名
- `student_number`: string - 學生學號（唯一）
- `student_semester`: string - 學年學期（格式如 1141, 1142）

**選填欄位**:
- `student_status`: string - 學生狀態（修業中/二退/被當/修業完畢），預設 "修業中"

**Response (201)**:
```json
{
  "status": "success",
  "message": "Student created successfully",
  "data": {
    "student_uuid": "1141_s_20240101120000",
    "student_name": "王小明",
    "student_number": "110001234",
    "student_semester": "1141",
    "student_status": "修業中",
    "student_created_at": "2024-01-01T12:00:00",
    "student_updated_at": "2024-01-01T12:00:00"
  },
  "code": 201
}
```

**備註**: 創建學生時會自動創建對應的空白成績記錄

---

### 1.2 查詢學生
**Endpoint**: `POST /Student_MetadataWriter/read`

**Request Body**:

查詢單個學生：
```json
{
  "student_uuid": "1141_s_20240101120000"
}
```

條件查詢：
```json
{
  "student_semester": "1141",
  "student_status": "修業中"
}
```

查詢全部：
```json
{}
```

**可用查詢欄位**:
- `student_uuid`: string - 學生唯一識別碼
- `student_number`: string - 學生學號
- `student_semester`: string - 學年學期
- `student_status`: string - 學生狀態
- `student_name`: string - 學生姓名

**Response (200)**:
```json
{
  "status": "success",
  "message": "Students retrieved successfully",
  "data": [
    {
      "student_uuid": "1141_s_20240101120000",
      "student_name": "王小明",
      "student_number": "110001234",
      "student_semester": "1141",
      "student_status": "修業中",
      "student_created_at": "2024-01-01T12:00:00",
      "student_updated_at": "2024-01-01T12:00:00"
    }
  ],
  "code": 200
}
```

---

### 1.3 更新學生
**Endpoint**: `POST /Student_MetadataWriter/update`

**Request Body**:
```json
{
  "student_uuid": "1141_s_20240101120000",
  "student_name": "王大明",
  "student_status": "被當"
}
```

**必填欄位**:
- `student_uuid`: string - 學生唯一識別碼

**可更新欄位**:
- `student_name`: string - 學生姓名
- `student_number`: string - 學生學號
- `student_semester`: string - 學年學期
- `student_status`: string - 學生狀態

**Response (200)**:
```json
{
  "status": "success",
  "message": "Student updated successfully",
  "data": {
    "student_uuid": "1141_s_20240101120000",
    "student_name": "王大明",
    "student_status": "被當",
    ...
  },
  "code": 200
}
```

---

### 1.4 刪除學生
**Endpoint**: `POST /Student_MetadataWriter/delete`

**Request Body**:
```json
{
  "student_uuid": "1141_s_20240101120000"
}
```

**必填欄位**:
- `student_uuid`: string - 學生唯一識別碼

**Response (200)**:
```json
{
  "status": "success",
  "message": "Student deleted successfully",
  "data": null,
  "code": 200
}
```

**備註**: 刪除學生時會自動級聯刪除該學生的所有成績記錄

---

### 1.5 查詢學生狀態
**Endpoint**: `POST /Student_MetadataWriter/status`

**Request Body**:
```json
{
  "student_semester": "1141"
}
```

**必填欄位**:
- `student_semester`: string - 學年學期

**Response (200)**:
```json
{
  "status": "success",
  "message": "Student status retrieved successfully",
  "data": {
    "修業中": 25,
    "修業完畢": 10,
    "被當": 3,
    "二退": 2
  },
  "code": 200
}
```

---

## 2. 成績管理 API (Score_MetadataWriter)

### 2.1 創建/更新分數
**Endpoint**: `POST /Score_MetadataWriter/create`

**Request Body**:
```json
{
  "f_student_uuid": "1141_s_20240101120000",
  "update_field": "score_quiz1",
  "score_value": "85"
}
```

**必填欄位**:
- `f_student_uuid`: string - 學生 UUID
- `update_field`: string - 要更新的分數欄位（score_quiz1/score_midterm/score_quiz2/score_finalexam）
- `score_value`: string/number - 分數值（0-100 或空字串）

**允許的 update_field 值**:
- `score_quiz1`: 第一次小考
- `score_midterm`: 期中考
- `score_quiz2`: 第二次小考
- `score_finalexam`: 期末考

**Response (201)**:
```json
{
  "status": "success",
  "message": "Score created successfully",
  "data": {
    "score_uuid": "1141_sc_20240101120000",
    "f_student_uuid": "1141_s_20240101120000",
    "score_quiz1": "85",
    "score_midterm": "",
    "score_quiz2": "",
    "score_finalexam": "",
    "score_total": "",
    "score_created_at": "2024-01-01T12:00:00",
    "score_updated_at": "2024-01-01T12:00:00"
  },
  "code": 201
}
```

---

### 2.2 查詢成績
**Endpoint**: `POST /Score_MetadataWriter/read`

**Request Body**:

按 score_uuid 查詢：
```json
{
  "score_uuid": "1141_sc_20240101120000"
}
```

按學生查詢：
```json
{
  "f_student_uuid": "1141_s_20240101120000"
}
```

查詢全部：
```json
{}
```

**Response (200)**:
```json
{
  "status": "success",
  "message": "Scores retrieved successfully",
  "data": [
    {
      "score_uuid": "1141_sc_20240101120000",
      "f_student_uuid": "1141_s_20240101120000",
      "score_quiz1": "85",
      "score_midterm": "78",
      "score_quiz2": "90",
      "score_finalexam": "82",
      "score_total": "",
      "score_created_at": "2024-01-01T12:00:00",
      "score_updated_at": "2024-01-01T12:10:00"
    }
  ],
  "code": 200
}
```

---

### 2.3 更新成績
**Endpoint**: `POST /Score_MetadataWriter/update`

**Request Body**:
```json
{
  "score_uuid": "1141_sc_20240101120000",
  "update_field": "score_midterm",
  "score_value": "88"
}
```

**必填欄位**:
- `score_uuid`: string - 成績 UUID
- `update_field`: string - 要更新的分數欄位
- `score_value`: string/number - 分數值

**Response (200)**:
```json
{
  "status": "success",
  "message": "Score updated successfully",
  "data": { ... },
  "code": 200
}
```

---

### 2.4 刪除成績
**Endpoint**: `POST /Score_MetadataWriter/delete`

**Request Body**:
```json
{
  "score_uuid": "1141_sc_20240101120000"
}
```

**必填欄位**:
- `score_uuid`: string - 成績 UUID

**Response (200)**:
```json
{
  "status": "success",
  "message": "Score deleted successfully",
  "data": null,
  "code": 200
}
```

---

### 2.5 計算期末總成績
**Endpoint**: `POST /Score_MetadataWriter/calculation_final`

**Request Body**:
```json
{
  "test_semester": "1141",
  "passing_score": 60
}
```

**必填欄位**:
- `test_semester`: string - 學年學期
- `passing_score`: number - 及格分數線

**Response (200)**:
```json
{
  "status": "success",
  "message": "Final scores calculated successfully for 25 students",
  "data": {
    "updated_count": 25
  },
  "code": 200
}
```

**備註**:
- 需先設定考試權重（使用 `/Test_MetadataWriter/setweight`）
- 權重總和必須為 1.0
- 會自動更新學生狀態（修業完畢/被當）
- 只計算有完整四項成績的學生
- 不計算二退學生

---

### 2.6 計算考試統計
**Endpoint**: `POST /Score_MetadataWriter/test_score`

**Request Body**:
```json
{
  "score_semester": "1141",
  "score_field": "score_quiz1",
  "exclude_empty": true
}
```

**必填欄位**:
- `score_semester`: string - 學年學期
- `score_field`: string - 要統計的分數欄位

**選填欄位**:
- `exclude_empty`: boolean - 是否排除空值，預設 true

**Response (200)**:
```json
{
  "status": "success",
  "message": "Test statistics calculated successfully",
  "data": {
    "semester": "1141",
    "score_field": "score_quiz1",
    "total_count": 25,
    "average": 78.5,
    "median": 80.0
  },
  "code": 200
}
```

---

## 3. 考試管理 API (Test_MetadataWriter)

### 3.1 創建考試
**Endpoint**: `POST /Test_MetadataWriter/create`

**Request Body**:
```json
{
  "test_name": "第一次小考",
  "test_date": "2024-03-15",
  "test_range": "Chapter 1-3",
  "test_semester": "1141",
  "test_weight": "0.2"
}
```

**必填欄位**:
- `test_name`: string - 考試名稱
- `test_date`: string - 考試日期
- `test_range`: string - 考試範圍
- `test_semester`: string - 學年學期

**選填欄位**:
- `test_weight`: string - 權重（0-1 之間，預設空字串）

**Response (201)**:
```json
{
  "status": "success",
  "message": "Test created successfully",
  "data": {
    "test_uuid": "1141_q1_20240101120000",
    "test_name": "第一次小考",
    "test_date": "2024-03-15",
    "test_range": "Chapter 1-3",
    "test_semester": "1141",
    "test_weight": "0.2",
    "test_states": "尚未出考卷",
    "pt_opt_score_uuid": "",
    "test_created_at": "2024-01-01T12:00:00",
    "test_updated_at": "2024-01-01T12:00:00"
  },
  "code": 201
}
```

---

### 3.2 查詢考試
**Endpoint**: `POST /Test_MetadataWriter/read`

**Request Body**:

按 UUID 查詢：
```json
{
  "test_uuid": "1141_q1_20240101120000"
}
```

按學期查詢：
```json
{
  "test_semester": "1141"
}
```

查詢全部：
```json
{}
```

**Response (200)**:
```json
{
  "status": "success",
  "message": "Tests retrieved successfully",
  "data": [
    {
      "test_uuid": "1141_q1_20240101120000",
      "test_name": "第一次小考",
      "test_date": "2024-03-15",
      "test_range": "Chapter 1-3",
      "test_semester": "1141",
      "test_weight": "0.2",
      "test_states": "尚未出考卷",
      ...
    }
  ],
  "code": 200
}
```

---

### 3.3 更新考試
**Endpoint**: `POST /Test_MetadataWriter/update`

**Request Body**:
```json
{
  "test_uuid": "1141_q1_20240101120000",
  "test_name": "第一次小考（修訂版）",
  "test_range": "Chapter 1-4"
}
```

**必填欄位**:
- `test_uuid`: string - 考試 UUID

**可更新欄位**:
- `test_name`: string - 考試名稱
- `test_date`: string - 考試日期
- `test_range`: string - 考試範圍
- `test_weight`: string - 權重

**Response (200)**:
```json
{
  "status": "success",
  "message": "Test updated successfully",
  "data": { ... },
  "code": 200
}
```

---

### 3.4 刪除考試
**Endpoint**: `POST /Test_MetadataWriter/delete`

**Request Body**:
```json
{
  "test_uuid": "1141_q1_20240101120000"
}
```

**必填欄位**:
- `test_uuid`: string - 考試 UUID

**Response (200)**:
```json
{
  "status": "success",
  "message": "Test deleted successfully",
  "data": null,
  "code": 200
}
```

---

### 3.5 更新考試狀態
**Endpoint**: `POST /Test_MetadataWriter/status`

**Request Body**:
```json
{
  "test_uuid": "1141_q1_20240101120000",
  "test_state": "考卷完成"
}
```

**必填欄位**:
- `test_uuid`: string - 考試 UUID
- `test_state`: string - 考試狀態

**允許的狀態值**:
- `尚未出考卷`: 初始狀態
- `考卷完成`: 考卷已完成
- `考卷成績結算`: 成績已結算

**Response (200)**:
```json
{
  "status": "success",
  "message": "Test status updated successfully",
  "data": { ... },
  "code": 200
}
```

---

### 3.6 設定考試權重
**Endpoint**: `POST /Test_MetadataWriter/setweight`

**Request Body**:
```json
{
  "test_semester": "1141",
  "weights": {
    "第一次小考": "0.2",
    "期中考": "0.3",
    "第二次小考": "0.2",
    "期末考": "0.3"
  }
}
```

**必填欄位**:
- `test_semester`: string - 學年學期
- `weights`: object - 權重對照表（key 為考試名稱，value 為權重）

**驗證規則**:
- 所有權重總和必須為 1.0
- 權重值為 0-1 之間的數字（字串格式）

**Response (200)**:
```json
{
  "status": "success",
  "message": "Weights set successfully for 4 tests",
  "data": {
    "updated_count": 4
  },
  "code": 200
}
```

**備註**: 設定權重後會自動將考試狀態更新為 "考卷成績結算"

---

## 4. 考卷檔案管理 API (test-filedata - NonSQL)

### 4.1 上傳考卷檔案
**Endpoint**: `POST /test-filedata/create`

**Content-Type**: `multipart/form-data`

**Request Body** (FormData):
```
test_uuid: "1141_q1_20240101120000"
asset_type: "paper"
file: [File Object(s)]
```

**必填欄位**:
- `test_uuid`: string - 考試 UUID
- `asset_type`: string - 資產類型
- `file`: File(s) - 檔案物件（可多個）

**允許的 asset_type 值**:
- `paper`: 考卷
- `test_pic`: 考試圖片
- `histogram`: 直方圖
- `test_pic_histogram`: 考試圖片直方圖

**Response (201)**:
```json
{
  "status": "success",
  "message": "Files uploaded successfully",
  "data": {
    "file_uuid": "1141_file_20240101120000",
    "asset_type": "paper",
    "file_count": 1,
    "mongodb_id": "507f1f77bcf86cd799439011"
  },
  "code": 201
}
```

---

### 4.2 讀取考卷檔案
**Endpoint**: `POST /test-filedata/read`

**Request Body**:
```json
{
  "test_pic_uuid": "1141_file_20240101120000",
  "asset_type": "paper"
}
```

**必填欄位**:
- `test_pic_uuid`: string - 檔案 UUID
- `asset_type`: string - 資產類型

**Response**: 直接返回檔案（File Response）
- Content-Type: image/jpeg (或對應的檔案類型)
- Content-Disposition: inline; filename="..."

---

### 4.3 更新考卷檔案
**Endpoint**: `POST /test-filedata/update`

**Content-Type**: `multipart/form-data`

**Request Body** (FormData):
```
uid: "1141_file_20240101120000"
asset_type: "paper"
file: [File Object]
```

**必填欄位**:
- `uid`: string - 檔案 UUID
- `asset_type`: string - 資產類型
- `file`: File - 新檔案物件

**Response (200)**:
```json
{
  "status": "success",
  "message": "File updated successfully",
  "data": {
    "file_uuid": "1141_file_20240101120000",
    "asset_type": "paper"
  },
  "code": 200
}
```

**備註**: 會替換原有檔案

---

### 4.4 刪除考卷檔案
**Endpoint**: `POST /test-filedata/delete`

**Request Body**:
```json
{
  "uid": "1141_file_20240101120000",
  "asset_type": "paper"
}
```

**必填欄位**:
- `uid`: string - 檔案 UUID
- `asset_type`: string - 資產類型

**Response (200)**:
```json
{
  "status": "success",
  "message": "File deleted successfully",
  "data": null,
  "code": 200
}
```

---

## 5. 錯誤碼說明

### HTTP 狀態碼
- `200`: 操作成功
- `201`: 創建成功
- `400`: 客戶端錯誤（參數錯誤、驗證失敗）
- `404`: 資源不存在
- `500`: 伺服器內部錯誤

### 常見錯誤訊息

#### 400 錯誤
```json
{
  "status": "error",
  "message": "Missing required keys: ['student_uuid']",
  "data": null,
  "code": 400
}
```

```json
{
  "status": "error",
  "message": "Invalid JSON format",
  "data": null,
  "code": 400
}
```

```json
{
  "status": "error",
  "message": "Validation failed",
  "data": {
    "student_number": ["This field is required."]
  },
  "code": 400
}
```

#### 404 錯誤
```json
{
  "status": "error",
  "message": "Student not found",
  "data": null,
  "code": 404
}
```

#### 500 錯誤
```json
{
  "status": "error",
  "message": "Unknown error: Database connection failed",
  "data": null,
  "code": 500
}
```

---

## 6. 前端實作建議

### 6.1 API 封裝範例（JavaScript/TypeScript）

```typescript
// api.ts
const BASE_URL = 'http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata';

interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message: string;
  data: T | null;
  code: number;
}

class CalculusAPI {
  // 通用請求方法
  private async request<T>(endpoint: string, data: any = {}): Promise<ApiResponse<T>> {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }

  // 學生相關 API
  async createStudent(data: {
    student_name: string;
    student_number: string;
    student_semester: string;
    student_status?: string;
  }) {
    return this.request('/Student_MetadataWriter/create', data);
  }

  async readStudents(filters: any = {}) {
    return this.request('/Student_MetadataWriter/read', filters);
  }

  async updateStudent(student_uuid: string, updates: any) {
    return this.request('/Student_MetadataWriter/update', {
      student_uuid,
      ...updates,
    });
  }

  async deleteStudent(student_uuid: string) {
    return this.request('/Student_MetadataWriter/delete', { student_uuid });
  }

  async getStudentStatus(student_semester: string) {
    return this.request('/Student_MetadataWriter/status', { student_semester });
  }

  // 成績相關 API
  async createScore(data: {
    f_student_uuid: string;
    update_field: 'score_quiz1' | 'score_midterm' | 'score_quiz2' | 'score_finalexam';
    score_value: string | number;
  }) {
    return this.request('/Score_MetadataWriter/create', data);
  }

  async readScores(filters: any = {}) {
    return this.request('/Score_MetadataWriter/read', filters);
  }

  async calculateFinalScores(test_semester: string, passing_score: number) {
    return this.request('/Score_MetadataWriter/calculation_final', {
      test_semester,
      passing_score,
    });
  }

  async getTestStatistics(score_semester: string, score_field: string) {
    return this.request('/Score_MetadataWriter/test_score', {
      score_semester,
      score_field,
    });
  }

  // 考試相關 API
  async createTest(data: {
    test_name: string;
    test_date: string;
    test_range: string;
    test_semester: string;
    test_weight?: string;
  }) {
    return this.request('/Test_MetadataWriter/create', data);
  }

  async readTests(filters: any = {}) {
    return this.request('/Test_MetadataWriter/read', filters);
  }

  async updateTestStatus(test_uuid: string, test_state: string) {
    return this.request('/Test_MetadataWriter/status', {
      test_uuid,
      test_state,
    });
  }

  async setTestWeights(test_semester: string, weights: Record<string, string>) {
    return this.request('/Test_MetadataWriter/setweight', {
      test_semester,
      weights,
    });
  }

  // 檔案上傳 API
  async uploadFile(test_uuid: string, asset_type: string, files: File[]) {
    const formData = new FormData();
    formData.append('test_uuid', test_uuid);
    formData.append('asset_type', asset_type);
    files.forEach(file => formData.append('file', file));

    const response = await fetch(`${BASE_URL}/test-filedata/create`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  }

  async downloadFile(test_pic_uuid: string, asset_type: string) {
    const response = await fetch(`${BASE_URL}/test-filedata/read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ test_pic_uuid, asset_type }),
    });
    return response.blob();
  }
}

export const api = new CalculusAPI();
```

### 6.2 使用範例

```typescript
// 創建學生
const result = await api.createStudent({
  student_name: '王小明',
  student_number: '110001234',
  student_semester: '1141',
});

if (result.status === 'success') {
  console.log('學生創建成功:', result.data);
} else {
  console.error('創建失敗:', result.message);
}

// 查詢學生
const students = await api.readStudents({ student_semester: '1141' });

// 更新成績
await api.createScore({
  f_student_uuid: '1141_s_20240101120000',
  update_field: 'score_quiz1',
  score_value: '85',
});

// 上傳檔案
const fileInput = document.querySelector('input[type="file"]');
const files = Array.from(fileInput.files);
await api.uploadFile('1141_q1_20240101120000', 'paper', files);
```

---

## 7. 資料模型說明

### 7.1 學生 (Students)
```typescript
interface Student {
  student_uuid: string;          // 唯一識別碼（後端自動生成）
  student_name: string;           // 學生姓名
  student_number: string;         // 學生學號（唯一）
  student_semester: string;       // 學年學期（如 1141）
  student_status: string;         // 狀態（修業中/二退/被當/修業完畢）
  student_created_at: string;     // 創建時間（後端自動生成）
  student_updated_at: string;     // 更新時間（後端自動維護）
}
```

### 7.2 成績 (Score)
```typescript
interface Score {
  score_uuid: string;             // 唯一識別碼（後端自動生成）
  f_student_uuid: string;         // 關聯學生 UUID
  score_quiz1: string;            // 第一次小考（0-100 或空字串）
  score_midterm: string;          // 期中考（0-100 或空字串）
  score_quiz2: string;            // 第二次小考（0-100 或空字串）
  score_finalexam: string;        // 期末考（0-100 或空字串）
  score_total: string;            // 總分（計算後填入）
  score_created_at: string;       // 創建時間（後端自動生成）
  score_updated_at: string;       // 更新時間（後端自動維護）
}
```

### 7.3 考試 (Test)
```typescript
interface Test {
  test_uuid: string;              // 唯一識別碼（後端自動生成）
  test_name: string;              // 考試名稱
  test_date: string;              // 考試日期
  test_range: string;             // 考試範圍
  test_semester: string;          // 學年學期
  test_weight: string;            // 權重（0-1 或空字串）
  test_states: string;            // 狀態（尚未出考卷/考卷完成/考卷成績結算）
  pt_opt_score_uuid: string;      // 關聯 MongoDB 檔案 UUID
  test_created_at: string;        // 創建時間（後端自動生成）
  test_updated_at: string;        // 更新時間（後端自動維護）
}
```

### 7.4 考卷檔案 (TestFileData - MongoDB)
```typescript
interface TestFileData {
  test_pic_uuid: string;          // 唯一識別碼（後端自動生成）
  test_pic: string;               // 考卷/圖片檔案路徑
  test_pic_histogram: string;     // 直方圖檔案路徑
  pic_created_at: string;         // 創建時間（後端自動生成）
  pic_updated_at: string;         // 更新時間（後端自動維護）
}
```

---

## 8. 業務流程建議

### 8.1 學期初始化流程
1. 創建考試記錄（4 場考試）
2. 批量創建學生資料
3. 系統自動為每個學生創建空白成績記錄

### 8.2 考試成績錄入流程
1. 上傳考卷檔案（`/test-filedata/create`）
2. 更新考試狀態為 "考卷完成"（`/Test_MetadataWriter/status`）
3. 為學生錄入成績（`/Score_MetadataWriter/create`）
4. 上傳成績直方圖（`/test-filedata/create`）
5. 更新考試狀態為 "考卷成績結算"

### 8.3 期末結算流程
1. 設定考試權重（`/Test_MetadataWriter/setweight`）
2. 計算期末總成績（`/Score_MetadataWriter/calculation_final`）
3. 查詢學生狀態統計（`/Student_MetadataWriter/status`）

---

## 9. 注意事項

### 9.1 UUID 格式
- 學生: `{semester}_s_{timestamp}` (如: `1141_s_20240101120000`)
- 成績: `{semester}_sc_{timestamp}` (如: `1141_sc_20240101120000`)
- 考試: `{semester}_{type}_{timestamp}` (如: `1141_q1_20240101120000`)
- 檔案: `{semester}_file_{timestamp}` (如: `1141_file_20240101120000`)

### 9.2 資料驗證
- 所有 UUID 由後端自動生成，前端不需提供
- 學號必須唯一
- 分數必須在 0-100 之間或為空字串
- 考試權重總和必須為 1.0
- 時間戳由後端自動生成和更新

### 9.3 級聯操作
- 刪除學生會自動刪除其所有成績記錄
- 創建學生會自動創建空白成績記錄
- 設定權重會自動更新考試狀態

### 9.4 狀態管理
**學生狀態**:
- 修業中（預設）
- 二退（不參與成績計算）
- 被當（總分低於及格線）
- 修業完畢（總分達到及格線）

**考試狀態**:
- 尚未出考卷（預設）
- 考卷完成
- 考卷成績結算（設定權重後自動更新）

---

## 10. 開發環境配置

### 10.1 後端啟動
```bash
cd Calculus_oom
docker-compose up -d
```

### 10.2 API 測試
可使用 Postman、Thunder Client 或直接使用專案提供的測試腳本：
```bash
python test_all_apis.py
```

### 10.3 前端開發建議
- 建立統一的 API Service 層
- 實作錯誤處理機制
- 添加 loading 狀態
- 實作資料快取（適當情況下）
- 處理檔案上傳進度

---

## 附錄：完整 API 端點清單

| 分類 | 端點 | 方法 | 說明 |
|-----|------|------|------|
| 學生 | `/Student_MetadataWriter/create` | POST | 創建學生 |
| 學生 | `/Student_MetadataWriter/read` | POST | 查詢學生 |
| 學生 | `/Student_MetadataWriter/update` | POST | 更新學生 |
| 學生 | `/Student_MetadataWriter/delete` | POST | 刪除學生 |
| 學生 | `/Student_MetadataWriter/status` | POST | 查詢學生狀態統計 |
| 成績 | `/Score_MetadataWriter/create` | POST | 創建/更新分數 |
| 成績 | `/Score_MetadataWriter/read` | POST | 查詢成績 |
| 成績 | `/Score_MetadataWriter/update` | POST | 更新成績 |
| 成績 | `/Score_MetadataWriter/delete` | POST | 刪除成績 |
| 成績 | `/Score_MetadataWriter/calculation_final` | POST | 計算期末總成績 |
| 成績 | `/Score_MetadataWriter/test_score` | POST | 計算考試統計 |
| 考試 | `/Test_MetadataWriter/create` | POST | 創建考試 |
| 考試 | `/Test_MetadataWriter/read` | POST | 查詢考試 |
| 考試 | `/Test_MetadataWriter/update` | POST | 更新考試 |
| 考試 | `/Test_MetadataWriter/delete` | POST | 刪除考試 |
| 考試 | `/Test_MetadataWriter/status` | POST | 更新考試狀態 |
| 考試 | `/Test_MetadataWriter/setweight` | POST | 設定考試權重 |
| 檔案 | `/test-filedata/create` | POST | 上傳考卷檔案 |
| 檔案 | `/test-filedata/read` | POST | 讀取考卷檔案 |
| 檔案 | `/test-filedata/update` | POST | 更新考卷檔案 |
| 檔案 | `/test-filedata/delete` | POST | 刪除考卷檔案 |

**總計**: 20 個 API 端點

---

文檔版本: v1.0  
最後更新: 2024-01-01  
維護者: Backend Team
