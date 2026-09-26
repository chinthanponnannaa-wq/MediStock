from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import UsableItem, Medicine, Vendor, ExpiredItem, CustomerTransaction, VendorTransaction
from .forms import NewMedicineForm, VendorForm, RevenueForm, PasswordChangingForm, UserRegisterForm, AverageForm
from datetime import date
from django.contrib.auth.hashers import check_password


def prec(x):
    x = round(x*100)
    return x/100

# Create your views here.


@login_required(login_url='login')
def home(request):
    total_medicines = Medicine.objects.count()

    usable_items = UsableItem.objects.filter(expiry_date__gte=date.today())
    medicines = Medicine.objects.all()

    low_stock_list = []
    for med in medicines:
        qty = sum(item.quantity for item in usable_items if item.medicine_id == med.id)
        if med.threshold_value > 0 and qty <= med.threshold_value:
            low_stock_list.append({
                'medicine': med,
                'quantity': qty
            })

    low_stock_count = len(low_stock_list)
    expired_count = ExpiredItem.objects.count()
    expired_list = ExpiredItem.objects.all()[:5]

    customer_txs = CustomerTransaction.objects.all()
    total_sales_count = customer_txs.count()
    total_revenue = sum(tx.quantity * tx.medicine.unit_selling for tx in customer_txs) if customer_txs.exists() else 0

    recent_tx_ids = customer_txs.values_list('transaction_id', flat=True).distinct().order_by('-transaction_id')[:5]
    recent_sales = []
    for tx_id in recent_tx_ids:
        tx_items = customer_txs.filter(transaction_id=tx_id)
        first_item = tx_items.first()
        total_qty = sum(item.quantity for item in tx_items)
        total_amount = sum(item.quantity * item.medicine.unit_selling for item in tx_items)
        med_names = list(set(item.medicine.trade_name for item in tx_items if item.medicine))
        med_summary = ", ".join(med_names)
        recent_sales.append({
            'transaction_id': tx_id,
            'name': first_item.name,
            'phone': first_item.phone,
            'medicine_summary': med_summary,
            'total_qty': total_qty,
            'total_amount': total_amount,
            'date': first_item.date,
        })

    context = {
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'low_stock_list': low_stock_list[:5],
        'expired_count': expired_count,
        'expired_list': expired_list,
        'total_sales_count': total_sales_count,
        'total_revenue': total_revenue,
        'recent_sales': recent_sales,
    }
    return render(request, 'home.html', context)


def login_excluded(redirect_to):
    """ This decorator kicks authenticated users out of a view """
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_to)
            return view_method(request, *args, **kwargs)
        return _arguments_wrapper
    return _method_wrapper


@login_excluded('home')
def loginpage(request, backend = None):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect.')
    else:
        list(messages.get_messages(request))
    context = {}
    return render(request, 'loginpage.html', context)


@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def change_password(request):
    currentpassword = request.user.password  # user's current password

    form = PasswordChangingForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            currentpasswordentered = form.cleaned_data.get("old_password")
            password1 = form.cleaned_data.get("new_password1")
            password2 = form.cleaned_data.get("new_password2")

            matchcheck = check_password(currentpasswordentered, currentpassword)
            if matchcheck:
                if password1 == password2:
                    u = request.user
                    u.set_password(password1)
                    u.save()
                    print(password1)
                    messages.success(
                        request, ('Password Was Changed Successfully.'))
                    return render(request, 'home.html', {})
                else:
                    messages.success(
                        request, ('New Passwords do not match.'))
            else:
                messages.success(
                    request, ('Old Password is incorect.'))
        else:
            messages.success(
                request, ('Passwords not Valid.'))
    return render(request, 'change-password.html', {})


@login_required(login_url='login')
def search(request):
    if request.method == "GET":
        usable_item = UsableItem.objects.all()
        search = request.GET.get('search')
        medicine = Medicine.objects.all().filter(
            trade_name__icontains=search) | Medicine.objects.all().filter(generic_name__icontains=search)
        return render(request, 'search.html', {'medicine': medicine, 'usable_item': usable_item})

@login_required(login_url='login')
def listOfMed(request):
    if request.method == "GET":
        usable_item = UsableItem.objects.all()
        medicine = Medicine.objects.all().filter(
            trade_name__icontains='') | Medicine.objects.all().filter(generic_name__icontains='')
        return render(request, 'listOfmed.html', {'medicine': medicine, 'usable_item': usable_item})
        
@login_required(login_url='login')
def newmed(request):
    vendors = Vendor.objects.all
    if request.method == "POST":
        form = NewMedicineForm(request.POST or None)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
        else:
            messages.success(
                request, ('There was an error in your form. Please try again...'))
            return render(request, 'newmed.html', {'vendors': vendors})
        messages.success(request, ('Medicine has been added successfully!'))
        return render(request, 'newmed.html', {'vendors': vendors})
    else:
        return render(request, 'newmed.html', {'vendors': vendors})


@login_required(login_url='login')
def below_threshold(request):
    medicines = Medicine.objects.all()
    usable_items = UsableItem.objects.filter(expiry_date__gte=date.today())
    
    low_stock_items = []
    for med in medicines:
        qty = sum(item.quantity for item in usable_items if item.medicine_id == med.id)
        if med.threshold_value > 0 and qty <= med.threshold_value:
            required_qty = med.threshold_value - qty
            low_stock_items.append({
                'medicine': med,
                'current_stock': qty,
                'threshold': med.threshold_value,
                'qty_required': required_qty,
            })

    return render(request, 'below_threshold.html', {
        'low_stock_items': low_stock_items,
        'date': date.today()
    })

