from wattson_core.update_manager.git import GitUpdateChecker


def test_git_update_checker_exists():
    checker = GitUpdateChecker()

    assert checker is not None
