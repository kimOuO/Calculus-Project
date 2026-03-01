# Calculus OOM Backend - 詳細 Use Case API 對照表

## 📊 Use Case 總覽

| Use Case ID | 場景名稱 | 涉及 API 數量 | 主要角色 | 業務價值 |
|-------------|----------|---------------|----------|----------|
| UC-01 | 學生資料建立 | 2 個 | 管理員 | 建立學期學生名單（含 Email） |
| UC-02 | 學生資料查詢 | 1 個 | 管理員/教師 | 查看學生資訊 |
| UC-03 | 學生資料更新 | 1 個 | 管理員 | 修正學生資訊 |
| UC-04 | 學生狀態管理 | 1 個 | 管理員 | 處理學生異動 |
| UC-05 | 學生資料匯出 | 1 個 | 管理員/教師 | 產生成績報表（被當紅色標記） |
| UC-06 | 考試規劃建立 | 1 個 | 管理員/教師 | 規劃考試安排 |
| UC-07 | 考試資料查詢 | 1 個 | 管理員/教師 | 查看考試資訊 |
| UC-08 | 考試資料更新 | 1 個 | 管理員/教師 | 修正考試資訊 |
| UC-09 | 考試權重設定 | 1 個 | 管理員/教師 | 設定成績計算權重 |
| UC-10 | 考卷檔案管理 | 4 個 | 管理員/教師 | 考卷上傳與 GridFS 管理 |
| UC-11 | 成績錄入管理 | 2 個 | 教師 | 錄入考試成績 |
| UC-12 | 成績查詢檢視 | 1 個 | 教師/學生 | 查看成績資料 |
| UC-13 | 總成績計算 | 1 個 | 教師 | 計算學期總分 |
| UC-14 | 成績統計分析 | 2 個 | 教師/管理員 | 分析成績分布 |
| UC-15 | 完整學期流程 | 15+ 個 | 全角色 | 端到端業務流程 |

---

## 🔍 詳細 Use Case 分析

### UC-01: 學生資料建立
**業務場景**: 新學期開始時建立學生名單

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 單筆建立學生 | `/Student_MetadataWriter/create` | POST | `student_name`, `student_number`, `student_semester`, `student_email`(選填) | `student_uuid`, 學生完整資訊 |
| 批量匯入學生 | `/Student_MetadataWriter/upload_excel` | POST (multipart) | `file`(Excel), `student_semester`(POST參數) | 成功匯入數量, 錯誤列表 |

**Excel 欄位對應（upload_excel）**:
| Excel 欄 | 索引 | 對應欄位 | 備註 |
|----------|------|----------|------|
| Col A | 0 | student_name | 名字 |
| Col B | 1 | — | 跳過（姓氏/@帳號） |
| Col C | 2 | student_number | 學號（唯一鍵） |
| Col D | 3 | student_email | 電子郵件信箱 |
| Col E | 4 | — | 跳過（科系） |
| Col F | 5 | — | 跳過（分組） |

**前置條件**: 學期代碼已確定（由呼叫方以 POST 參數傳入）
**後置條件**: 學生資料已建立，狀態為「修業中」；同時自動建立對應空白 Score 記錄
**異常處理**:
- 重複學號 → 跳過該筆，回報 `errors` 列表，不中斷其他筆
- 缺少 `student_semester` POST 參數 → 400 錯誤
- 欄位不足 4 欄 → 跳過該行並記錄錯誤

---

### UC-02: 學生資料查詢
**業務場景**: 查詢學生基本資料與狀態

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 單筆查詢 | `/Student_MetadataWriter/read` | POST | `student_uuid` | 單一學生完整資訊（含 student_email） |
| 條件查詢 | `/Student_MetadataWriter/read` | POST | `student_semester`, `student_status` | 符合條件的學生列表 |
| 全部查詢 | `/Student_MetadataWriter/read` | POST | `{}` (空物件) | 所有學生資料 |

**前置條件**: 學生資料已存在
**後置條件**: 無狀態變更
**異常處理**: 資料不存在回傳 404

---

### UC-03: 學生資料更新
**業務場景**: 修正學生個人資訊

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 更新學生資訊 | `/Student_MetadataWriter/update` | POST | `student_uuid`, 更新欄位（可含 `student_email`） | 更新後的完整資訊 |

**前置條件**: 學生資料已存在
**後置條件**: 學生資料已更新
**異常處理**: UUID 不存在、資料格式錯誤

---

### UC-04: 學生狀態管理
**業務場景**: 處理學生學籍異動

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 狀態變更 | `/Student_MetadataWriter/status` | POST | `student_uuid`, `student_status` | 更新後狀態 |

**狀態流程**: 修業中 → {二退, 被當, 修業完畢}
**前置條件**: 學生資料已存在
**後置條件**: 學生狀態已更新；若為「二退」則所有成績欄位清空為 `''`
**異常處理**: 無效狀態值 → 400 錯誤

