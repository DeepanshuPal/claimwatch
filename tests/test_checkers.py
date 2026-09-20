from claimwatch.checkers import checker_for


def test_supported_platforms():
    for platform in ["domain", "github", "x", "instagram", "tiktok"]:
        assert checker_for(platform)
