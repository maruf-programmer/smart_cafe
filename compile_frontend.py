import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_CORE_DIR = os.path.join(BASE_DIR, 'core', 'templates', 'core')
TEMPLATE_STAFF_DIR = os.path.join(BASE_DIR, 'core', 'templates', 'staff')
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')
FRONTEND_STAFF_DIR = os.path.join(FRONTEND_DIR, 'staff')

os.makedirs(FRONTEND_DIR, exist_ok=True)
os.makedirs(FRONTEND_STAFF_DIR, exist_ok=True)
os.makedirs(os.path.join(FRONTEND_DIR, 'js'), exist_ok=True)

# Write JS config file
with open(os.path.join(FRONTEND_DIR, 'js', 'config.js'), 'w', encoding='utf-8') as f:
    f.write("const API_BASE_URL = 'http://127.0.0.1:8000';\n")

# Load base layouts
base_html = open(os.path.join(TEMPLATE_CORE_DIR, 'base.html'), 'r', encoding='utf-8').read()
base_staff_html = open(os.path.join(TEMPLATE_STAFF_DIR, 'base_staff.html'), 'r', encoding='utf-8').read()

def extract_block(content, block_name):
    pattern = rf'{{% block {block_name} %}}(.*?){{% endblock %}}'
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ''

def clean_django_tags(html):
    # Remove load static tags
    html = re.sub(r'{% load static %}', '', html)
    # Replace csrf token
    html = re.sub(r"{'X-CSRFToken': '[^']+'}", "{'X-CSRFToken': getCookie('csrftoken')}", html)
    html = re.sub(r'"{% csrf_token %}"', '""', html)
    html = re.sub(r'{% csrf_token %}', '', html)
    
    # Replace standard menu url routing
    html = re.sub(r'"{% url \'core:menu\' table_id %}"', '"menu.html"', html)
    html = re.sub(r'"{% url \'core:cart\' table_id %}"', '"cart.html"', html)
    html = re.sub(r'"{% url \'core:my_orders\' table_id %}"', '"my_orders.html"', html)
    html = re.sub(r'"{% url \'core:complete_session\' table_id %}"', '"complete_session.html"', html)
    html = re.sub(r'"{% url \'core:staff_dashboard\' %}"', '"staff/dashboard.html"', html)
    
    # Staff navigation mapping
    html = re.sub(r'"{% url \'core:staff_orders\' %}"', '"orders.html"', html)
    html = re.sub(r'"{% url \'core:staff_calls\' %}"', '"calls.html"', html)
    html = re.sub(r'"{% url \'core:staff_menu\' %}"', '"menu.html"', html)
    html = re.sub(r'"{% url \'core:staff_tables\' %}"', '"tables.html"', html)
    html = re.sub(r'"/admin/logout/"', 'API_BASE_URL + "/admin/logout/"', html)
    
    # Fix fetch api calls to point to API_BASE_URL and include credentials
    # 1. Matches fetch('/api/...)
    html = re.sub(r"fetch\('(/api/[^']+)'\)", r"fetch(API_BASE_URL + '\1', { credentials: 'include' })", html)
    html = re.sub(r"fetch\('(/api/[^']+)',\s*({[^}]+})\)", r"fetch(API_BASE_URL + '\1', Object.assign({ credentials: 'include' }, \2))", html)
    
    # 2. Matches fetch(`/api/...)
    html = re.sub(r"fetch\(`(/api/[^`]+)`\)", r"fetch(API_BASE_URL + `\1`, { credentials: 'include' })", html)
    html = re.sub(r"fetch\(`(/api/[^`]+)`,\s*({[^}]+})\)", r"fetch(API_BASE_URL + `\1`, Object.assign({ credentials: 'include' }, \2))", html)
    
    # Prepend media URLs
    html = re.sub(r'"/media/', 'API_BASE_URL + "/media/', html)
    html = re.sub(r'`/media/', 'API_BASE_URL + `/media/', html)
    
    # Custom dashboard staff setup & redirection URL updates
    html = html.replace('document.getElementById(\'lblPendingOrders\').innerText = data.pending_orders;', 'localStorage.setItem(\'is_staff\', \'true\');\n            document.getElementById(\'lblPendingOrders\').innerText = data.pending_orders;')
    html = html.replace('href="/complete/${t.id}/"', 'href="../complete_session.html?table_id=${t.id}"')
    html = html.replace('href="/complete/${table.id}/"', 'href="../complete_session.html?table_id=${table.id}"')
    
    # Static frontend edit redirections
    html = html.replace('/staff/menu/item/${item.id}/edit/', 'menu_item_form.html?item_id=${item.id}')
    html = html.replace('/staff/menu/item/${item_id}/edit/', 'menu_item_form.html?item_id=${item_id}')
    
    return html