---

### UC-05: 學生資料匯出
**業務場景**: 產生學期成績報表

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| Excel 匯出 | `/Student_MetadataWriter/feedback_excel` | POST | `student_semester` | Excel 檔案下載（.xlsx） |

**匯出欄位**:
| 欄位 | 來源 | 備註 |
|------|------|------|
| 學生名字 | Students.student_name | |
| 學號 | Students.student_number | |
| 第一次小考 | Score.score_quiz1 | |
| 期中考 | Score.score_midterm | |
| 第二次小考 | Score.score_quiz2 | |
| 期末考 | Score.score_finalexam | |
| 最後成績 | Score.score_total | |
| 是否被當 | Students.student_status == '被當' | 被當整行淡紅底（FFCCCC）+ 紅字（CC0000） |

**前置條件**: 學期資料完整
**後置條件**: 無狀態變更
**異常處理**: 學期不存在、無學生資料 → 404

---

### UC-06: 考試規劃建立
**業務場景**: 建立學期考試安排

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 建立考試 | `/Test_MetadataWriter/create` | POST | `test_name`, `test_semester`, `test_date`, `test_range`, `test_weight` | `test_uuid`, 考試完整資訊 |

**前置條件**: 學期已規劃
**後置條件**: 考試資料已建立，`test_states` 為「尚未出考卷」
**異常處理**: 重複考試名稱檢查

---

### UC-07: 考試資料查詢
**業務場景**: 查詢考試基本資訊

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 單筆查詢 | `/Test_MetadataWriter/read` | POST | `test_uuid` | 單一考試完整資訊（含 pt_opt_score_uuid） |
| 學期查詢 | `/Test_MetadataWriter/read` | POST | `test_semester` | 該學期所有考試 |

**前置條件**: 考試資料已存在
**後置條件**: 無狀態變更
**異常處理**: 資料不存在回傳 404

---

### UC-08: 考試資料更新
**業務場景**: 修正考試資訊

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 更新考試資訊 | `/Test_MetadataWriter/update` | POST | `test_uuid`, 更新欄位 | 更新後的完整資訊 |

**前置條件**: 考試資料已存在
**後置條件**: 考試資料已更新
**異常處理**: UUID 不存在、資料格式錯誤

---

### UC-09: 考試權重設定
**業務場景**: 設定各考試在總成績中的權重

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 批量設定權重 | `/Test_MetadataWriter/setweight` | POST | `test_semester`, `weights` 物件 | 設定結果確認 |

**權重規則**: 所有權重總和必須等於 1.0
**前置條件**: 考試資料已存在
**後置條件**: 考試 `test_weight` 欄位已更新
**異常處理**: 權重總和驗證、考試不存在

---

### UC-10: 考卷檔案管理
**業務場景**: 考卷與圖表檔案的完整管理（MongoDB GridFS 存儲）

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 上傳檔案 | `/test-filedata/create` | POST (multipart) | `test_uuid`, `asset_type`, `file` | `file_uuid`, `gridfs_id` |
| 讀取檔案 | `/test-filedata/read` | POST | `test_pic_uuid`, `asset_type` | 二進位檔案（Content-Type 正確） |
| 更新檔案 | `/test-filedata/update` | POST (multipart) | `uid`, `asset_type`, `file` | 新 `gridfs_id` |
| 刪除檔案 | `/test-filedata/delete` | POST | `test_pic_uuid`, `asset_type` | 刪除成功確認 |

**檔案類型（asset_type）**:
| 值 | GridFS 欄位 | 考試狀態自動更新 |
|----|-------------|-----------------|
| `paper` / `test_pic` | `test_pic_gridfs_id` | 尚未出考卷 → 考卷完成 |
| `histogram` / `test_pic_histogram` | `test_pic_histogram_gridfs_id` | 考卷完成 → 考卷成績結算 |

**MongoDB 文件結構（test_pic_information 集合）**:
```json
{
  "test_pic_uuid": "tpic_...",
  "test_uuid": "tst_...",
  "test_semester": "1131",
  "test_name": "期中考",
  "test_pic_gridfs_id": "<ObjectId>",
  "test_pic_histogram_gridfs_id": "<ObjectId>",
  "pic_created_at": "...",
  "pic_updated_at": "..."
}
```

**讀取優先順序**: GridFS（gridfs_id 不為空）→ 本地磁碟路徑（向下相容舊格式）

**前置條件**: 考試資料已存在（含 test_uuid）
**後置條件**: 檔案存入 GridFS；若覆蓋則舊 GridFS 檔案自動刪除
**異常處理**: 檔案格式/大小驗證（前端）、GridFS 錯誤

---

### UC-11: 成績錄入管理
**業務場景**: 錄入與維護學生考試成績

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 建立成績 | `/Score_MetadataWriter/create` | POST | `f_student_uuid`, `update_field`, `score_value` | `score_uuid`, 成績資訊 |
| 更新成績 | `/Score_MetadataWriter/update` | POST | `score_uuid`, `update_field`, `score_value` | 更新後成績資訊 |

