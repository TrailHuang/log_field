// ===== 通用模态框函数 =====

function openEditModal(filePath, project, isDeprecated, description, versionStatus) {
    document.getElementById('edit_file_path').value = filePath;
    document.getElementById('edit_project').value = project;
    document.getElementById('edit_version_status').value = versionStatus || 'new';
    document.getElementById('edit_is_deprecated').value = isDeprecated;
    document.getElementById('edit_description').value = description;
    document.getElementById('editModal').style.display = 'block';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

function saveAttributes() {
    const formData = {
        file_path: document.getElementById('edit_file_path').value,
        project: document.getElementById('edit_project').value,
        version_status: document.getElementById('edit_version_status').value,
        is_deprecated: document.getElementById('edit_is_deprecated').value,
        description: document.getElementById('edit_description').value
    };

    fetch('/update_attributes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('属性保存成功！');
            closeEditModal();
            location.reload();
        } else {
            alert('错误: ' + data.message);
        }
    })
    .catch(error => {
        alert('错误: ' + error);
    });
}

// ===== 模板列表页专用函数 =====

function filterTemplates() {
    const versionStatus = document.getElementById('version_status').value;
    const project = document.getElementById('project').value;
    const status = document.getElementById('status').value;
    
    let url = '/templates?version_status=' + versionStatus;
    if (project !== 'all') {
        url += '&project=' + encodeURIComponent(project);
    }
    if (status !== 'all') {
        url += '&status=' + status;
    }
    
    window.location.href = url;
}

function showFields(templateId, filePath, tplName, fieldCount) {
    const fields = (typeof templatesFields !== 'undefined' && templatesFields[templateId]) ? templatesFields[templateId] : [];
    document.getElementById('fieldsModalTitle').textContent = '模板字段: ' + tplName;
    const content = document.getElementById('fieldsModalContent');

    let html = '<div style="margin-bottom: 10px; color: #666;">文件: ' + filePath + '</div>';
    html += '<div style="margin-bottom: 10px; color: #666;">字段总数: ' + fields.length + '</div>';
    html += '<div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">';
    html += '<strong>字段列表:</strong><br><br>';

    if (fields.length === 0) {
        html += '<div style="color: #999;">暂无字段</div>';
    } else {
        fields.forEach(function(field, index) {
            html += '<span style="display: inline-block; background-color: #e3f2fd; padding: 4px 8px; margin: 3px; border-radius: 3px; font-size: 13px;">' + index + '. ' + field + '</span>';
        });
    }

    html += '</div>';
    content.innerHTML = html;
    document.getElementById('fieldsModal').style.display = 'block';
}

function closeFieldsModal() {
    document.getElementById('fieldsModal').style.display = 'none';
}

function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = selectAllCheckbox.checked;
    });
    updateSelectedCount();
}

function selectAll() {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = true;
    });
    document.getElementById('selectAllCheckbox').checked = true;
    updateSelectedCount();
}

function deselectAll() {
    const checkboxes = document.querySelectorAll('.row-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = false;
    });
    document.getElementById('selectAllCheckbox').checked = false;
    updateSelectedCount();
}

function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    const count = checkboxes.length;
    document.getElementById('selectedCount').textContent = count;
    document.getElementById('batchCount').textContent = count;
    document.getElementById('batchEditBtn').disabled = count === 0;
}

function openBatchEdit() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('请至少选择一个模板');
        return;
    }
    document.getElementById('batchEditModal').style.display = 'block';
}

function closeBatchEditModal() {
    document.getElementById('batchEditModal').style.display = 'none';
}

function saveBatchAttributes() {
    const checkboxes = document.querySelectorAll('.row-checkbox:checked');
    const filePaths = Array.from(checkboxes).map(cb => cb.value);

    const project = document.getElementById('batch_project').value;
    const versionStatus = document.getElementById('batch_version_status').value;
    const isDeprecated = document.getElementById('batch_is_deprecated').value;
    const description = document.getElementById('batch_description').value;

    fetch('/batch_update_attributes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file_paths: filePaths,
            project: project,
            version_status: versionStatus,
            is_deprecated: isDeprecated,
            description: description
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('成功更新 ' + data.updated_count + ' 个模板！');
            closeBatchEditModal();
            location.reload();
        } else {
            alert('错误: ' + data.message);
        }
    })
    .catch(error => {
        alert('错误: ' + error);
    });
}

// ===== 点击外部关闭模态框 =====
window.onclick = function(event) {
    const editModal = document.getElementById('editModal');
    if (editModal && event.target == editModal) {
        closeEditModal();
    }

    const batchEditModal = document.getElementById('batchEditModal');
    if (batchEditModal && event.target == batchEditModal) {
        closeBatchEditModal();
    }

    const fieldsModal = document.getElementById('fieldsModal');
    if (fieldsModal && event.target == fieldsModal) {
        closeFieldsModal();
    }
}
