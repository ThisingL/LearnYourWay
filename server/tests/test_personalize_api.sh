#!/bin/bash
# 个性化功能 API 测试脚本

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "个性化功能 API 测试"
echo "=========================================="

# 1. 创建用户画像
echo -e "\n1️⃣ 创建用户画像..."
PROFILE_RESPONSE=$(curl -s -X POST "$BASE_URL/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_01",
    "grade": 5,
    "interests": ["足球", "科学实验", "恐龙"]
  }')

echo "$PROFILE_RESPONSE" | jq .

# 2. 查询用户画像
echo -e "\n2️⃣ 查询用户画像..."
curl -s "$BASE_URL/profiles/test_user_01" | jq .

# 3. 创建个性化任务
echo -e "\n3️⃣ 创建个性化改写任务..."
PERSONALIZE_RESPONSE=$(curl -s -X POST "$BASE_URL/personalize" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_id": "chunk_001",
    "profile_id": "test_user_01",
    "original_text": "光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。在叶绿体中，叶绿素吸收光能，通过一系列复杂的化学反应，最终产生葡萄糖，同时释放氧气到大气中。这个过程对地球上的生命至关重要，因为它不仅为植物提供能量，也为其他生物提供氧气和食物来源。",
    "must_keep_terms": ["光合作用", "二氧化碳", "叶绿素", "叶绿体"]
  }')

echo "$PERSONALIZE_RESPONSE" | jq .

# 提取任务ID
TASK_ID=$(echo "$PERSONALIZE_RESPONSE" | jq -r '.data.task_id')

if [ "$TASK_ID" != "null" ]; then
  # 4. 轮询任务状态
  echo -e "\n4️⃣ 查询任务状态（任务ID: $TASK_ID）..."
  
  for i in {1..5}; do
    echo -e "\n  📊 第 $i 次查询..."
    TASK_STATUS=$(curl -s "$BASE_URL/personalize/tasks/$TASK_ID" | jq .)
    echo "$TASK_STATUS"
    
    STATUS=$(echo "$TASK_STATUS" | jq -r '.data.status')
    if [ "$STATUS" == "success" ]; then
      echo -e "\n  ✅ 任务完成！"
      echo "$TASK_STATUS" | jq '.data.result'
      break
    elif [ "$STATUS" == "failure" ]; then
      echo -e "\n  ❌ 任务失败！"
      echo "$TASK_STATUS" | jq '.data.error'
      break
    fi
    
    sleep 2
  done
fi

# 5. 测试不同年级和兴趣组合
echo -e "\n=========================================="
echo "5️⃣ 测试不同年级和兴趣组合"
echo "=========================================="

# 创建小学2年级学生画像
echo -e "\n📝 创建2年级学生画像..."
curl -s -X POST "$BASE_URL/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_grade_2",
    "grade": 2,
    "interests": ["小动物", "画画", "唱歌"]
  }' | jq .

# 创建中学8年级学生画像
echo -e "\n📝 创建8年级学生画像..."
curl -s -X POST "$BASE_URL/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "student_grade_8",
    "grade": 8,
    "interests": ["编程", "机器人", "物理实验"]
  }' | jq .

# 6. 测试边界情况
echo -e "\n=========================================="
echo "6️⃣ 测试边界情况"
echo "=========================================="

# 测试不存在的用户画像
echo -e "\n❌ 查询不存在的用户画像..."
curl -s "$BASE_URL/profiles/non_existent_user" | jq .

# 测试使用不存在的画像创建任务
echo -e "\n❌ 使用不存在的画像创建任务..."
curl -s -X POST "$BASE_URL/personalize" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_id": "chunk_002",
    "profile_id": "non_existent_user",
    "original_text": "测试文本"
  }' | jq .

echo -e "\n=========================================="
echo "✅ 测试完成！"
echo "=========================================="

