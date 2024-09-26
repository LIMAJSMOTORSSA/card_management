from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.contrib import messages
from ..models import PassengerUser, SubscriptionPlan, Subscription, Transaction
from django.contrib.auth.decorators import login_required
from ..forms import UserSearchForm, SubscriptionSelectionForm, CheckoutForm
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse





@login_required
def search_users_api(request):
    query = request.GET.get('query', '')
    if len(query) > 2:
        users = PassengerUser.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) | 
            Q(passengerid__icontains=query)
        )[:10]  # Limit to 10 results for performance
        data = [{'id': user.id, 'nom': user.nom, 'prenom': user.prenom, 'passengerid': user.passengerid} for user in users]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def search_usersub(request):
    form = UserSearchForm(request.GET or None)
    users = []
    if form.is_valid():
        search_query = form.cleaned_data['search_query']
        users = PassengerUser.objects.filter(
            Q(nom__icontains=search_query) | 
            Q(prenom__icontains=search_query) | 
            Q(passengerid__iexact=search_query)
        )
    return render(request, 'admin/search_user.html', {'form': form, 'users': users})

@login_required
def choose_payment_frequency(request, user_id):
    user = get_object_or_404(PassengerUser, id=user_id)
    if request.method == 'POST':
        frequency = request.POST.get('frequency')
        return redirect('select_subscriptions', user_id=user_id, frequency=frequency)
    return render(request, 'admin/choose_payment_frequency.html', {'user': user})

@login_required
def select_subscriptions(request, user_id, frequency):
    user = get_object_or_404(PassengerUser, id=user_id)
    available_plans = SubscriptionPlan.objects.filter(
        user_type=user.type_utilisateur,
        duration=frequency
    )
    
    if request.method == 'POST':
        form = SubscriptionSelectionForm(request.POST, available_plans=available_plans)
        if form.is_valid():
            selected_plan_ids = form.cleaned_data['selected_plans']
            selected_plans = SubscriptionPlan.objects.filter(id__in=selected_plan_ids)
            payment_method = form.cleaned_data['payment_method']
            return redirect('checkout', user_id=user_id, plan_ids=','.join(str(plan.id) for plan in selected_plans), payment_method=payment_method)
    else:
        form = SubscriptionSelectionForm(available_plans=available_plans)
    
    return render(request, 'admin/select_subscriptions.html', {'form': form, 'user': user, 'available_plans': available_plans})

@login_required
def checkout(request, user_id, plan_ids, payment_method):
    user = get_object_or_404(PassengerUser, id=user_id)
    selected_plans = SubscriptionPlan.objects.filter(id__in=plan_ids.split(','))
    total_price = sum(plan.price for plan in selected_plans)
    registration_fee = Decimal('1000.00')  # Assuming this is fixed
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            discount = form.cleaned_data['discount']
            total_price_with_discount = total_price - discount
            final_total = total_price_with_discount + registration_fee
            
            # Create subscriptions
            for plan in selected_plans:
                Subscription.objects.create(
                    passenger_user=user,
                    plan=plan,
                    payment_method=payment_method,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date() + timezone.timedelta(days=30 if plan.duration == 'monthly' else 90),
                    is_active=True,
                    payment_received=True
                )
            
            # Create transaction
            Transaction.objects.create(
                passenger_user=user,
                transaction_type='subscription',
                payment_method=payment_method,
                amount=final_total,
                is_successful=True,
                details=f"Subscription for plans: {', '.join(str(plan) for plan in selected_plans)}"
            )
            
            messages.success(request, "Subscriptions created successfully!")
            return redirect('home')
    else:
        form = CheckoutForm()
    
    context = {
        'user': user,
        'selected_plans': selected_plans,
        'total_price': total_price,
        'registration_fee': registration_fee,
        'form': form,
        'payment_method': payment_method
    }
    return render(request, 'admin/checkout.html', context)