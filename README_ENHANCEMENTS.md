# JSON Fields DB 增强功能说明

## 新增功能

### 1. 文件属性管理
每个JSON模板文件现在支持以下属性：
- **project**: 使用项目名称
- **is_deprecated**: 是否废弃（0=使用中，1=已废弃）
- **description**: 描述信息

### 2. 智能数据导入
- 使用相对路径存储文件路径，避免不同路径导致同一文件重复
- 导入数据时保留已有文件的属性设置
- 仅更新template字段，不覆盖用户自定义的属性

### 3. 默认目录
- 默认读取当前脚本所在目录下的 `home` 目录
- 可通过命令行参数指定其他目录：`python json_fields_db.py /path/to/directory`

### 4. Web界面增强

#### 4.1 搜索页面 (/)
- 在搜索框输入字段名称进行搜索
- 搜索结果表格显示文件的所有属性（Project、Status、Description）
- 每条记录都有"Edit"按钮，可直接编辑属性
- 点击右上角"View All Templates"按钮查看所有模板

#### 4.2 模板列表页面 (/templates) ⭐ 新增
- **显示所有模板文件**：完整展示所有JSON模板及其属性
- **字段统计**：显示每个模板包含的字段数量
- **单个编辑**：点击每行的"Edit"按钮编辑单个模板属性
- **批量选择**：
  - 使用复选框选择多个模板
  - "Select All" / "Deselect All" 快速全选/取消全选
  - 表头复选框可一键全选/取消
- **批量编辑** ⭐：
  - 选择多个模板后点击"Batch Edit Selected"按钮
  - 弹出批量编辑对话框
  - 支持选择性更新字段（留空则保持原值）
  - 一次更新所有选中的模板
  - 显示更新成功数量

### 5. 批量编辑功能详解

#### 使用场景
- 将多个模板标记为同一项目
- 批量废弃一组不再使用的模板
- 为多个模板添加相同的描述信息
- 混合更新：某些字段统一设置，某些字段保持原值

#### 操作步骤
1. 访问 `/templates` 页面
2. 勾选需要编辑的模板（可使用全选功能）
3. 点击"Batch Edit Selected (n)"按钮
4. 在弹出框中设置要更新的属性：
   - **Project**：留空则不修改原有项目
   - **Status**：选择"Keep original"保持原状态
   - **Description**：留空则不修改原有描述
5. 点击"Save All"保存
6. 系统提示成功更新的模板数量

## 使用方法

### 启动服务
```bash
# 使用默认home目录
python json_fields_db.py

# 使用指定目录
python json_fields_db.py /path/to/home
```

### 搜索字段
1. 访问 http://localhost:5000
2. 在搜索框输入字段名称
3. 点击Search按钮
4. 查看搜索结果表格
5. 可点击右上角"View All Templates"查看所有模板

### 编辑单个属性
1. 在搜索结果或模板列表中点击"Edit"按钮
2. 在弹出框中修改：
   - Project: 输入项目名称
   - Status: 选择Active或Deprecated
   - Description: 输入描述信息
3. 点击Save保存
4. 页面自动刷新显示最新数据

### 批量编辑属性 ⭐
1. 访问 http://localhost:5000/templates
2. 勾选需要编辑的模板（支持全选）
3. 点击"Batch Edit Selected (n)"按钮
4. 在弹出框中设置属性（留空表示不修改）：
   - Project: 统一设置为某项目（可选）
   - Status: 统一设置状态（可选）
   - Description: 统一添加描述（可选）
5. 点击"Save All"批量保存
6. 页面刷新显示更新结果


## 数据库结构

### json_files表
```sql
CREATE TABLE json_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE,
    tpl_name TEXT,
    project TEXT DEFAULT '',
    is_deprecated INTEGER DEFAULT 0,
    description TEXT DEFAULT ''
)
```

### template_fields表
```sql
CREATE TABLE template_fields (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER,
    field_name TEXT,
    FOREIGN KEY (file_id) REFERENCES json_files(id)
)
```

## 技术改进

1. **路径处理**: 使用`os.path.relpath()`计算相对路径
2. **数据保留**: 导入时检查文件是否存在，保留用户设置的属性
3. **Web API**: 
   - 新增`/update_attributes`端点处理单个属性更新
   - 新增`/batch_update_attributes`端点处理批量属性更新
   - 新增`/templates`路由显示所有模板列表
4. **前端交互**: 
   - 使用模态框和Fetch API实现无刷新编辑
   - 支持复选框批量选择
   - 智能批量更新（留空字段保持原值）
5. **数据库查询优化**: 使用LEFT JOIN和GROUP BY统计字段数量
