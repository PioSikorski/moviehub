import re


def parse_title_to_url(title: str) -> str:
    SYMBOLS = [":", "'"]
    for symbol in SYMBOLS:
        title = title.replace(symbol, "")
    return title.lower()


def format_title(title: str) -> str:
    title = title.replace("&", "and")
    return title


def format_title_for_rotten_tomatoes(title: str) -> str:
    title = title.replace(" ", "_").replace("-", "")
    title = re.sub(r"_+", "_", title)
    title = format_title(title=title)
    return title


def format_title_for_metacritic(title: str) -> str:
    title = title.replace(" ", "-")
    title = format_title(title=title)
    return title


def get_rotten_url(title: str, media_type: str) -> str:
    title = format_title_for_rotten_tomatoes(parse_title_to_url(title))
    base_url = "https://www.rottentomatoes.com/"
    if media_type == "series":
        return f"{base_url}tv/{title}"
    return f"{base_url}m/{title}"


def get_metacritic_url(title: str, media_type: str) -> str:
    title = format_title_for_metacritic(parse_title_to_url(title))
    base_url = "https://www.metacritic.com/"
    if media_type == "series":
        return f"{base_url}tv/{title}/"
    return f"{base_url}movie/{title}/"
