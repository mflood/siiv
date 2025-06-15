import os
import pytest
from agent.tools.list_files_tool import ListFilesTool
from agent.tools.tool_interface import ToolExecutionResult

@pytest.fixture
def setup_tool(tmp_path):
    tool = ListFilesTool(pwd=str(tmp_path))
    return tool

def test_execute_valid_directory(setup_tool):
    test_dir = os.path.join(setup_tool._root_path, 'test_dir')
    os.mkdir(test_dir)
    with open(os.path.join(test_dir, 'file1.txt'), 'w') as f:
        f.write('Test file 1')
    with open(os.path.join(test_dir, 'file2.txt'), 'w') as f:
        f.write('Test file 2')

    result = setup_tool.execute(directory='test_dir', recursive=False)
    assert result.return_code == 0
    assert 'file1.txt' in result.stdout
    assert 'file2.txt' in result.stdout

def test_execute_invalid_directory(setup_tool):
    result = setup_tool.execute(directory='invalid_dir', recursive=False)
    assert result.return_code == 1
    assert 'Not a directory' in result.stderr

def test_execute_outside_allowed_directory(setup_tool):
    result = setup_tool.execute(directory='.', recursive=False)
    assert result.return_code == 0
    assert 'test_dir' not in result.stdout

def test_execute_ignore_files(setup_tool):
    test_dir = os.path.join(setup_tool._root_path, 'test_dir')
    os.mkdir(test_dir)
    with open(os.path.join(test_dir, '.DS_Store'), 'w') as f:
        f.write('Ignore this')
    with open(os.path.join(test_dir, 'file3.txt'), 'w') as f:
        f.write('Test file 3')

    result = setup_tool.execute(directory='test_dir', recursive=False)
    assert result.return_code == 0
    assert 'file3.txt' in result.stdout
    assert '.DS_Store' not in result.stdout

def test_execute_recursive_listing(setup_tool):
    test_dir = os.path.join(setup_tool._root_path, 'test_dir')
    os.mkdir(test_dir)
    sub_dir = os.path.join(test_dir, 'sub_dir')
    os.mkdir(sub_dir)
    with open(os.path.join(test_dir, 'file4.txt'), 'w') as f:
        f.write('Test file 4')
    with open(os.path.join(sub_dir, 'file5.txt'), 'w') as f:
        f.write('Test file 5')

    result = setup_tool.execute(directory='test_dir', recursive=True)
    assert result.return_code == 0
    assert 'file4.txt' in result.stdout
    assert 'file5.txt' in result.stdout
