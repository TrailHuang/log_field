#!/usr/bin/env python3
import os
import json
import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)

def create_database():
    """Create SQLite database and tables"""
    conn = sqlite3.connect('json_fields.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS json_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_path TEXT UNIQUE,
        tpl_name TEXT,
        project TEXT DEFAULT '',
        is_deprecated INTEGER DEFAULT 0,
        description TEXT DEFAULT '',
        version_status TEXT DEFAULT 'new'
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS template_fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER,
        field_name TEXT,
        FOREIGN KEY (file_id) REFERENCES json_files(id)
    )
    ''')
    
    # Add new columns if they don't exist (for existing databases)
    try:
        cursor.execute('ALTER TABLE json_files ADD COLUMN project TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE json_files ADD COLUMN is_deprecated INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE json_files ADD COLUMN description TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE json_files ADD COLUMN version_status TEXT DEFAULT 'new'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

def insert_data(directory):
    """Insert JSON file data into database"""
    conn = sqlite3.connect('json_fields.db')
    cursor = conn.cursor()
    
    # 获取基准目录用于计算相对路径
    base_dir = os.path.abspath(directory)
    
    # Insert new data (不清除已有数据，保留属性)
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'template' in data and isinstance(data['template'], list):
                            # 使用相对路径
                            relative_path = os.path.relpath(file_path, base_dir)
                            tpl_name = data.get('tpl_name', 'N/A')
                            
                            # 检查文件是否已存在
                            cursor.execute('SELECT id, project, is_deprecated, description, version_status FROM json_files WHERE file_path = ?',
                                         (relative_path,))
                            existing = cursor.fetchone()
                            
                            if existing:
                                # 文件已存在，保留已有属性
                                file_id = existing[0]
                                # 更新tpl_name（可能从文件中读取到新的）
                                cursor.execute('UPDATE json_files SET tpl_name = ? WHERE id = ?',
                                             (tpl_name, file_id))
                            else:
                                # 新文件，插入默认属性
                                cursor.execute('INSERT INTO json_files (file_path, tpl_name, project, is_deprecated, description, version_status) VALUES (?, ?, ?, ?, ?, ?)',
                                             (relative_path, tpl_name, '', 0, '', 'new'))
                                file_id = cursor.lastrowid
                            
                            # 删除旧的template fields（如果存在）
                            cursor.execute('DELETE FROM template_fields WHERE file_id = ?', (file_id,))
                            
                            # 插入template fields
                            for field in data['template']:
                                cursor.execute('INSERT INTO template_fields (file_id, field_name) VALUES (?, ?)',
                                             (file_id, field))
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    conn.commit()
    conn.close()

def search_field(field_name, version_status='all', project='all', status='all'):
    """Search for field in database"""
    conn = sqlite3.connect('json_fields.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build dynamic WHERE clause
    where_conditions = ['f.field_name = ?']
    params = [field_name]
    
    if version_status != 'all':
        where_conditions.append('j.version_status = ?')
        params.append(version_status)
    
    if project != 'all':
        where_conditions.append('j.project = ?')
        params.append(project)
    
    if status == 'active':
        where_conditions.append('j.is_deprecated = 0')
    elif status == 'deprecated':
        where_conditions.append('j.is_deprecated = 1')
    
    where_clause = ' AND '.join(where_conditions)
    
    # Search for field occurrences with file attributes
    cursor.execute(f'''
    SELECT j.file_path, j.tpl_name, j.project, j.is_deprecated, j.description, j.version_status
    FROM json_files j
    JOIN template_fields f ON j.id = f.file_id
    WHERE {where_clause}
    ''', params)
    
    results = [dict(row) for row in cursor.fetchall()]
    
    # Count occurrences
    cursor.execute(f'''
    SELECT COUNT(*) as count
    FROM template_fields f
    JOIN json_files j ON f.file_id = j.id
    WHERE {where_clause}
    ''', params)
    
    count = cursor.fetchone()['count']
    
    conn.close()
    return results, count

def update_file_attributes(file_path, project, is_deprecated, description, version_status='new'):
    """Update file attributes in database"""
    conn = sqlite3.connect('json_fields.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE json_files 
    SET project = ?, is_deprecated = ?, description = ?, version_status = ?
    WHERE file_path = ?
    ''', (project, int(is_deprecated), description, version_status, file_path))
    
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_all_templates(version_status='all', project='all', status='all'):
    """Get all template files with their attributes and fields"""
    conn = sqlite3.connect('json_fields.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build dynamic WHERE clause
    where_conditions = []
    params = []
    
    if version_status != 'all':
        where_conditions.append('j.version_status = ?')
        params.append(version_status)
    
    if project != 'all':
        where_conditions.append('j.project = ?')
        params.append(project)
    
    if status == 'active':
        where_conditions.append('j.is_deprecated = 0')
    elif status == 'deprecated':
        where_conditions.append('j.is_deprecated = 1')
    
    where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
    
    cursor.execute(f'''
    SELECT j.id, j.file_path, j.tpl_name, j.project, j.is_deprecated, j.description, j.version_status
    FROM json_files j
    WHERE {where_clause}
    ORDER BY j.file_path
    ''', params)
    
    results = []
    for row in cursor.fetchall():
        template = dict(row)
        # 获取该模板的所有字段
        cursor.execute('''
        SELECT field_name FROM template_fields WHERE file_id = ? ORDER BY field_name
        ''', (template['id'],))
        template['fields'] = [r['field_name'] for r in cursor.fetchall()]
        template['field_count'] = len(template['fields'])
        results.append(template)
    
    conn.close()
    return results

def batch_update_attributes(file_paths, project, is_deprecated, description, version_status='new'):
    """Batch update attributes for multiple files"""
    conn = sqlite3.connect('json_fields.db')
    cursor = conn.cursor()
    
    updated_count = 0
    for file_path in file_paths:
        cursor.execute('''
        UPDATE json_files 
        SET project = ?, is_deprecated = ?, description = ?, version_status = ?
        WHERE file_path = ?
        ''', (project, int(is_deprecated), description, version_status, file_path))
        updated_count += cursor.rowcount
    
    conn.commit()
    conn.close()
    return updated_count

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    count = 0
    field_name = ''
    version_status = request.args.get('version_status', 'all')
    project = request.args.get('project', 'all')
    status = request.args.get('status', 'all')
    
    if request.method == 'POST':
        field_name = request.form.get('field_name', '').strip()
        version_status = request.form.get('version_status', 'all')
        project = request.form.get('project', 'all')
        status = request.form.get('status', 'all')
        if field_name:
            results, count = search_field(field_name, version_status, project, status)
    
    # Get all unique fields for autocomplete
    conn = sqlite3.connect('json_fields.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT field_name FROM template_fields ORDER BY field_name')
    all_fields = [row[0] for row in cursor.fetchall()]
    
    # Get all unique projects for filter dropdown
    cursor.execute('SELECT DISTINCT project FROM json_files WHERE project != "" AND project IS NOT NULL ORDER BY project')
    all_projects = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('index.html', field_name=field_name, results=results, count=count, 
                          all_fields=all_fields, all_projects=all_projects,
                          version_status=version_status, project=project, status=status)

@app.route('/update_attributes', methods=['POST'])
def update_attributes():
    """API endpoint to update file attributes"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        project = data.get('project', '')
        is_deprecated = data.get('is_deprecated', 0)
        description = data.get('description', '')
        version_status = data.get('version_status', 'new')
        
        if not file_path:
            return {'success': False, 'message': 'File path is required'}, 400
        
        success = update_file_attributes(file_path, project, is_deprecated, description, version_status)
        
        if success:
            return {'success': True, 'message': 'Attributes updated successfully'}
        else:
            return {'success': False, 'message': 'File not found'}, 404
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

@app.route('/templates', methods=['GET'])
def templates_list():
    """Show all template files"""
    version_status = request.args.get('version_status', 'all')
    project = request.args.get('project', 'all')
    status = request.args.get('status', 'all')
    
    templates = get_all_templates(version_status, project, status)
    
    # Get all unique projects for filter dropdown
    conn = sqlite3.connect('json_fields.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT project FROM json_files WHERE project != "" AND project IS NOT NULL ORDER BY project')
    all_projects = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('templates_list.html', templates=templates, all_projects=all_projects,
                          version_status=version_status, project=project, status=status)

@app.route('/batch_update_attributes', methods=['POST'])
def batch_update():
    """API endpoint to batch update file attributes"""
    try:
        data = request.get_json()
        file_paths = data.get('file_paths', [])
        project = data.get('project', '')
        version_status = data.get('version_status', '')
        is_deprecated = data.get('is_deprecated', '')
        description = data.get('description', '')
        
        if not file_paths:
            return {'success': False, 'message': 'No files selected'}, 400
        
        # If fields are empty string, we need to get current values
        if is_deprecated == '' and version_status == '' and project == '' and description == '':
            return {'success': False, 'message': 'No fields to update'}, 400
        
        # For batch update, if not specified, we'll keep original
        # We need to handle this differently - only update specified fields
        updated_count = 0
        conn = sqlite3.connect('json_fields.db')
        cursor = conn.cursor()
        
        for file_path in file_paths:
            # Build dynamic UPDATE query based on provided fields
            updates = []
            params = []
            
            if project != '':
                updates.append('project = ?')
                params.append(project)
            
            if version_status != '':
                updates.append('version_status = ?')
                params.append(version_status)
            
            if is_deprecated != '':
                updates.append('is_deprecated = ?')
                params.append(int(is_deprecated))
            
            if description != '':
                updates.append('description = ?')
                params.append(description)
            
            if updates:
                params.append(file_path)
                query = f"UPDATE json_files SET {', '.join(updates)} WHERE file_path = ?"
                cursor.execute(query, params)
                updated_count += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Attributes updated', 'updated_count': updated_count}
    except Exception as e:
        return {'success': False, 'message': str(e)}, 500

if __name__ == "__main__":
    import sys
    
    # 默认使用当前目录下的home目录
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home')
    
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        print(f"Usage: python json_fields_db.py [directory]")
        print(f"Default directory: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home')}")
        sys.exit(1)
    
    print(f"Using directory: {directory}")
    print("Creating database...")
    create_database()
    
    print(f"Inserting data from {directory}...")
    insert_data(directory)
    
    print("Starting web server...")
    print("Access at http://localhost:5000")
    app.run(debug=True)
