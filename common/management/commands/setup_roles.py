"""
Management command to bootstrap common RBAC groups with correct permissions.

Usage:
    python manage.py setup_roles

This is idempotent — safe to run multiple times. It will:
  - Create groups if they don't exist
  - Assign page-level permissions (Edit, Publish — never Delete)
  - Skip if pages/groups already exist
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, GroupPagePermission


# Define roles and their target page types
# Format: (group_name, description, page_model_label, permission_types)
ROLE_DEFINITIONS = [
    {
        'name': 'Journalists',
        'description': 'Can edit and publish news/announcements',
        'page_type': 'news.NewsIndexPage',
        'permissions': ['add', 'edit', 'publish'],
    },
    {
        'name': 'IT Department',
        'description': 'Can edit faculty and department pages',
        'page_type': 'faculties.FacultyIndexPage',
        'permissions': ['add', 'edit'],
    },
]


class Command(BaseCommand):
    help = 'Bootstrap RBAC groups with page permissions (Edit/Publish only, no Delete)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE ===\n'))

        self.stdout.write(self.style.MIGRATE_HEADING('Setting up RBAC groups...\n'))

        for role_def in ROLE_DEFINITIONS:
            self._setup_role(role_def, dry_run)

        # Grant Wagtail admin access to all custom groups
        self._grant_admin_access(dry_run)

        self.stdout.write(self.style.SUCCESS('\n✅ RBAC setup complete!'))
        self.stdout.write(
            '\nNext steps:\n'
            '  1. Go to Wagtail Admin → Settings → Groups\n'
            '  2. Review the created groups and adjust permissions as needed\n'
            '  3. Create users and assign them to groups\n'
            '  4. You can also create new custom groups directly in the admin!\n'
        )

    def _setup_role(self, role_def, dry_run):
        group_name = role_def['name']
        page_type = role_def['page_type']
        permission_types = role_def['permissions']

        self.stdout.write(f'  📋 Group: "{group_name}"')

        # Create or get the group
        if dry_run:
            group = Group.objects.filter(name=group_name).first()
            if group:
                self.stdout.write(f'     → Group already exists')
            else:
                self.stdout.write(f'     → Would create group')
            return
        
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'     → Created group'))
        else:
            self.stdout.write(f'     → Group already exists')

        # Find the target page
        app_label, model_name = page_type.split('.')
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
            target_pages = Page.objects.filter(content_type=ct).specific()
            
            if not target_pages.exists():
                self.stdout.write(self.style.WARNING(
                    f'     ⚠ No "{model_name}" pages found yet. '
                    f'Create one first, then re-run this command.'
                ))
                return

            for page in target_pages:
                for perm_type in permission_types:
                    perm, perm_created = GroupPagePermission.objects.get_or_create(
                        group=group,
                        page=page,
                        permission_type=perm_type,
                    )
                    if perm_created:
                        self.stdout.write(self.style.SUCCESS(
                            f'     → Granted "{perm_type}" on "{page.title}"'
                        ))
                    else:
                        self.stdout.write(
                            f'     → "{perm_type}" on "{page.title}" already set'
                        )

        except ContentType.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                f'     ✗ Content type "{page_type}" not found. '
                f'Make sure migrations are applied.'
            ))

    def _grant_admin_access(self, dry_run):
        """Grant 'wagtailadmin.access_admin' permission to all custom groups."""
        self.stdout.write(f'\n  🔑 Granting Wagtail admin access...')

        try:
            admin_perm = Permission.objects.get(
                content_type__app_label='wagtailadmin',
                codename='access_admin'
            )
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                '     ✗ Wagtail admin permission not found. '
                'Make sure Wagtail is properly installed.'
            ))
            return

        for role_def in ROLE_DEFINITIONS:
            group_name = role_def['name']
            if dry_run:
                self.stdout.write(f'     → Would grant admin access to "{group_name}"')
                continue

            try:
                group = Group.objects.get(name=group_name)
                if admin_perm not in group.permissions.all():
                    group.permissions.add(admin_perm)
                    self.stdout.write(self.style.SUCCESS(
                        f'     → Granted admin access to "{group_name}"'
                    ))
                else:
                    self.stdout.write(
                        f'     → "{group_name}" already has admin access'
                    )
            except Group.DoesNotExist:
                pass
