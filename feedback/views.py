from django.shortcuts import render


def submit_feedback(request, table_id, order_id=0):
    return render(request, 'feedback/submit.html', {'table_id': table_id, 'order_id': order_id})
