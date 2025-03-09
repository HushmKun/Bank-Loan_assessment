from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission

from core.models import User, Application


class Command(BaseCommand):
    def handle(self, **options):
                
        groups = {
            "Provider": [
                "add_application",
                "view_application",
            ],
            "Borrower": [
                "add_application",
                "view_application",
                "view_payment",
            ],
            "Bank Personnel": [
                "add_application",
                "change_application",
                "view_application",
                "change_payment",
                "view_payment",
            ],
        }
        for group_name, perms in groups.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            if _ : 
                self.stdout.write(f">>> Creating group {group_name}")

            for perm in perms: 
                try:
                    group.permissions.add(Permission.objects.get(codename=perm))
                    self.stdout.write(f">>>>> Adding Permission : {perm}")
                except:
                    self.stderr.write(f">>>>> Failed adding Permission : {perm}")

        self.stdout.write("Filling database with users data .......")
        user_list = [
            [
                "admin",
                "admin@admin.com",
                "@dmin123",
                True,
                "Bank Personnel",
            ],
            [
                "borrower_1",
                "customer_1@admin.com",
                "@dmin123",
                True,
                "Borrower",
            ],
            [
                "borrower_2",
                "customer_2@admin.com",
                "@dmin123",
                True,
                "Borrower",
            ],
            [
                "borrower_3",
                "customer_3@admin.com",
                "@dmin123",
                True,
                "Borrower",
            ],
            [
                "provider_1",
                "provider_1@admin.com",
                "@dmin123",
                True,
                "Provider",
            ],
            [
                "provider_2",
                "provider_2@admin.com",
                "@dmin123",
                True,
                "Provider",
            ],
            [
                "provider_3",
                "provider_3@admin.com",
                "@dmin123",
                True,
                "Provider",
            ],
        ]

        users = [
            User(
                username=user[0],
                email=user[1],
                password=make_password(user[2]),
                is_active=True,
                is_superuser= True if user[0] == "admin" else False,
                is_staff=user[3],
            )
            for user in user_list
        ]
        User.objects.bulk_create(users)

        pro = Group.objects.get(name="Provider")
        bor = Group.objects.get(name="Borrower")
        ban = Group.objects.get(name="Bank Personnel")

        for user, item in zip(users, user_list):
            if "Borrower" in item[-1]:
                bor.user_set.add(user)
            elif "Provider" in item[-1]:
                pro.user_set.add(user)
            elif "Bank" in item[-1]:
                ban.user_set.add(user)
        self.stdout.write(
            "============= Finished Database Filling ============="
        )
