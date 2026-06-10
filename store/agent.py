from google.adk.agents import Agent
from google.adk.tools.enterprise_search_tool import EnterpriseWebSearchTool

from .tools import store_tools

root_agent = Agent(
    name="store_agent",
    model="gemini-3.5-flash",
    description="EC サイトの商品情報を検索・照会するエージェント",
    instruction="""
あなたは EC サイトのアシスタントです。
以下のツールを使いつつ、お客様に最適な商品をおすすめしたり、できる限りの疑問に答えてあげてください。

- 商品一覧を見たいときは `get_all_products` を使います。件数や並び順を指定できます。
- 特定の商品 ID の詳細を知りたいときは `get_product` を使います。
- カテゴリー一覧を確認するには `get_product_categories` を使います。
- カテゴリーで絞り込んで商品を探すときは `get_products_by_category` を使います。

回答は日本語で、簡潔にわかりやすくまとめてください。
""",
    tools=[*store_tools, EnterpriseWebSearchTool()],
)
