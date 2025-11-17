from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from users.forms import CustomRegistrationForm, LoginForm, AssignRoleForm, CreateGroupForm
from django.contrib import messages
from django.contrib.auth import  login,logout,get_user_model 
from django.contrib.auth.models import  Group 
from django.db.models import Prefetch
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
User = get_user_model()


def is_admin(user):
    return user.groups.filter(name='admin').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

'''User Register'''


def sign_up(request):
    form = CustomRegistrationForm()
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password1'))
            user.is_active = False
            user.save()
            messages.success(request, 'A Confirmation mail sent. Please check your email')
            return redirect('sign-in')
        else:
            print("Form is not valid")
    return render(request, 'sign_user/sign_up.html', {"form": form})



'''User Login'''

def sign_in(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    return render(request, 'sign_user/login.html', {'form': form})


@login_required
def sign_out(request):

    if request.method == "POST":
        logout(request)
        return redirect('home')
    return redirect('home')


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated. You can now sign in.")
        return redirect('sign-in')
    else:
        return HttpResponse("Invalid activation link", status=400)


@user_passes_test(is_admin, login_url='no_permission')
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch('groups', queryset=Group.objects.all(), to_attr='all_groups')
    ).all()


    for user in users:
        if getattr(user, 'all_groups', None):
            user.groups_name = user.all_groups[0].name
        else:
            user.groups_name = "No Group Assigned"

    if request.method == "POST":
        action = request.POST.get("action")

        # Delete user 
        if action == 'delete_user':
            user_id = request.POST.get('user_id', '').strip()
            if not user_id:
                messages.error(request, "User id missing.")
                return redirect('admin-dashboard')

            try:
                user_id_int = int(user_id)
            except (ValueError, TypeError):
                messages.error(request, "Invalid user id.")
                return redirect('admin-dashboard')

            user_obj = get_object_or_404(User, id=user_id_int)

            # Do not allow deleting superusers
            if getattr(user_obj, 'is_superuser', False):
                messages.error(request, "Cannot delete a superuser account.")
                return redirect('admin-dashboard')

            username = user_obj.username
            user_obj.delete()

            messages.success(request, f"User '{username}' deleted successfully.")
            return redirect('admin-dashboard')

    return render(request, 'admin/dashboard.html', {"users": users})



@user_passes_test(is_admin, login_url='no_permission')
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    form = AssignRoleForm()

    if request.method == 'POST':
        form = AssignRoleForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')  
            user.groups.clear()
            user.groups.add(role)
            messages.success(request, f"User {user.username} assigned to role {role.name}.")
            return redirect('admin-dashboard')

    return render(request, 'admin/assign_role.html', {"form": form, "target_user": user})





@user_passes_test(is_admin, login_url='no_permission')
def create_group(request):
    form = CreateGroupForm()
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f"Group {group.name} has been created successfully")
            return redirect('show-groups')
    return render(request, 'admin/create_group.html', {'form': form})





@user_passes_test(is_admin, login_url='no_permission')
def show_groups(request):
  
    if request.method == "POST":
        action = request.POST.get("action")
        # Delete a group
        if action == "delete_group":
            group_id = request.POST.get("group_id")
            group = get_object_or_404(Group, id=group_id)
            #  do not allow delete'admin'
            if group.name.lower() == "admin":
                messages.error(request, "Cannot delete the 'admin' group.")
            else:
                group.delete()
                messages.success(request, f"Group '{group.name}' has been deleted.")
            return redirect("show-groups")

        # Remove a user from a group
        if action == "remove_user":
            group_id = request.POST.get("group_id")
            user_id = request.POST.get("user_id")
            group = get_object_or_404(Group, id=group_id)
            target = get_object_or_404(User, id=user_id)

 
            if target.is_superuser:
                messages.error(request, "Cannot remove a superuser from this group .")
            else:
                target.groups.remove(group)
                messages.success(
                    request,
                    f"{target.get_full_name() or target.username} removed from group '{group.name}'."
                )
            return redirect("show-groups")

        messages.error(request, "Unknown action.")
        return redirect("show-groups")


    groups = Group.objects.prefetch_related("user_set").all()
    return render(request, "admin/show_groups.html", {"groups": groups})



def no_permission(request):
    return render(request, 'no_permission.html')