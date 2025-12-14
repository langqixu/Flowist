# 依赖检查报告

生成时间: 2025-12-14 18:26

---

## 📊 总体情况

✅ **未发现依赖版本冲突**

- 总安装包数: **153 个**
- Requirements.txt 定义: **15 个直接依赖**
- 所有包兼容性检查: **通过**

---

## 1️⃣ 重复包检查结果

✅ **未发现同一个包安装了多个版本**

在 Python 的 site-packages 中，pip 会确保每个包只安装一个版本。如果尝试安装不同版本，旧版本会被自动覆盖。

---

## 2️⃣ Requirements.txt 依赖状态

所有 requirements.txt 中定义的包均已正确安装：

| 包名 | 要求版本 | 已安装版本 | 状态 |
|------|---------|-----------|------|
| fastapi | >=0.104.0 | 0.124.4 | ✅ |
| uvicorn | >=0.24.0 | 0.38.0 | ✅ |
| pydantic | >=2.0 | 2.12.5 | ✅ |
| pydantic-settings | >=2.0 | 2.11.0 | ✅ |
| openai | >=1.0.0 | 2.11.0 | ✅ |
| langchain | >=0.1.0 | 0.3.27 | ✅ |
| langchain-openai | >=0.0.2 | 0.3.35 | ✅ |
| langchain-community | >=0.0.10 | 0.3.31 | ✅ |
| chromadb | >=0.4.0 | 1.3.7 | ✅ |
| python-dotenv | >=1.0.0 | 1.2.1 | ✅ |
| httpx | >=0.25.0 | 0.28.1 | ✅ |
| streamlit | >=1.28.0 | 1.50.0 | ✅ |
| requests | >=2.31.0 | 2.32.5 | ✅ |
| pytest | >=7.4.0 | 8.4.2 | ✅ |
| pytest-asyncio | >=0.21.0 | 1.2.0 | ✅ |

---

## 3️⃣ 依赖树分析

使用 `pipdeptree --warn fail` 检查全部依赖树，**未发现版本冲突**。

### 常见的依赖共享情况

以下包被多个上层依赖共同使用，但版本兼容：

#### `typing_extensions==4.15.0`
被以下包依赖：
- pydantic (>=4.14.1)
- langchain-core (>=4.7.0)
- openai (>=4.11)
- streamlit (>=4.4.0)
- altair (>=4.10.0)
- 等多个包...

**结论**: 所有依赖的版本要求都被 `4.15.0` 满足 ✅

#### `anyio==4.12.0`
被以下包依赖：
- openai (>=3.5.0)
- httpx (任意版本)
- langchain-core (>=3.0.0)
- watchfiles (>=3.0.0)

**结论**: 所有依赖的版本要求都被 `4.12.0` 满足 ✅

#### `requests==2.32.5`
被以下包依赖：
- streamlit (>=2.27)
- langsmith (>=2.4.0)
- tiktoken (>=2.26.0)

**结论**: 所有依赖的版本要求都被 `2.32.5` 满足 ✅

#### `pydantic==2.12.5`
被以下包依赖：
- fastapi (>=1.7.0)
- pydantic-settings (>=2.0.0)
- langchain-core (>=2.7.4)
- openai (>=1.9.0)

**结论**: 所有依赖的版本要求都被 `2.12.5` 满足 ✅

---

## 4️⃣ pip check 结果

```
✅ No broken requirements found.
```

所有已安装的包及其依赖关系均兼容，无版本冲突。

---

## 🔍 潜在关注点

### 1. pip 版本较旧
```
WARNING: You are using pip version 21.2.4; however, version 25.3 is available.
```

**建议**: 
```bash
python3 -m pip install --upgrade pip
```

### 2. 包版本远超 requirements.txt 最低要求

许多包的实际安装版本远高于 requirements.txt 中的最低要求，这通常是好事，但如果需要严格的版本控制，建议：

**方案 1**: 锁定确切版本（推荐用于生产环境）
```bash
python3 -m pip freeze > requirements-lock.txt
```

**方案 2**: 使用 Poetry 或 Pipenv 进行更精细的依赖管理

---

## ✅ 结论

**您的本地环境依赖健康，未发现版本冲突或重复安装的问题。**

所有包的版本兼容性良好，可以放心使用当前环境进行开发。

---

## 📝 相关脚本

- `check_dependencies.py` - 自动化依赖检查脚本
- 可重复运行以监控依赖健康状况

运行方式：
```bash
python3 check_dependencies.py
```