**成績欄位（update_field）**: `score_quiz1`, `score_midterm`, `score_quiz2`, `score_finalexam`
**前置條件**: 學生資料已存在
**後置條件**: 成績記錄已建立/更新
**異常處理**: 分數範圍驗證、學生不存在

---

### UC-12: 成績查詢檢視
**業務場景**: 查看學生成績資料

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 學生成績查詢 | `/Score_MetadataWriter/read` | POST | `f_student_uuid` | 學生所有成績 |
| 成績ID查詢 | `/Score_MetadataWriter/read` | POST | `score_uuid` | 單筆成績詳細資訊 |

**前置條件**: 成績資料已存在
**後置條件**: 無狀態變更
**異常處理**: 資料不存在回傳 404

---

### UC-13: 總成績計算
**業務場景**: 根據權重計算學期總成績

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 計算總成績 | `/Score_MetadataWriter/calculation_final` | POST | `test_semester`, `passing_score` | 計算結果統計 |

**計算邏輯**: 加權平均 = Σ(成績 × 權重)
**前置條件**: 權重已設定、成績已錄入
**後置條件**: `score_total` 更新；低於 `passing_score` 的學生狀態更新為「被當」
**異常處理**: 權重驗證、成績不完整

---

### UC-14: 成績統計分析
**業務場景**: 產生成績統計與視覺化分析

| 子場景 | API 端點 | HTTP 方法 | 主要參數 | 回應資料 |
|--------|----------|-----------|----------|----------|
| 統計分析 | `/Score_MetadataWriter/test_score` | POST | `score_semester`, `score_field` | 平均分、中位數等統計 |
| 分布圖產生 | `/Score_MetadataWriter/step_diagram` | POST | `score_semester`, `score_field` | 直方圖存入 GridFS，回傳 file_uuid |

**統計指標**: 平均分、中位數、標準差
**直方圖存儲**: 存入 MongoDB GridFS（`test_pic_histogram_gridfs_id`）
**前置條件**: 成績資料充足
**後置條件**: 統計結果產生；圖表存入 GridFS；考試狀態更新為「考卷成績結算」
**異常處理**: 資料不足、圖表生成失敗

---

### UC-15: 完整學期流程
**業務場景**: 端到端完整學期管理流程

| 階段 | 涉及 Use Case | API 呼叫順序 | 預期結果 |
|------|---------------|--------------|----------|
| 1. 學期初始化 | UC-01, UC-06 | Student/upload_excel(+semester) → Test/create | 學生名單（含email）、考試規劃完成 |
| 2. 考試準備 | UC-09, UC-10 | Test/setweight → test-filedata/create | 權重設定、考卷上傳至 GridFS 完成 |
| 3. 成績管理 | UC-11, UC-12 | Score/create → Score/read | 成績錄入、驗證完成 |
| 4. 結果產出 | UC-13, UC-14, UC-05 | Score/calculation_final → Score/step_diagram → Student/feedback_excel | 總分計算、圖表生成、報表匯出（被當紅色標記）完成 |

**完整流程時間**: 約一學期 (4個月)
**關鍵檢查點**: 權重驗證、成績完整性、計算正確性
**回滾機制**: 支援成績修正、狀態回復；GridFS 覆蓋上傳自動刪舊檔

---

## 📈 API 使用頻率分析

| API 分類 | 高頻使用 | 中頻使用 | 低頻使用 |
|----------|----------|----------|----------|
| **學生管理** | read | create, update | delete, status, upload_excel, feedback_excel |
| **考試管理** | read | create, update | delete, status, setweight |
| **成績管理** | create, read, update | calculation_final, test_score | delete, step_diagram |
| **檔案管理** | read | create | update, delete |

**建議優化重點**: 針對高頻 API 進行快取優化，中頻 API 加強錯誤處理，低頻 API 注重安全性驗證。

---

## 📅 變更紀錄

| 日期 | Use Case | 變更內容 |
|------|----------|----------|
| 2026-02-28 | UC-01 | upload_excel 欄位對應修正（Col A=名字, Col C=學號, Col D=email）；學期改由 POST 參數指定；重複學號防呆 |
| 2026-02-28 | UC-01 | 新增 student_email 欄位（DB migration 0003） |
| 2026-02-28 | UC-05 | feedback_excel 欄位更新（移除學期/狀態，加入四次成績/最後成績/是否被當）；被當紅色標記 |
| 2026-02-28 | UC-10 | 檔案存儲改為 MongoDB GridFS；MongoDB doc 加入 test_uuid/test_semester/test_name；read 向下相容舊路徑 |
| 2026-02-28 | UC-14 | step_diagram 產生的直方圖直接存入 GridFS（不再寫本地磁碟） |
