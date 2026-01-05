#!/usr/bin/env python3
"""
测试状态自动更新功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v0.1/Calculus_oom/Calculus_metadata"

def test_status_workflow():
    """测试完整的状态转换流程"""
    
    print("=== 测试状态自动更新流程 ===\n")
    
    # Step 1: 创建测试
    print("1. 创建新测试...")
    test_data = {
        "test_name": "状态测试考试",
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
    
    # Step 2: 检查初始状态
    if test['test_states'] != '尚未出考卷':
        print(f"❌ 初始状态错误，应为 '尚未出考卷'，实际为 '{test['test_states']}'")
        return
    
    print()
    
    # Step 3: 上传考卷（应该自动更新状态为 "考卷完成"）
    print("2. 上传考卷（paper）...")
    
    # 创建一个测试文件
    files = {
        'file': ('test_paper.txt', b'This is a test paper', 'text/plain')
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
        return
    
    upload_result = response.json()['data']
    print(f"✅ 考卷上传成功")
    print(f"   File UUID: {upload_result['file_uuid']}")
    if 'test_states' in upload_result:
        print(f"   更新后状态: {upload_result['test_states']}")
    
    print()
    
    # Step 4: 重新读取测试，检查状态是否已更新
    print("3. 检查状态是否已自动更新...")
    response = requests.post(
        f"{BASE_URL}/Test_MetadataWriter/read",
        json={"test_uuid": test_uuid}
    )
    
    if response.status_code != 200:
        print(f"❌ 读取测试失败: {response.text}")
        return
    
    updated_test = response.json()['data']
    if isinstance(updated_test, list):
        updated_test = updated_test[0]
    
    print(f"   当前状态: {updated_test['test_states']}")
    
    if updated_test['test_states'] != '考卷完成':
        print(f"❌ 状态未自动更新，应为 '考卷完成'，实际为 '{updated_test['test_states']}'")
        return
    else:
        print(f"✅ 状态已自动更新为 '考卷完成'")
    
    print()
    
    # Step 5: 设置权重（应该自动更新状态为 "考卷成績結算"）
    print("4. 设置权重...")
    weights_data = {
        "test_semester": "1141",
        "weights": {
            "状态测试考试": "1.0"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/Test_MetadataWriter/setweight",
        json=weights_data
    )
    
    if response.status_code != 200:
        print(f"❌ 设置权重失败: {response.text}")
        return
    
    print(f"✅ 权重设置成功")
    print()
    
    # Step 6: 再次读取测试，检查状态是否已更新
    print("5. 检查状态是否已自动更新...")
    response = requests.post(
        f"{BASE_URL}/Test_MetadataWriter/read",
        json={"test_uuid": test_uuid}
    )
    
    if response.status_code != 200:
        print(f"❌ 读取测试失败: {response.text}")
        return
    
    final_test = response.json()['data']
    if isinstance(final_test, list):
        final_test = final_test[0]
    
    print(f"   当前状态: {final_test['test_states']}")
    print(f"   权重: {final_test['test_weight']}")
    
    if final_test['test_states'] != '考卷成績結算':
        print(f"❌ 状态未自动更新，应为 '考卷成績結算'，实际为 '{final_test['test_states']}'")
        return
    else:
        print(f"✅ 状态已自动更新为 '考卷成績結算'")
    
    print()
    print("=== ✅ 所有测试通过！状态自动更新功能正常工作 ===")
    
    # Cleanup
    print("\n清理测试数据...")
    requests.post(
        f"{BASE_URL}/Test_MetadataWriter/delete",
        json={"test_uuid": test_uuid}
    )
    print("✅ 测试数据已清理")

if __name__ == "__main__":
    try:
        test_status_workflow()
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
