from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def menu(request, table_id):
    return render(request, 'core/menu.html', {'table_id': table_id})


def item_detail(request, table_id, item_id):
    return render(request, 'core/item_detail.html', {'table_id': table_id, 'item_id': item_id})


def cart(request, table_id):
    return render(request, 'core/cart.html', {'table_id': table_id})


def my_orders(request, table_id):
    return render(request, 'core/my_orders.html', {'table_id': table_id})


def complete_session(request, table_id):
    return render(request, 'core/complete_session.html', {'table_id': table_id})


import traceback
from django.http import HttpResponse

def debug_view(request):
    import sys
    import os
    
    output = []
    output.append(f"Python Version: {sys.version}")
    output.append(f"CWD: {os.getcwd()}")
    
    # Test DB write
    try:
        from core.models import Category
        count = Category.objects.count()
        output.append(f"Categories count: {count}")
        
        from django.contrib.sessions.models import Session
        session_count = Session.objects.count()
        output.append(f"Sessions count: {session_count}")
    except Exception as e:
        output.append(f"Database error: {e}")
        output.append(traceback.format_exc())
        
    # Check permissions
    try:
        from django.conf import settings
        db_path = str(settings.BASE_DIR / 'db.sqlite3')
        if os.path.exists(db_path):
            output.append(f"db.sqlite3 exists at: {db_path}")
            output.append(f"Read permission: {os.access(db_path, os.R_OK)}")
            output.append(f"Write permission: {os.access(db_path, os.W_OK)}")
            
            db_dir = os.path.dirname(db_path)
            output.append(f"Directory: {db_dir}")
            output.append(f"Directory Read permission: {os.access(db_dir, os.R_OK)}")
            output.append(f"Directory Write permission: {os.access(db_dir, os.W_OK)}")
        else:
            output.append(f"db.sqlite3 does NOT exist at: {db_path}")
    except Exception as e:
        output.append(f"Permission check error: {e}")
        
    return HttpResponse("<pre>" + "\n".join(output) + "</pre>")
