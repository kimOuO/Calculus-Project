# 状态自动更新功能说明

## 概述

系统现在支持在特定操作后自动更新考试状态，无需前端手动调用状态更新API。这确保了数据一致性并简化了前端逻辑。

## 状态流程

考试状态按以下顺序自动转换：

```
尚未出考卷 → 考卷完成 → 考卷成績結算
```

## 自动状态更新规则

### 1. 上传考卷时自动更新状态

**触发条件：**
- 上传文件类型为 `paper`（考卷）
- 当前状态为 `尚未出考卷`

**自动执行：**
- 状态更新为 `考卷完成`
- 更新 `test_updated_at` 时间戳

**实现位置：**
- 后端：`testfiledata_actor.py` 第 130-137 行
- 上传成功后在响应中返回更新后的状态

**代码逻辑：**
```python
# 如果上傳的是考卷（paper），且當前狀態是"尚未出考卷"，則自動更新為"考卷完成"
if asset_type == 'paper' and test.test_states == '尚未出考卷':
    update_data['test_states'] = '考卷完成'
    update_data['test_updated_at'] = timestamp
```

### 2. 设置权重时自动更新状态

**触发条件：**
- 调用设置权重API
- 当前状态为 `考卷完成`

**自动执行：**
- 状态更新为 `考卷成績結算`
- 更新 `test_updated_at` 时间戳

**实现位置：**
- 后端：`test_actor.py` 第 275-282 行
- 只在状态为"考卷完成"时才更新状态

**代码逻辑：**
```python
# 只有當狀態為"考卷完成"時，才自動更新為"考卷成績結算"
if test.test_states == '考卷完成':
    update_data['test_states'] = '考卷成績結算'
```

## 前端变更

### 1. 上传文件后的处理

前端不再需要手动调用状态更新API，只需：
1. 上传文件
2. 重新加载测试数据（获取后端更新的状态）
3. 更新UI显示

**代码位置：** `front/app/tests/[testUuid]/page.tsx`

```typescript
const handleUpload = async (assetType: AssetType, files: File[]) => {
  // Upload files (backend will auto-update status if needed)
  await upload({ test_uuid, asset_type, files });
  
  // Close modal
  setIsUploadModalOpen(false);
  
  // Reload test data to get updated status
  const updatedTest = await getTest(testUuid);
  setTest(updatedTest);
  
  // Load images...
};
```

### 2. 设置权重后的处理

测试列表页面已经在设置权重后调用 `refetch()` 重新加载数据：

**代码位置：** `front/app/tests/page.tsx`

```typescript
const handleSetWeights = async (weights: Record<string, string>) => {
  await setWeights({ test_semester: semester, weights });
  refetch(); // 重新加载数据，获取更新后的状态
};
```

## API响应变更

### 上传文件API响应

**端点：** `POST /api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create`

**新增字段：**
```json
{
  "file_uuid": "...",
  "asset_type": "paper",
  "file_count": 1,
  "mongodb_id": "...",
  "test_states": "考卷完成"  // 新增：返回更新后的状态
}
```

## 测试验证

运行测试脚本验证功能：

```bash
cd /home/mitlab/project/Calculus_oom
source venv/bin/activate
python3 test_status_update.py
```

**测试覆盖：**
1. ✅ 创建测试（状态：尚未出考卷）
2. ✅ 上传考卷 → 自动更新为"考卷完成"
3. ✅ 设置权重 → 自动更新为"考卷成績結算"

## 数据一致性保证

### 后端保证

1. **原子性更新**：使用 Django 的 `@transaction.atomic` 确保数据一致性
2. **条件检查**：只在满足特定条件时才更新状态
3. **日志记录**：所有状态更新都有详细日志

### 前端处理

1. **重新加载数据**：操作成功后立即重新加载测试数据
2. **UI同步更新**：确保显示的状态与数据库保持一致
3. **错误处理**：操作失败时不更新UI状态

## 业务规则

### 状态转换限制

1. **尚未出考卷 → 考卷完成**
   - 只能通过上传 `paper` 类型的文件触发
   - 上传其他类型文件（histogram等）不会改变状态

2. **考卷完成 → 考卷成績結算**
   - 只能通过设置权重触发
   - 必须当前状态为"考卷完成"

3. **手动状态更新**
   - 仍然支持通过状态更新API手动修改状态
   - API端点：`POST /api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/status`

## 兼容性

### 向后兼容

- 现有的手动状态更新API仍然可用
- 前端可以选择依赖自动更新或手动更新
- 不影响其他功能模块

### 未来扩展

如需添加新的状态转换规则：

1. 在后端相应的业务逻辑中添加条件判断
2. 更新前端重新加载数据的逻辑
3. 添加相应的测试用例
4. 更新本文档

## 相关文件

### 后端
- `main/apps/Calculus_metadata/actors/testfiledata_actor.py`
- `main/apps/Calculus_metadata/actors/test_actor.py`
- `test_status_update.py`（测试脚本）

### 前端
- `front/app/tests/[testUuid]/page.tsx`
- `front/app/tests/page.tsx`
- `front/types/file.ts`

## 更新日志

**日期：** 2026-01-01

**更改：**
1. ✅ 上传考卷时自动更新状态为"考卷完成"
2. ✅ 设置权重时自动更新状态为"考卷成績結算"（仅当前状态为"考卷完成"时）
3. ✅ 前端移除手动状态更新逻辑，依赖后端自动更新
4. ✅ 添加完整的测试验证脚本
5. ✅ 更新类型定义，添加 test_states 字段到上传响应
