import requests
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

import environ

env = environ.Env()
env.read_env()


def get_token():
    response = requests.post('http://52.55.216.140:5690/api/token/',
                             data={'username': env('USERNAME_API'), 'password': env('PASSWORD_API')})
    if response.status_code == 200:
        return response.json().get('access')
    else:
        return None


def make_api_request(method, endpoint, headers=None, data=None):
    if headers is None:
        headers = {}
    token = get_token()
    if token is None:
        return None
    headers['Authorization'] = f'Bearer {token}'
    url = f'http://52.55.216.140:5690/api/{endpoint}/'
    response = requests.request(method, url, headers=headers, data=data)
    return response


def index(request):
    if request.method == 'GET':
        api_response = make_api_request('GET', 'tasks')
        deleted = request.GET.get('deleted')
        if deleted:
            return render(request, 'index.html', {'response': api_response.json(), 'alert': 'Task deleted successfully'})
        else:
            return render(request, 'index.html', {'response': api_response.json()})
    elif request.method == 'POST':
        task_data = {
            'priority': request.POST.get('priority'),
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
        }
        api_response = make_api_request('POST', 'tasks', data=task_data)
        if api_response.status_code == 201:
            api_response = make_api_request('GET', 'tasks')
            return render(request, 'index.html', {'alert': 'Task added successfully', 'response': api_response.json()})
        else:
            api_response = make_api_request('GET', 'tasks')
            return render(request, 'index.html', {'alert': 'Failed to add task', 'response': api_response.json()})
    else:
        return render(request, 'index.html', {'response': 'Invalid request method'})


def delete_task(request, task_id):
    if request.method == 'POST':
        api_response = make_api_request('DELETE', f'tasks/{task_id}')
        if api_response.status_code == 204:
            return HttpResponseRedirect('/?deleted=True')
        else:
            api_response = make_api_request('GET', 'tasks')
            return render(request, 'index.html', {'alert': 'Failed to delete task', 'response': api_response.json()})
    else:
        return render(request, 'index.html', {'response': 'Invalid request method'})


def update_task(request, task_id):
    if request.method == 'POST':
        task_data = {
            'priority': request.POST.get('priority'),
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
        }
        # Send the updated task data to the API using the task_id
        api_response = make_api_request(
            'PUT', f'tasks/{task_id}', data=task_data)
        if api_response.status_code == 200:
            return HttpResponseRedirect('/?updated=True')
        else:
            api_response = make_api_request('GET', 'tasks')
            return render(request, 'index.html', {'alert': 'Failed to update task', 'response': api_response.json()})
    else:
        return render(request, 'index.html', {'response': 'Invalid request method'})
