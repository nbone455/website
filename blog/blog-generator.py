import os
import yaml
import markdown
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def parse_frontmatter(md_content):
    """Parse YAML frontmatter from markdown content."""
    if md_content.startswith('---'):
        try:
            _, frontmatter, content = md_content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            return metadata, content.strip()
        except:
            return {}, md_content
    return {}, md_content

def format_date(date_value):
    """Format date value to a readable string format."""
    if isinstance(date_value, str):
        try:
            date = datetime.strptime(date_value, '%Y-%m-%d')
        except ValueError:
            return date_value
    elif isinstance(date_value, datetime):
        date = date_value
    else:
        try:
            date = datetime.combine(date_value, datetime.min.time())
        except:
            return str(date_value)
    
    return date.strftime('%B %d, %Y')

def get_post_data(md_file):
    """Extract post data from markdown file."""
    md_content = md_file.read_text(encoding='utf-8')
    metadata, content = parse_frontmatter(md_content)
    
    return {
        'title': metadata.get('title', 'Untitled'),
        'date': metadata.get('date', datetime.now().date()),
        'date_str': format_date(metadata.get('date', datetime.now().date())),
        'topics': metadata.get('topics', []),
        'filename': md_file.stem + '.html',
        'path': str(md_file)
    }

def generate_index_page(posts, template_file, output_dir):
    """Generate index page with filtering capabilities."""
    # Sort posts by date (newest first)
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)
    
    # Collect all unique topics
    all_topics = sorted(set(topic for post in posts for topic in post['topics']))
    
    # Group posts by topic
    posts_by_topic = defaultdict(list)
    for post in sorted_posts:
        for topic in post['topics']:
            posts_by_topic[topic].append(post)
    
    # Read index template
    template = template_file.parent / 'blog-index-template.html'
    index_html = template.read_text(encoding='utf-8')
    
    # Generate topics list HTML
    topics_html = '\n'.join([
        f'<button class="topic-button" data-topic="{topic}">{topic}</button>'
        for topic in all_topics
    ])
    
    # Generate posts list HTML
    posts_html = '\n'.join([
        f'''
        <div class="post-item" data-date="{post['date']}" data-topics="{','.join(post['topics'])}">
            <div class="post-date">{post['date_str']}</div>
            <div class="post-title">
                <a href="{post['filename']}">{post['title']}</a>
            </div>
            <div class="post-topics">
                {' '.join(f'<span class="topic-tag">{topic}</span>' for topic in post['topics'])}
            </div>
        </div>
        '''
        for post in sorted_posts
    ])
    
    # Replace placeholders
    final_html = index_html.replace('<!-- TOPICS -->', topics_html).replace('<!-- POSTS -->', posts_html)
    
    # Write index file
    output_path = output_dir / 'index.html'
    output_path.write_text(final_html, encoding='utf-8')
    print(f'Generated index page: {output_path}')

def generate_html(md_file, template_file, output_dir):
    """Generate HTML file from markdown content using template."""
    # Read markdown file
    md_content = md_file.read_text(encoding='utf-8')
    
    # Parse frontmatter and content
    metadata, content = parse_frontmatter(md_content)
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'footnotes'])
    html_content = md.convert(content)
    
    # Read template
    template = template_file.read_text(encoding='utf-8')
    
    # Format date
    date_str = format_date(metadata.get('date', 'No date'))
    
    # Generate topics HTML if present
    topics_html = ''
    if metadata.get('topics'):
        topics_html = '<div class="post-topics">' + ' '.join(
            f'<span class="topic-tag">{topic}</span>' 
            for topic in metadata['topics']
        ) + '</div>'
    
    # Replace placeholders in template
    final_html = template.replace(
        '<h1>What is Folk Music?</h1>',
        f'<h1>{metadata.get("title", "Untitled")}</h1>'
    ).replace(
        'January 5, 2025',
        date_str
    ).replace(
        '<p>Your content goes here...</p>',
        html_content + topics_html
    )
    
    # Create output filename
    output_filename = md_file.stem + '.html'
    output_path = output_dir / output_filename
    
    # Write HTML file
    output_path.write_text(final_html, encoding='utf-8')
    print(f'Generated {output_path}')

def main():
    # Setup directories
    script_dir = Path(__file__).parent
    posts_dir = script_dir / 'posts'
    template_file = script_dir / 'blog-template.html'
    output_dir = script_dir / 'output'
    
    # Create directories if they don't exist
    output_dir.mkdir(exist_ok=True)
    posts_dir.mkdir(exist_ok=True)
    
    # Process all markdown files and collect post data
    posts = []
    for md_file in posts_dir.glob('*.md'):
        post_data = get_post_data(md_file)
        posts.append(post_data)
        generate_html(md_file, template_file, output_dir)
    
    # Generate index page
    if posts:
        generate_index_page(posts, template_file, output_dir)
    else:
        print("No markdown files found in the 'posts' directory.")
        print(f"Please add your .md files to: {posts_dir}")

if __name__ == '__main__':
    main()
