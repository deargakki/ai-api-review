from atlassian import Confluence
import os
from dotenv import load_dotenv

load_dotenv()

class ConfluenceService:
    def __init__(self):
        self.confluence = Confluence(
            url=os.getenv('CONFLUENCE_URL'),
            username=os.getenv('CONFLUENCE_USERNAME'),
            password=os.getenv('CONFLUENCE_API_TOKEN')
        )

    def get_page_content(self, page_id):
        """获取 Confluence 页面内容"""
        try:
            page = self.confluence.get_page_by_id(page_id, expand='body.storage')
            return page['body']['storage']['value']
        except Exception as e:
            print(f"Error getting page content: {e}")
            return None

    def get_page_title(self, page_id):
        """获取 Confluence 页面标题"""
        try:
            page = self.confluence.get_page_by_id(page_id)
            return page['title']
        except Exception as e:
            print(f"Error getting page title: {e}")
            return None
