import math
import os
from datetime import datetime

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
    """Generate a cleaner, more minimal coffee board SVG."""
    # Each contribution == one coffee, but cap for the board
    max_cups = 120
    cups = max(1, min(total_contributions, max_cups))

    cups_per_row = 12
    cup_size = 20  # spacing between coffees
    padding_x = 32
    padding_y = 56

    rows = math.ceil(cups / cups_per_row)

    width = padding_x * 2 + cups_per_row * cup_size
    height = padding_y * 2 + rows * cup_size + 20

    title = "Coffee Contributions"
    updated_at = datetime.utcnow().strftime("%Y-%m-%d")

    svg_parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "  <defs>",
        "    <style>",
        "      .bg { fill: #050816; }",
        "      .title { fill: #e5e7eb; font-size: 18px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; }",
        "      .meta { fill: #9ca3af; font-size: 11px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; }",
        "      .cup { font-size: 16px; font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', system-ui; }",
        "    </style>",
        "  </defs>",
        f"  <rect class='bg' x='0' y='0' width='{width}' height='{height}' rx='16' ry='16' />",
        f"  <text class='title' x='{padding_x}' y='30'>☕ Coffee board</text>",
        f"  <text class='meta' x='{padding_x}' y='46'>{total_contributions} contribuições no último ano · atualizado {updated_at}</text>",
    ]

    start_y = padding_y

    for i in range(cups):
        row = i // cups_per_row
        col = i % cups_per_row
        x = padding_x + col * cup_size
        y = start_y + row * cup_size
        svg_parts.append(f"  <text class='cup' x='{x}' y='{y}'>☕</text>")

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
