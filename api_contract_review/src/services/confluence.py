from atlassian import Confluence
from ..config.config import config
from bs4 import BeautifulSoup

def html_to_text_with_tables_and_code(html_content):
    """将 HTML 转换为纯文本，保留表格结构和代码块"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 处理代码块
    for code_macro in soup.find_all('ac:structured-macro', {'ac:name': 'code'}):
        # 找到代码内容
        code_body = code_macro.find('ac:plain-text-body')
        if code_body:
            code_content = code_body.get_text(strip=True)
            # 构建代码块的纯文本表示
            code_text = '\n```json\n' + code_content + '\n```\n'
            # 替换原代码块
            code_macro.replace_with(BeautifulSoup(code_text, 'html.parser'))
    
    # 处理表格
    for table in soup.find_all('table'):
        # 找到所有行
        rows = table.find_all('tr')
        if not rows:
            continue
        
        # 提取表头
        headers = []
        header_row = rows[0]
        for th in header_row.find_all(['th', 'td']):
            headers.append(th.get_text(strip=True))
        
        # 提取数据行
        data_rows = []
        for row in rows[1:]:
            row_data = []
            for td in row.find_all(['th', 'td']):
                row_data.append(td.get_text(strip=True))
            if row_data:
                data_rows.append(row_data)
        
        # 构建表格的纯文本表示
        if headers:
            # 计算每列的最大宽度
            col_widths = []
            for i in range(len(headers)):
                max_width = len(headers[i])
                for row in data_rows:
                    if i < len(row):
                        max_width = max(max_width, len(row[i]))
                col_widths.append(max_width)
            
            # 构建表格
            table_text = '\n'
            # 表头
            header_line = ' | '.join([headers[i].ljust(col_widths[i]) for i in range(len(headers))])
            table_text += header_line + '\n'
            # 分隔线
            separator_line = ' | '.join(['-' * col_widths[i] for i in range(len(headers))])
            table_text += separator_line + '\n'
            # 数据行
            for row in data_rows:
                row_line = ' | '.join([row[i].ljust(col_widths[i]) if i < len(row) else ' ' * col_widths[i] for i in range(len(headers))])
                table_text += row_line + '\n'
            
            # 替换原表格
            table.replace_with(BeautifulSoup(table_text, 'html.parser'))
    
    # 转换为纯文本
    return soup.get_text(separator='\n', strip=True)

class ConfluenceService:
    def __init__(self):
        self.confluence = Confluence(
            url=config.CONFLUENCE_URL,
            username=config.CONFLUENCE_USERNAME,
            password=config.CONFLUENCE_API_TOKEN
        )

    def get_page_content(self, page_id):
        """获取 Confluence 页面内容（HTML 格式）"""
        try:
            page = self.confluence.get_page_by_id(page_id, expand='body.storage')
            return page['body']['storage']['value']
        except Exception as e:
            print(f"Error getting page content: {e}")
            return None

    def get_page_content_as_text(self, page_id):
        """获取 Confluence 页面内容（纯文本格式，保留表格和代码块）"""
        html_content = self.get_page_content(page_id)
        if not html_content:
            return None
        return html_to_text_with_tables_and_code(html_content)

    def get_page_title(self, page_id):
        """获取 Confluence 页面标题"""
        try:
            page = self.confluence.get_page_by_id(page_id)
            return page['title']
        except Exception as e:
            print(f"Error getting page title: {e}")
            return None
