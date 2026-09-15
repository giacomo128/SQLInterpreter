import main
import pytest
from pathlib import Path

origin = Path(__file__).parent

def test_not_existing_program_file():
    with pytest.raises(RuntimeError) as e:
        main.runner.execute("notexisting.usql", False)

    with pytest.raises(RuntimeError) as e:
        main.runner.execute("notexisting.usql", True)

def test_file_not_usql():
    file_path = origin / "test_files" / "sample.csv"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, True)

def test_select(capsys):
    file_path = origin / "test_programs" / "select.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc, mt, ms, cr;\n"
        "CS3052, Computational Complexity, 2, 15;\n"
        "cs3101, Databases, 2, 15;\n"
    )
    assert output.out == str_compare

def test_project(capsys):
    file_path = origin / "test_programs" / "project.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "ms;\n"
        "1;\n"
        "2;\n"
    )
    assert output.out == str_compare

def test_diff(capsys):
    file_path = origin / "test_programs" / "difference.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc, mt, ms, cr;\n"
        "CS2001, Foundations of Computation, 1, 30;\n"
        "cs3101, Databases, 2, 15;\n"
    )
    assert output.out == str_compare

def test_union(capsys):
    file_path = origin / "test_programs" / "union.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc, mt, ms, cr;\n"
        "CS2001, Foundations of Computation, 1, 30;\n"
        "CS3050, Logic and Reasoning, 1, 15;\n"
        "CS3052, Computational Complexity, 2, 15;\n"
        "cs3101, Databases, 2, 15;\n"
        "CS3106, HCI, 2, 15;\n"
    )
    assert output.out == str_compare

def test_rename(capsys):
    file_path = origin / "test_programs" / "rename.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc1, mt1, ms1, cr1;\n"
        "CS2001, Foundations of Computation, 1, 30;\n"
        "CS3050, Logic and Reasoning, 1, 15;\n"
        "CS3052, Computational Complexity, 2, 15;\n"
        "cs3101, Databases, 2, 15;\n"
    )
    assert output.out == str_compare

def test_join(capsys):
    file_path = origin / "test_programs" / "join.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc, mt, ms, cr;\n"
        "CS3050, Logic and Reasoning, 1, 15;\n"
        "CS3052, Computational Complexity, 2, 15;\n"
    )
    assert output.out == str_compare

def test_original(capsys):
    file_path = origin / "test_programs" / "test.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc, mt, cr;\n"
        "CS3052, Computational Complexity, 15;\n"
        "cs3101, Databases, 15;\n"
    )
    assert output.out == str_compare

def test_fd(capsys):
    file_path = origin / "test_programs" / "fd_creation.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc, mt, ms, cr;\n"
        "CS3052, Computational Complexity, 2, 15;\n"
        "cs3101, Databases, 2, 15;\n"
    )
    assert output.out == str_compare

def test_let(capsys):
    file_path = origin / "test_programs" / "let.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        ""
    )
    assert output.out == str_compare

def test_wrong_select():
    file_path = origin / "test_programs" / "wrong_select.usql"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, True)

def test_wrong_project():
    file_path = origin / "test_programs" / "wrong_project.usql"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, True)

def test_wrong_rename():
    file_path = origin / "test_programs" / "wrong_rename.usql"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

def test_wrong_union():
    file_path = origin / "test_programs" / "wrong_union.usql"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

def test_wrong_difference():
    file_path = origin / "test_programs" / "wrong_difference.usql"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

def test_wrong_fd():
    file_path = origin / "test_programs" / "invalid_fd.usql"

    with pytest.raises(RuntimeError) as e:
        main.runner.execute(file_path, False)

def test_project_rename(capsys):
    file_path = origin / "test_programs" / "project_rename.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "ms1;\n"
        "1;\n"
        "2;\n"
    )
    assert output.out == str_compare

def test_select_rename(capsys):
    file_path = origin / "test_programs" / "select_rename.usql"
    main.runner.execute(file_path, False)
    output = capsys.readouterr()
    str_compare = (
        "mc1, mt1, ms1, cr1;\n"
        "CS3052, Computational Complexity, 2, 15;\n"
        "cs3101, Databases, 2, 15;\n"
    )
    assert output.out == str_compare