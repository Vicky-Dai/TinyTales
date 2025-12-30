# Postman 测试指南

## 设置 Postman 请求

### 1. 测试健康检查
- **Method:** GET
- **URL:** `http://localhost:8000/health`

### 2. 生成故事
- **Method:** POST
- **URL:** `http://localhost:8000/api/story/generate`
- **Headers:**
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "age_range": "4-7",
  "language": "en",
  "moral": "sharing is caring",
  "characters": ["Lily", "a friendly dragon"],
  "setting": "a small village near a forest",
  "tone": "warm",
  "pages": 5
}
```

### 3. 获取故事
- **Method:** GET
- **URL:** `http://localhost:8000/api/story/{storyId}`
- 将 `{storyId}` 替换为生成故事时返回的 storyId


