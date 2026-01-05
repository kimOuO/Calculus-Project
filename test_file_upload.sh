#!/bin/bash

# 測試考卷上傳功能

echo "=== 測試考卷上傳功能 ==="

# 1. 獲取第一個考試
echo -e "\n1. 獲取考試列表..."
TEST_UUID=$(curl -s -X POST http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/read \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -c "import json,sys; data=json.load(sys.stdin); print(data['data'][0]['test_uuid'])")

echo "選擇考試 UUID: $TEST_UUID"

# 2. 創建測試圖片
echo -e "\n2. 創建測試圖片..."
convert -size 800x600 xc:white -pointsize 40 -fill black \
  -annotate +100+300 "Test Paper" \
  /tmp/test_paper.jpg

convert -size 800x600 xc:white -pointsize 40 -fill black \
  -annotate +100+300 "Histogram" \
  /tmp/test_histogram.jpg

echo "測試圖片已創建"

# 3. 上傳考卷
echo -e "\n3. 上傳考卷..."
UPLOAD_RESULT=$(curl -s -X POST http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create \
  -F "test_uuid=$TEST_UUID" \
  -F "asset_type=paper" \
  -F "file=@/tmp/test_paper.jpg")

echo "上傳結果: $UPLOAD_RESULT"

FILE_UUID=$(echo $UPLOAD_RESULT | python3 -c "import json,sys; data=json.load(sys.stdin); print(data.get('data',{}).get('file_uuid',''))")
echo "FILE UUID: $FILE_UUID"

# 4. 上傳直方圖
echo -e "\n4. 上傳直方圖..."
curl -s -X POST http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/create \
  -F "test_uuid=$TEST_UUID" \
  -F "asset_type=histogram" \
  -F "file=@/tmp/test_histogram.jpg"

# 5. 檢查考試記錄是否更新
echo -e "\n5. 檢查考試記錄..."
curl -s -X POST http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/Test_MetadataWriter/read \
  -H "Content-Type: application/json" \
  -d "{\"test_uuid\":\"$TEST_UUID\"}" | python3 -m json.tool

# 6. 讀取文件
if [ ! -z "$FILE_UUID" ]; then
  echo -e "\n6. 讀取考卷..."
  curl -s -X POST http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata/test-filedata/read \
    -H "Content-Type: application/json" \
    -d "{\"test_pic_uuid\":\"$FILE_UUID\",\"asset_type\":\"paper\"}" \
    -o /tmp/downloaded_paper.jpg
  
  if [ -f /tmp/downloaded_paper.jpg ]; then
    echo "考卷已下載到 /tmp/downloaded_paper.jpg"
    ls -lh /tmp/downloaded_paper.jpg
  else
    echo "下載失敗"
  fi
fi

echo -e "\n=== 測試完成 ==="
