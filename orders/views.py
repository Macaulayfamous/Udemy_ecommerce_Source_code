from django.shortcuts import render, redirect
from cart.models import CartItem
from .forms import OrderForm
from .models import Order, OrderProduct
import datetime
import json
from django.http import JsonResponse
from .models import Payment
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
# Create your views here.


def payments(request):
    body  = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderId'])
    payment =  Payment(
        user = request.user,
        payment_id = body['transId'],
        payment_method  = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cart_items = CartItem.objects.filter(user=request.user)
    for item  in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id= order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save() 

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    CartItem.objects.filter(user=request.user).delete() 
    mail_subject = "Thank you for your order"
    message = render_to_string('orders/ordered_recive_email.html',{
                'user': request.user,
                'order': order,

                

    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()     

    data = {
        'order_number':order_number,
        'transId': payment.payment_id,
        
    }


    return render(request, 'orders/payments.html')


def place_order(request, total=0, quantity=0,):
    current_user = request.user


    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
         return redirect('order_complete')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price *cart_item.quantity)
        quantity += cart_item.quantity 
    tax = (2 * total)/100
    grand_total =  total + tax    
   


    if request.method == 'POST':
        
        data = Order()

        data.user = current_user

        data.first_name = request.POST.get("first_name","")
        data.last_name = request.POST.get("last_name","")
        data.phone_number = request.POST.get("phone_number","")
        data.email = request.POST.get("email","")
        data.address_line_1 = request.POST.get("address_line_1","")
        data.address_line_2 = request.POST.get("address_line_2","")
        data.country = request.POST.get("country","")
        data.state = request.POST.get("state","")
        data.city = request.POST.get("city","")
        data.order_note = request.POST.get("order_note","")
        data.ip = request.META.get("REMOTE_ADDR")
        data.save()
        data.order_total =grand_total
        data.tax = tax
      
        data.save()
       

        
        """generating order number"""
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,  mt, dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number

        data.save()
        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax':tax,
            'grand_total': grand_total
        }
    
        return render(request , 'orders/payments.html', context)

       
  
            
    else:
        form = OrderForm()
    return redirect('home')


def order_complete(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('created_at')

    context = {
        'orders':orders,
    }
    return render(request, 'orders/order_complete.html',context)
