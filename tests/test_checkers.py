from claimwatch.checkers import checker_for


def test_supported_platforms():
    platforms = [
        "domain", "github", "x", "instagram", "tiktok", "youtube", "linkedin",
        "reddit", "threads", "twitch", "pinterest", "snapchat", "bluesky",
        "mastodon", "telegram", "producthunt", "substack", "medium", "dev.to",
        "npm", "pypi", "dockerhub",
    ]
    for platform in platforms:
        assert checker_for(platform)
