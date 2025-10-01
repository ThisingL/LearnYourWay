#!/bin/bash
# 学习素材生成功能 API 测试脚本

BASE_URL="http://localhost:8000"

echo "=========================================="
echo "学习素材生成 API 测试"
echo "=========================================="

# 测试内容
TEST_CONTENT="光合作用是植物利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。这个过程主要在叶绿体中进行。叶绿体中的叶绿素能够吸收光能，通过一系列复杂的化学反应，将二氧化碳和水转化为葡萄糖，同时释放氧气。光合作用对地球上的生命至关重要，它不仅为植物提供能量，也为其他生物提供氧气和食物来源。"

# 1. 创建用户画像
echo -e "\n1️⃣ 创建用户画像..."
curl -s -X POST "$BASE_URL/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_material_user",
    "grade": 5,
    "interests": ["足球", "科学实验", "恐龙"]
  }' | jq .

# 2. 生成测验题
echo -e "\n=========================================="
echo "2️⃣ 生成测验题..."
echo "=========================================="
QUIZ_RESPONSE=$(curl -s -X POST "$BASE_URL/materials/quiz" \
  -H "Content-Type: application/json" \
  -d "{
    \"chunk_id\": \"test_chunk_001\",
    \"profile_id\": \"test_material_user\",
    \"content\": \"$TEST_CONTENT\",
    \"count\": 8
  }")

echo "$QUIZ_RESPONSE" | jq .

# 显示题目详情
echo -e "\n📝 测验题详情："
echo "$QUIZ_RESPONSE" | jq -r '.data.questions[] | "题目 \(.id): \(.stem) (类型: \(.type), 难度: \(.difficulty))"'

# 3. 生成思维导图
echo -e "\n=========================================="
echo "3️⃣ 生成思维导图..."
echo "=========================================="
MINDMAP_RESPONSE=$(curl -s -X POST "$BASE_URL/materials/mindmap" \
  -H "Content-Type: application/json" \
  -d "{
    \"chunk_id\": \"test_chunk_001\",
    \"profile_id\": \"test_material_user\",
    \"content\": \"$TEST_CONTENT\"
  }")

echo "$MINDMAP_RESPONSE" | jq .

# 显示节点和边统计
echo -e "\n🌐 思维导图统计："
NODE_COUNT=$(echo "$MINDMAP_RESPONSE" | jq '.data.nodes | length')
EDGE_COUNT=$(echo "$MINDMAP_RESPONSE" | jq '.data.edges | length')
echo "  - 节点数: $NODE_COUNT"
echo "  - 连接数: $EDGE_COUNT"

echo -e "\n节点列表："
echo "$MINDMAP_RESPONSE" | jq -r '.data.nodes[] | "  [\(.type)] \(.label)"'

# 4. 生成沉浸式文本
echo -e "\n=========================================="
echo "4️⃣ 生成沉浸式文本..."
echo "=========================================="
IMMERSIVE_RESPONSE=$(curl -s -X POST "$BASE_URL/materials/immersive" \
  -H "Content-Type: application/json" \
  -d "{
    \"chunk_id\": \"test_chunk_001\",
    \"profile_id\": \"test_material_user\",
    \"content\": \"$TEST_CONTENT\"
  }")

echo "$IMMERSIVE_RESPONSE" | jq .

# 显示章节统计
echo -e "\n📖 沉浸式文本章节："
SECTION_COUNT=$(echo "$IMMERSIVE_RESPONSE" | jq '.data.sections | length')
echo "  - 章节数: $SECTION_COUNT"

echo -e "\n章节标题："
echo "$IMMERSIVE_RESPONSE" | jq -r '.data.sections[] | "  📌 \(.title)"'

# 5. 测试不同年级
echo -e "\n=========================================="
echo "5️⃣ 测试不同年级的素材生成差异"
echo "=========================================="

# 创建2年级学生画像
echo -e "\n创建2年级学生画像..."
curl -s -X POST "$BASE_URL/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "kid_grade2",
    "grade": 2,
    "interests": ["小猫", "画画", "玩具"]
  }' | jq .

# 为2年级生成测验
echo -e "\n为2年级生成测验..."
curl -s -X POST "$BASE_URL/materials/quiz" \
  -H "Content-Type: application/json" \
  -d "{
    \"chunk_id\": \"test_chunk_002\",
    \"profile_id\": \"kid_grade2\",
    \"content\": \"$TEST_CONTENT\",
    \"count\": 5
  }" | jq -r '.data.questions[] | "\n题目: \(.stem)\n答案: \(.answer)\n"'

# 创建8年级学生画像
echo -e "\n创建8年级学生画像..."
curl -s -X POST "$BASE_URL/profiles" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "teen_grade8",
    "grade": 8,
    "interests": ["编程", "化学实验", "天文"]
  }' | jq .

# 为8年级生成测验
echo -e "\n为8年级生成测验..."
curl -s -X POST "$BASE_URL/materials/quiz" \
  -H "Content-Type: application/json" \
  -d "{
    \"chunk_id\": \"test_chunk_003\",
    \"profile_id\": \"teen_grade8\",
    \"content\": \"$TEST_CONTENT\",
    \"count\": 5
  }" | jq -r '.data.questions[] | "\n题目: \(.stem)\n答案: \(.answer)\n"'

# 6. 测试错误处理
echo -e "\n=========================================="
echo "6️⃣ 测试错误处理"
echo "=========================================="

# 测试不存在的用户画像
echo -e "\n测试不存在的用户画像..."
curl -s -X POST "$BASE_URL/materials/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_id": "test_chunk_999",
    "profile_id": "non_existent_user",
    "content": "测试内容",
    "count": 5
  }' | jq .

# 测试无效的题目数量
echo -e "\n测试无效的题目数量（超出范围）..."
curl -s -X POST "$BASE_URL/materials/quiz" \
  -H "Content-Type: application/json" \
  -d "{
    \"chunk_id\": \"test_chunk_004\",
    \"profile_id\": \"test_material_user\",
    \"content\": \"$TEST_CONTENT\",
    \"count\": 100
  }" | jq .

echo -e "\n=========================================="
echo "✅ 测试完成！"
echo "=========================================="

echo -e "\n💡 提示："
echo "  - 访问 http://localhost:8000/docs 查看完整 API 文档"
echo "  - 所有素材都已根据用户兴趣（足球、科学实验、恐龙）进行了个性化"
echo "  - 不同年级的素材难度和表达方式会有明显差异"