@login_required(login_url='login')
def threshold(request):
    thresholds = Medicine.objects
    new = CustomerTransaction.objects

    quantity = 0

    for a in thresholds.all():
        for b in new.all():
            if(a.trade_name == b.medicine.trade_name):
                quantity += b.quantity
        x = quantity % 7
        quantity /= 7
        if (x > 0):
            quantity += 1
        a.threshold_value = quantity
        a.save()

        quantity = 0

    return render(request, 'threshold.html', {'threshold': thresholds})


@login_required(login_url='login')
def addvendor(request):
    form = VendorForm()
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.success(
                request, ('There was an error in your form. Please try again...'))
            return render(request, 'addvendor.html', {})
        messages.success(request, ('Vendor has been added successfully!'))

    context = {'form': form}
    return render(request, 'addvendor.html', context)


@login_required(login_url='login')
def usable(request):
    usa = UsableItem.objects

    for a in usa.all():
        if(a.expiry_date < date.today()):
            b = ExpiredItem(batch_id=a.batch_id, expiry_date=a.expiry_date,
                            order_date=a.order_date, quantity=a.quantity, medicine=a.medicine)
            b.save()
            a.delete()

    return render(request, 'usable.html', {'usable': usa})


@login_required(login_url='login')
def expired(request):
    usa = UsableItem.objects

    for a in usa.all():
        if(a.expiry_date < date.today()):
            b = ExpiredItem(batch_id=a.batch_id, expiry_date=a.expiry_date,
                            order_date=a.order_date, quantity=a.quantity, medicine=a.medicine)
            b.save()
            a.delete()

    exp = ExpiredItem.objects


    return render(request, 'expired.html', {'expired': exp})


@login_required(login_url='login')
def revenue(request):
    form = RevenueForm()
    if request.method == 'POST':
        form = RevenueForm(request.POST)
        if form.is_valid():
            final_dic = calc(form.cleaned_data)
            return render(request, 'revenue_data.html', final_dic)
        else:
            messages.success(request, ('Please Choose Proper Dates'))


    context = {'form': form}

    return render(request, 'revenue.html', context)



def calc(form):
    start = form['start_date']
    end = form['end_date']
    result = end - start
    days = result.days + 1
    c_val = 0
    v_val = 0
    c_list = []
    v_list = []

    ct = CustomerTransaction.objects
    v = VendorTransaction.objects

    for i in ct.all():
        if(i.date >= start and i.date <= end):
            price = 0
            c_dict = {}
            price = i.quantity * i.medicine.unit_selling
            c_val += price
            c_dict["transaction_id"] = i.transaction_id
            c_dict["name"] = i.name
            c_dict["trade_name"] = i.medicine.trade_name
            c_dict["vendor"] = i.medicine.vendor
            c_dict["date"] = i.date
            c_dict["quantity"] = i.quantity
            c_dict["c_revenue"] = (i.quantity)*(i.medicine.unit_selling)
            c_list.append(c_dict)
        

    for i in v.all():
        if(i.date >= start and i.date <= end):
            price = 0
            v_dict = {}
            price = i.quantity * i.medicine.purchasePrice
            v_val += price
            v_dict["transaction_id"] = i.transaction_id
            v_dict["vendor"] = i.vendor
            v_dict["trade_name"] = i.medicine.trade_name
            v_dict["date"] = i.date
            v_dict["quantity"] = i.quantity
            v_dict["v_cost"] = (i.quantity)*(i.medicine.purchasePrice)

            v_list.append(v_dict)

    name_list = []
    name_dict1 = {}
    name_dict1["cus1"] = "Customer Transaction"
    name_dict1["cus2"] = c_val
    name_dict1["cus3"] = prec(c_val/days)
    name_list.append(name_dict1)

    name_dict2 = {}
    name_dict2["cus1"] = "Vendor Transaction"
    name_dict2["cus2"] = v_val
    name_dict2["cus3"] = prec(v_val/days)
    name_list.append(name_dict2)

    name_dict3 = {}
    name_dict3["cus1"] = "Net Profit"
    name_dict3["cus2"] = c_val - v_val
    name_dict3["cus3"] = prec((c_val - v_val)/days)
    if(c_val>v_val): name_dict3["col"] = 1
    else: name_dict3["col"] = 0
    #name_list.append(name_dict3)


    final_dic = {}
    final_dic['profit'] = name_dict3
    final_dic["vendor"] = v_list
    final_dic["customer"] = c_list
    final_dic["name"] = name_list
    final_dic["start"] = start
    final_dic["end"] = end
    

    return final_dic





@login_required(login_url='login')
def clear_exp(request):
    exp = ExpiredItem.objects
    for a in exp.all():
        a.delete()
    messages.success(request, "ALl the expired items thrown away.")

    return redirect('home')


def register(request):
    if request.method == 'POST':   # Forms get submitted as post requests
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html',{'form':form})


@login_required(login_url='login')
def average(request):
    form = AverageForm()
    if request.method == 'POST':
        form = AverageForm(request.POST)
        if form.is_valid():
            final_dic = calc(form.cleaned_data)
            return render(request, 'average_data.html', final_dic)
        else:
            messages.success(request, ('Please Choose Proper Dates'))


    context = {'form': form}
    return render(request, 'average.html', context)