def compile_customer_page(filename):
    print(f"Compiling Customer Page: {filename}")
    page_content = open(os.path.join(TEMPLATE_CORE_DIR, filename), 'r', encoding='utf-8').read()
    
    title = extract_block(page_content, 'title')
    extra_css = extract_block(page_content, 'extra_css')
    extra_js = extract_block(page_content, 'extra_js')
    content = extract_block(page_content, 'content')
    
    compiled = base_html
    
    # Replace header script configuration in base layout
    config_script = '<script src="js/config.js"></script>'
    compiled = compiled.replace('<head>', f'<head>\n    {config_script}')
    
    # Replace base block placeholders
    compiled = compiled.replace('{% block title %}Cafe Tizimi{% endblock %}', title or 'Smart Cafe')
    compiled = compiled.replace('{% block extra_css %}{% endblock %}', extra_css)
    compiled = compiled.replace('{% block extra_js %}{% endblock %}', extra_js)
    compiled = compiled.replace('{% block content %}{% endblock %}', content)
    
    # Adapt header action links dynamically using client-side JavaScript
    header_placeholder = """
        <div class="header-actions">
            {% if table_id %}
            <a href="{% url 'core:menu' table_id %}" title="Menyu"><i class="fas fa-book-open"></i></a>
            <a href="{% url 'core:cart' table_id %}" title="Savat"><i class="fas fa-shopping-cart"></i></a>
            {% endif %}
            {% if request.user.is_staff %}
            <a href="{% url 'core:staff_dashboard' %}" title="Admin Panel"><i class="fas fa-user-shield"></i></a>
            {% endif %}
        </div>
    """
    
    static_header = """
        <div class="header-actions" id="nav-actions">
            <a href="#" id="nav-menu-link" title="Menyu"><i class="fas fa-book-open"></i></a>
            <a href="#" id="nav-cart-link" title="Savat"><i class="fas fa-shopping-cart"></i></a>
            <a href="staff/dashboard.html" id="nav-admin-link" title="Admin Panel" style="display: none;"><i class="fas fa-user-shield"></i></a>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', () => {
                const urlParams = new URLSearchParams(window.location.search);
                let tId = urlParams.get('table_id') || localStorage.getItem('table_id');
                if (tId) {
                    localStorage.setItem('table_id', tId);
                    document.getElementById('nav-menu-link').href = `menu.html?table_id=${tId}`;
                    document.getElementById('nav-cart-link').href = `cart.html?table_id=${tId}`;
                } else {
                    document.getElementById('nav-menu-link').style.display = 'none';
                    document.getElementById('nav-cart-link').style.display = 'none';
                }
                if (localStorage.getItem('is_staff') === 'true') {
                    document.getElementById('nav-admin-link').style.display = 'inline-block';
                }
            });
        </script>
    """
    compiled = compiled.replace(header_placeholder, static_header)
    
    # Process relative API routes and Django templates syntax
    compiled = clean_django_tags(compiled)
    
    # Write out compiled HTML file
    with open(os.path.join(FRONTEND_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(compiled)

def compile_staff_page(filename):
    print(f"Compiling Staff Page: {filename}")
    page_content = open(os.path.join(TEMPLATE_STAFF_DIR, filename), 'r', encoding='utf-8').read()
    
    title = extract_block(page_content, 'title')
    page_title = extract_block(page_content, 'page_title')
    page_subtitle = extract_block(page_content, 'page_subtitle')
    top_actions = extract_block(page_content, 'top_actions')
    extra_css = extract_block(page_content, 'extra_css')
    extra_js = extract_block(page_content, 'extra_js')
    content = extract_block(page_content, 'content')
    
    compiled = base_staff_html
    
    # Replace header script configuration in base layout
    config_script = '<script src="../js/config.js"></script>'
    compiled = compiled.replace('<head>', f'<head>\n    {config_script}')
    
    # Replace base block placeholders
    compiled = compiled.replace('{% block title %}Boshqaruv Paneli{% endblock %}', title or 'Admin Panel')
    compiled = compiled.replace('{% block page_title %}Xush kelibsiz!{% endblock %}', page_title or 'Xush kelibsiz!')
    compiled = compiled.replace('{% block page_subtitle %}Boshqaruv Cockpit Panel{% endblock %}', page_subtitle or 'Boshqaruv Panel')
    compiled = compiled.replace('{% block top_actions %}{% endblock %}', top_actions)
    compiled = compiled.replace('{% block extra_css %}{% endblock %}', extra_css)
    compiled = compiled.replace('{% block extra_js %}{% endblock %}', extra_js)
    compiled = compiled.replace('{% block content %}{% endblock %}', content)
    
    # Handle active class logic dynamically using JS on static navbar
    compiled = re.sub(r'class="nav-item \{% if[^%]+%\}active\{% endif %\}"', 'class="nav-item"', compiled)
    
    # Process relative API routes and Django templates syntax
    compiled = clean_django_tags(compiled)
    
    # Correct relative paths since staff is inside a subfolder
    compiled = compiled.replace('"menu.html"', '"../menu.html"')
    compiled = compiled.replace('API_BASE_URL + "/media/', 'API_BASE_URL + "/media/')
    
    # Write out compiled HTML file
    with open(os.path.join(FRONTEND_STAFF_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(compiled)

# Compile customer views
for page in os.listdir(TEMPLATE_CORE_DIR):
    if page.endswith('.html') and page != 'base.html':
        compile_customer_page(page)

# Compile staff views
for page in os.listdir(TEMPLATE_STAFF_DIR):
    if page.endswith('.html') and page != 'base_staff.html':
        compile_staff_page(page)

print("Frontend compiled successfully!")
