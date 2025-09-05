import pandas as pd
import numpy as np
import os
import requests
import matplotlib
from bs4 import BeautifulSoup
from django.http import JsonResponse
from .forms import CategoryForm
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Contact, Category
from .forms import ContactForm, UserRegisterForm
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
from sklearn.cluster import KMeans
from django.db import models


@login_required
def api_view(request):
    contacts = Contact.objects.filter(user=request.user)
    data = [
        {
            'name': c.name,
            'phone': c.phone,
            'email': c.email,
            'category': c.category.name if c.category else '',
            'priority': c.priority,
        }
        for c in contacts
    ]
    return JsonResponse({'contacts': data})


def home(request):
    return render(request, 'contacts/home.html')

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'contacts/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'contacts/category_form.html', {'form': form})

@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'contacts/category_form.html', {'form': form, 'category': category})

@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted!')
        return redirect('category_list')
    return render(request, 'contacts/category_confirm_delete.html', {'category': category})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'contacts/register.html', {'form': form})

def login_view(request):
    from django import forms
    class LoginForm(forms.Form):
        username = forms.CharField(max_length=150)
        password = forms.CharField(widget=forms.PasswordInput)

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('contact_list')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Please enter both username and password.')
    else:
        form = LoginForm()
    return render(request, 'contacts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def contact_list(request):
    contacts = Contact.objects.filter(user=request.user)
    return render(request, 'contacts/contact_list.html', {'contacts': contacts})

@login_required
def contact_add(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            messages.success(request, 'Contact added!')
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'contacts/contact_form.html', {'form': form})

@login_required
def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact updated!')
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'contacts/contact_form.html', {'form': form, 'contact': contact})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk, user=request.user)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact deleted!')
        return redirect('contact_list')
    return render(request, 'contacts/contact_confirm_delete.html', {'contact': contact})

@login_required
def dashboard(request):
    contacts = Contact.objects.filter(user=request.user)
    total = contacts.count()
    common_category = contacts.values('category__name').annotate(count=models.Count('category')).order_by('-count').first()
    highest_priority = contacts.order_by('-priority').first()
    stats = {
        'total': total,
        'common_category': common_category['category__name'] if common_category else 'N/A',
        'highest_priority': highest_priority.name if highest_priority else 'N/A',
    }
    matplotlib.use('Agg')
    df = pd.DataFrame(list(contacts.values('category__name', 'priority')))
    charts_dir = os.path.join('static', 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    if not df.empty and df['category__name'].notnull().any():
        plt.figure(figsize=(8, 5))
        ax = df['category__name'].value_counts().plot(kind='bar', color='lightgreen')
        plt.title('Contacts by Category')
        plt.xlabel('Category')
        plt.ylabel('Contacts')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'category_chart.png'))
        plt.close()
    if not df.empty and df['priority'].notnull().any():
        plt.figure(figsize=(8, 5))
        contact_names = [c.name for c in contacts]
        priorities = [c.priority for c in contacts]
        ax = plt.bar(contact_names, priorities, color='skyblue')
        plt.title('Contacts by Priority')
        plt.xlabel('Contact Name')
        plt.ylabel('Priority')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'priority_chart.png'))
        plt.close()
    return render(request, 'contacts/dashboard.html', {'stats': stats, 'contacts': contacts})

@login_required
def import_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            Contact.objects.create(
                user=request.user,
                name=row.get('name', ''),
                phone=row.get('phone', ''),
                email=row.get('email', ''),
                address=row.get('address', ''),
                notes=row.get('notes', ''),
                priority=row.get('priority', 0),
            )
        messages.success(request, 'Contacts imported!')
        return redirect('contact_list')
    return render(request, 'contacts/import_csv.html')

@login_required
def export_csv(request):
    contacts = Contact.objects.filter(user=request.user)
    df = pd.DataFrame(list(contacts.values()))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=contacts.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response

@login_required
def ml_prioritize(request):
    contacts = Contact.objects.filter(user=request.user)
    df = pd.DataFrame(list(contacts.values('priority', 'latitude', 'longitude')))
    if not df.empty:
        kmeans = KMeans(n_clusters=3)
        df = df.dropna()
        if not df.empty:
            kmeans.fit(df[['priority', 'latitude', 'longitude']])
            labels = kmeans.labels_
            for i, contact in enumerate(contacts):
                contact.priority = int(labels[i])
                contact.save()
            messages.success(request, 'Contacts prioritized using ML!')
    return redirect('dashboard')
