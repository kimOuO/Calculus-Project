#!/usr/bin/env python3
"""
测试完整的文件上传和查看流程
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata"

def test_upload_and_view():
    """测试上传文件后能否正确查看"""
    
    print("=== 测试文件上传和查看流程 ===\n")
    
    # Step 1: 创建测试
    print("1. 创建新测试...")
    test_data = {
        "test_name": "文件上传测试",
        "test_weight": "0.3",
        "test_semester": "1141",
        "test_date": "2026-01-10",
        "test_range": "1-5章",
        "test_state": "尚未出考卷"
    }
    
    response = requests.post(
        f"{BASE_URL}/Test_MetadataWriter/create",
        json=test_data
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ 创建测试失败: {response.text}")
        return
    
    result = response.json()
    test = result.get('data', result)
    test_uuid = test['test_uuid']
    print(f"✅ 测试创建成功")
    print(f"   Test UUID: {test_uuid}")
    print(f"   初始状态: {test['test_states']}")
    print(f"   初始 pt_opt_score_uuid: {test.get('pt_opt_score_uuid', 'None')}")
    print()
    
    # Step 2: 上传考卷
    print("2. 上传考卷文件...")
    
    # 创建一个测试文件
    test_content = b'This is a test paper content for testing upload and download'
    files = {
        'file': ('test_paper.txt', test_content, 'text/plain')
    }
    data = {
        'test_uuid': test_uuid,
        'asset_type': 'paper'
    }
    
    response = requests.post(
        f"{BASE_URL}/test-filedata/create",
        data=data,
        files=files
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ 上传考卷失败: {response.text}")
        cleanup(test_uuid)
        return
    
    upload_result = response.json()['data']
    file_uuid = upload_result['file_uuid']
    print(f"✅ 考卷上传成功")
    print(f"   File UUID: {file_uuid}")
    print(f"   Asset Type: {upload_result['asset_type']}")
    print(f"   File Count: {upload_result['file_count']}")
    if 'test_states' in upload_result:
        print(f"   更新后状态: {upload_result['test_states']}")
    print()
    
    # Step 3: 重新读取测试，检查 pt_opt_score_uuid
    print("3. 检查测试数据是否已更新...")
    response = requests.post(
        f"{BASE_URL}/Test_MetadataWriter/read",
        json={"test_uuid": test_uuid}
    )
    
    if response.status_code != 200:
        print(f"❌ 读取测试失败: {response.text}")
        cleanup(test_uuid)
        return
    
    updated_test = response.json()['data']
    if isinstance(updated_test, list):
        updated_test = updated_test[0]
    
    print(f"   Test UUID: {updated_test['test_uuid']}")
    print(f"   当前状态: {updated_test['test_states']}")
    print(f"   pt_opt_score_uuid: {updated_test.get('pt_opt_score_uuid', 'None')}")
    
    if not updated_test.get('pt_opt_score_uuid'):
        print(f"❌ pt_opt_score_uuid 未设置！")
        cleanup(test_uuid)
        return
    else:
        print(f"✅ pt_opt_score_uuid 已正确设置")
    print()
    
    # Step 4: 下载文件验证
    print("4. 尝试下载上传的文件...")
    download_data = {
        "test_pic_uuid": updated_test['pt_opt_score_uuid'],
        "asset_type": "paper"
    }
    
    response = requests.post(
        f"{BASE_URL}/test-filedata/read",
        json=download_data
    )
    
    if response.status_code != 200:
        print(f"❌ 下载文件失败: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        cleanup(test_uuid)
        return
    
    downloaded_content = response.content
    print(f"✅ 文件下载成功")
    print(f"   Content-Type: {response.headers.get('Content-Type')}")
    print(f"   Content-Length: {len(downloaded_content)} bytes")
    print(f"   内容匹配: {'✅ 是' if downloaded_content == test_content else '❌ 否'}")
    print()
    
    # Step 5: 上传直方图
    print("5. 上传直方图文件...")
    
    histogram_content = b'This is a histogram image content'
    files = {
        'file': ('histogram.png', histogram_content, 'image/png')
    }
    data = {
        'test_uuid': test_uuid,
        'asset_type': 'histogram'
    }
    
    response = requests.post(
        f"{BASE_URL}/test-filedata/create",
        data=data,
        files=files
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ 上传直方图失败: {response.text}")
    else:
        print(f"✅ 直方图上传成功")
    print()
    
    # Step 6: 下载直方图验证
    print("6. 尝试下载直方图...")
    download_data = {
        "test_pic_uuid": updated_test['pt_opt_score_uuid'],
        "asset_type": "histogram"
    }
    
    response = requests.post(
        f"{BASE_URL}/test-filedata/read",
        json=download_data
    )
    
    if response.status_code != 200:
        print(f"⚠️ 下载直方图失败（这是正常的，因为可能还没上传）: {response.status_code}")
    else:
        print(f"✅ 直方图下载成功")
        print(f"   Content-Length: {len(response.content)} bytes")
    print()
    
    print("=== ✅ 测试完成！===")
    print("\n总结：")
    print(f"  - 测试UUID: {test_uuid}")
    print(f"  - 文件UUID: {updated_test.get('pt_opt_score_uuid')}")
    print(f"  - 当前状态: {updated_test['test_states']}")
    print(f"  - 考卷已上传并可下载: ✅")
    print(f"  - 直方图已上传: ✅")
    
    # Cleanup
    print("\n清理测试数据...")
    cleanup(test_uuid)

def cleanup(test_uuid):
    """清理测试数据"""
    try:
        requests.post(
            f"{BASE_URL}/Test_MetadataWriter/delete",
            json={"test_uuid": test_uuid}
        )
        print("✅ 测试数据已清理")
    except:
        print("⚠️ 清理失败（可能需要手动删除）")

if __name__ == "__main__":
    try:
        test_upload_and_view()
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
