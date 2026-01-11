# test_delete_final.py
import requests
import json

def test_delete_user_complete():
    url = "http://127.0.0.1:8000/api/admin/delete_user"
    
    # 要删除的用户ID
    user_id = 3
    
    # 准备表单数据
    data = {
        "user_id": str(user_id)
    }
    
    print("=" * 60)
    print("完整测试删除用户流程")
    print("=" * 60)
    
    print(f"\n测试删除用户 ID: {user_id}")
    print(f"URL: {url}")
    print(f"数据: {data}")
    
    try:
        response = requests.post(url, data=data)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 删除成功!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            error = response.json()
            print(f"\n❌ 删除失败: {error.get('detail')}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_delete_user_complete()