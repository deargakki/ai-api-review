from api_contract_review.src.services.confluence import ConfluenceService

def test_confluence():
    service = ConfluenceService()
    page_id = "98307"  # 从 URL 中提取的页面 ID
    
    # 获取 HTML 格式内容
    html_content = service.get_page_content(page_id)
    # 获取纯文本格式内容（使用新方法）
    text_content = service.get_page_content_as_text(page_id)
    # 获取页面标题
    title = service.get_page_title(page_id)
    
    print(f"Page Title: {title}")
    print(f"HTML Content Length: {len(html_content) if html_content else 0}")
    print(f"Text Content Length: {len(text_content) if text_content else 0}")
    
    # 打印 HTML 格式内容
    print("\nDocument Content (HTML):")
    print(html_content)
    
    # 打印纯文本格式内容（带表格结构和代码块）
    if text_content:
        print("\nDocument Content (Plain Text with Tables and Code):")
        print(text_content)
    else:
        print("\nDocument Content (Plain Text with Tables and Code): None")

if __name__ == "__main__":
    test_confluence()
