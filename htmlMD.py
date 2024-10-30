import os
import markdown
import frontmatter
from pathlib import Path

# Simple HTML template
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="date">{date}</div>
    <div class="content">
        {content}
    </div>
</body>
</html>
"""

def convert_markdown_files():
    # Create output directory if it doesn't exist
    blog_dir = Path("blog")
    html_dir = Path("blog/html")
    html_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each markdown file
    for md_file in blog_dir.glob("*.md"):
        # Read the markdown file with frontmatter
        post = frontmatter.load(md_file)
        
        # Extract metadata (or use defaults)
        title = post.get('title', md_file.stem.replace('-', ' ').title())
        date = post.get('date', '')
        
        # Convert markdown to HTML
        html_content = markdown.markdown(post.content, extensions=['fenced_code', 'tables'])
        
        # Create HTML file
        html_filename = md_file.stem + '.html'
        html_path = html_dir / html_filename
        
        # Fill in the template
        html_output = PAGE_TEMPLATE.format(
            title=title,
            date=date,
            content=html_content
        )
        
        # Write the HTML file
        html_path.write_text(html_output)
        
        print(f"Converted {md_file.name} to {html_filename}")

if __name__ == "__main__":
    convert_markdown_files()