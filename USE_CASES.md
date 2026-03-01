# Calculus OOM Backend - Use Case Scenarios

## 📚 學生管理場景

### Scenario 1: 新學期學生註冊
```
Given: 新學期開始，需要建立學生名單
When: 管理員上傳學生名單 Excel 或逐一建立學生資料
Then: 系統自動產生學生 UUID，狀態設為「修業中」，並記錄 student_email
```

**Excel 匯入格式（upload_excel）**:
| 欄位 | Excel 欄 | 說明 |
|------|----------|------|
| 名字 | Col A | student_name |
| 姓氏 | Col B | 略過 |
| 學號 | Col C | student_number（唯一鍵） |
| 電子郵件 | Col D | student_email |
| 科系 | Col E | 略過 |
| 分組 | Col F | 略過 |

- 學期 (`student_semester`) 由 POST 參數指定，不從 Excel 讀取
- 重複學號自動跳過並回報錯誤

### Scenario 2: 學生狀態變更
```
Given: 學期中學生狀態變化
When: 管理員更新學生狀態為「二退」、「被當」或「修業完畢」
Then: 系統更新狀態，若為「二退」則清空該學生所有成績
```

### Scenario 3: 學生資料查詢與匯出
```
Given: 需要查看特定學期學生資料與成績
When: 管理員查詢學生列表或匯出 Excel 報表
Then: 系統提供完整學生資料與成績報表
```

**Excel 匯出格式（feedback_excel）**:
| 欄位 | 說明 |
|------|------|
| 學生名字 | student_name |
| 學號 | student_number |
| 第一次小考 | score_quiz1 |
| 期中考 | score_midterm |
| 第二次小考 | score_quiz2 |
| 期末考 | score_finalexam |
| 最後成績 | score_total |
| 是否被當 | 通過 / 被當（被當整行紅底 + 紅字） |

## 📝 考試管理場景

### Scenario 4: 考試規劃與建立
```
Given: 學期開始，需要規劃考試安排
When: 管理員建立考試項目（期中、期末、小考等）
Then: 系統產生考試 UUID，狀態為「尚未出考卷」
```

### Scenario 5: 考試權重設定
```
Given: 考試項目已建立
When: 管理員設定各考試權重（總和必須為 1.0）
      例: 期中考 0.4，期末考 0.6
Then: 系統儲存權重設定，用於總成績計算
```

### Scenario 6: 考卷上傳與管理
```
Given: 考試已出題完成
When: 管理員上傳考卷圖片或 PDF 檔案
Then: 系統將二進位檔案儲存至 MongoDB GridFS，
      MongoDB doc 記錄 test_pic_gridfs_id，
      考試狀態自動更新為「考卷完成」
```

## 📊 成績管理場景

### Scenario 7: 成績錄入與更新
```
Given: 考試批改完成，需要錄入成績
When: 管理員輸入各學生的考試成績
Then: 系統建立或更新成績記錄，關聯至學生 UUID
```

### Scenario 8: 總成績計算
```
Given: 所有考試成績已錄入，權重已設定
When: 管理員執行總成績計算
Then: 系統依權重計算每位學生總分，
      總分 < passing_score 者狀態更新為「被當」
```

### Scenario 9: 成績統計分析
```
Given: 某考試成績已完整錄入
When: 管理員查詢考試統計資料
Then: 系統計算平均分、中位數等統計指標
```

### Scenario 10: 成績分布視覺化
```
Given: 成績資料完整
When: 管理員產生成績分布圖
Then: 系統生成直方圖，二進位存入 MongoDB GridFS，
      MongoDB doc 記錄 test_pic_histogram_gridfs_id
```

## 📁 檔案管理場景

### Scenario 11: 考卷/直方圖檔案上傳
```
Given: 考試題目已準備完成
When: 管理員上傳考卷圖片/PDF（asset_type: paper / histogram）
Then: 系統將檔案二進位存至 MongoDB GridFS，
      新增或更新 test_pic_information 集合中的文件，
      文件包含 test_uuid / test_semester / test_name 供跨 DB 驗證
```

### Scenario 12: 考卷/直方圖查看
```
Given: 考卷已上傳完成
When: 前端呼叫 read API 取得檔案
Then: 系統優先從 GridFS 讀取（依 gridfs_id）；
      若 gridfs_id 為空則 fallback 至舊本地磁碟路徑（向下相容）
```

### Scenario 13: 檔案更新與刪除
```
Given: 考卷需要修正或移除
When: 管理員更新或刪除考卷檔案
Then: 系統刪除 GridFS 舊檔案，上傳新版本或清空 gridfs_id 欄位
```

## 🔄 完整工作流程場景

### Scenario 14: 學期完整流程
```
Given: 新學期開始
When:
  1. 批量上傳學生名單 Excel（需帶入 student_semester）
  2. 規劃考試項目與權重
  3. 上傳考卷（存 GridFS，狀態自動轉「考卷完成」）
  4. 錄入各考試成績
  5. 計算總成績（被當者自動標記）
  6. 產生統計圖表（存 GridFS，狀態自動轉「考卷成績結算」）
  7. 匯出 Excel 成績報表（被當者紅色標記）
Then: 完整的學期成績管理與分析
```

### Scenario 15: 異常處理流程
```
Given: 系統運作中發生異常狀況
When:
  - 學生中途退學 → 狀態改為「二退」，成績清空
  - 考卷需要重新上傳 → 舊 GridFS 檔案自動刪除，上傳新版本
  - 成績錄入錯誤 → 成績修正更新
  - 重複學號匯入 → 自動跳過，回報 errors 列表
Then: 系統保持資料一致性，不影響其他學生
```

## 📋 API 支援的核心操作

| 場景類型 | 支援操作 | API 端點數量 |
|---------|---------|-------------|
| 學生管理 | CRUD + 狀態管理 + Excel 匯入匯出 | 7 個 |
| 考試管理 | CRUD + 權重設定 + 狀態管理 | 6 個 |
| 成績管理 | CRUD + 計算 + 統計 + 視覺化 | 6 個 |
| 檔案管理 | GridFS CRUD + 多格式支援 | 4 個 |

**總計：23 個 API 端點**，支援完整的微積分課程成績管理流程。

## 📅 版本記錄

| 日期 | 變更摘要 |
|------|----------|
| 2026-02-28 | GridFS 重構（檔案改存 MongoDB）、student_email 欄位、Excel 匯入格式修正、匯出紅色標記 |
