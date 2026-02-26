import math
import os
import textwrap

import requests


GITHUB_API_URL = "https://api.github.com/graphql"


def fetch_total_contributions(token: str, username: str) -> int:
    """Fetch total contributions in the last year for the given user."""
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        GITHUB_API_URL,
        json={"query": query, "variables": {"login": username}},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    # Be defensive in case of errors
    try:
        return (
            data["data"]["user"]["contributionsCollection"][
                "contributionCalendar"
            ]["totalContributions"]
            or 0
        )
    except (KeyError, TypeError):
        # Fallback to zero on unexpected response
        return 0


def generate_svg(total_contributions: int, output_path: str) -> None:
    """Generate a coffee board SVG based on total contributions."""
    # Each contribution == one coffee, but cap for the board so it doesn't explode
    max_cups = 200
    cups = max(1, min(total_contributions, max_cups))

    cups_per_row = 10
    cup_size = 24  # spacing between coffees
    padding_x = 24
    padding_y = 60

    rows = math.ceil(cups / cups_per_row)

    width = padding_x * 2 + cups_per_row * cup_size
    height = padding_y * 2 + rows * cup_size

    title = "☕ Coffee Board"
    subtitle = f"{total_contributions} contribuições = {total_contributions} cafés"
    if total_contributions > max_cups:
        subtitle += f" (mostrando {max_cups} no quadro)"

    svg_parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "  <defs>",
        "    <style>",
        "      .bg { fill: #0d1117; }",
        "      .title { fill: #f5f5f5; font-size: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; }",
        "      .subtitle { fill: #c9d1d9; font-size: 12px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; }",
        "      .cup { font-size: 18px; font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', system-ui; }",
        "    </style>",
        "  </defs>",
        f"  <rect class='bg' x='0' y='0' width='{width}' height='{height}' rx='16' ry='16' />",
        f"  <text class='title' x='{padding_x}' y='32'>{title}</text>",
        f"  <text class='subtitle' x='{padding_x}' y='50'>{subtitle}</text>",
    ]

    start_y = padding_y

    for i in range(cups):
        row = i // cups_per_row
        col = i % cups_per_row
        x = padding_x + col * cup_size
        y = start_y + row * cup_size
        svg_parts.append(f"  <text class='cup' x='{x}' y='{y}'>☕</text>")

    # Small footer note
    footer_text = "Cada contribuição vira um café."
    svg_parts.append(
        f"  <text class='subtitle' x='{padding_x}' y='{height - 16}'>{footer_text}</text>"
    )

    svg_parts.append("</svg>")

    svg_content = "\n".join(svg_parts)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN environment variable is required")

    username = os.environ.get("GITHUB_ACTOR") or os.environ.get("GITHUB_REPOSITORY_OWNER") or "SENPedroVitor"

    total = fetch_total_contributions(token, username)

    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "coffee-board.svg")
    generate_svg(total, output_path)


if __name__ == "__main__":
    main()
